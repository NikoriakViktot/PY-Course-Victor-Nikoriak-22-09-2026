"""
stream_core.py — генератори й стан для застосунку «Біржовий потік» (урок 10).

Жодного Dash тут немає: лише потоки даних і невеликий потокобезпечний стан.
app.py імпортує ці функції й малює результат.

Потоки (усі — генератори, дані не зберігаються наперед):
    transaction_stream(companies, seed)   нескінченний потік угод (while True + yield)
    read_ndjson(path)                     лінивий читач файлу: рядок за рядком
    replay_ndjson(path, companies)        нескінченний повтор файлу, угоди різних
                                          компаній перемішані за часом (heapq.merge)
    only_companies(stream, names)         фільтр-генератор

Стан:
    MarketState                           вікно останніх угод на кожну компанію;
                                          next() і запис — під одним замком,
                                          графіки отримують копію через snapshot()
"""
import heapq
import json
import random
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta

COMPANIES = {
    "Нафтогаз":   {"base": 145.0, "vol": 0.018, "color": "#FF6B35"},
    "ПриватБанк": {"base":  89.0, "vol": 0.012, "color": "#4ECDC4"},
    "Розетка":    {"base": 234.0, "vol": 0.022, "color": "#A78BFA"},
    "Укрнафта":   {"base":  67.0, "vol": 0.014, "color": "#34D399"},
    "Київстар":   {"base": 312.0, "vol": 0.009, "color": "#FBBF24"},
}


# ─────────────────────────────────────────────────────────────────────────────
# ДЖЕРЕЛА ДАНИХ
# ─────────────────────────────────────────────────────────────────────────────

def transaction_stream(companies=COMPANIES, seed=10, start=datetime(2024, 1, 2, 9, 0), step_seconds=2):
    """Нескінченний потік угод: while True + yield.

    random.Random(seed) — власний генератор випадкових чисел: той самий seed
    дає ті самі угоди. Час угод лише зростає, номер угоди наскрізний.
    """
    rng = random.Random(seed)
    names = list(companies)
    prices = {name: cfg["base"] for name, cfg in companies.items()}
    moment = start
    trade_id = 1
    while True:
        name = rng.choice(names)
        change = rng.gauss(0, companies[name]["vol"])
        prices[name] = max(prices[name] * (1 + change), 1.0)
        moment += timedelta(seconds=step_seconds)
        yield {
            "id": trade_id,
            "company": name,
            "price": round(prices[name], 2),
            "volume": rng.randint(100, 15_000),
            "change_pct": round(change * 100, 3),
            "time": moment,
        }
        trade_id += 1


def read_ndjson(path):
    """Лінивий читач NDJSON: у пам'яті одночасно лише один рядок файлу."""
    with open(path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                yield json.loads(line)


def only_companies(stream, names):
    """Фільтр-генератор: пропускає угоди лише вибраних компаній."""
    for tx in stream:
        if tx["company"] in names:
            yield tx


def replay_ndjson(path, companies):
    """Нескінченний повтор файлу з угодами.

    Файл з ноутбука зберігає угоди блоками: спершу всі угоди першої компанії,
    потім другої... Щоб компанії чергувались, для кожної відкривається свій
    лінивий фільтр по файлу, а heapq.merge зливає ці потоки за часом —
    без завантаження файлу в пам'ять.
    Номер угоди і час стають наскрізними, зміна ціни рахується від попередньої
    угоди тієї ж компанії. Якщо у файлі немає жодної з компаній — потік
    завершується, а не крутиться вічно.
    """
    trade_id = 1
    moment = datetime(2024, 1, 2, 9, 0)
    last_price = {}
    while True:
        streams = [only_companies(read_ndjson(path), {name}) for name in companies]
        merged = heapq.merge(*streams, key=lambda tx: tx["timestamp"])
        emitted = False
        for tx in merged:
            name = tx["company"]
            price = float(tx["price"])
            previous = last_price.get(name, price)
            last_price[name] = price
            moment += timedelta(seconds=2)
            emitted = True
            yield {
                "id": trade_id,
                "company": name,
                "price": price,
                "volume": int(tx["volume"]),
                "change_pct": round((price - previous) / previous * 100, 3),
                "time": moment,
            }
            trade_id += 1
        if not emitted:
            return


# ─────────────────────────────────────────────────────────────────────────────
# СТАН ЗАСТОСУНКУ
# ─────────────────────────────────────────────────────────────────────────────

class MarketState:
    """Останні угоди по кожній компанії.

    Dash виконує callback-и в різних потоках. Генератор не можна викликати
    з двох потоків одночасно («generator already executing»), а deque не можна
    читати, поки в неї пишуть. Тому:
      * next() і всі записи — лише всередині advance() під self._lock;
      * графіки читають snapshot() — копію, зроблену під тим самим замком.
    """

    def __init__(self, stream, window=80, tape=12):
        self._lock = threading.Lock()
        self._stream = stream
        self._window = window
        self._tape_size = tape
        self._reset()

    def _reset(self):
        self.series = defaultdict(lambda: deque(maxlen=self._window))
        self.tape = deque(maxlen=self._tape_size)
        self.counts = defaultdict(int)
        self.volumes = defaultdict(int)
        self.last = {}
        self.first_price = {}
        self.total = 0
        self.finished = False

    def replace_stream(self, stream):
        """Нове джерело даних: стан починається з нуля."""
        with self._lock:
            self._stream = stream
            self._reset()

    def set_window(self, window):
        """Змінює розмір вікна, зберігаючи останні точки."""
        with self._lock:
            if window == self._window:
                return
            self._window = window
            old = self.series
            self.series = defaultdict(lambda: deque(maxlen=self._window))
            for name, points in old.items():
                self.series[name].extend(points)

    def advance(self, n):
        """Бере з генератора n угод і записує їх. Повертає кількість узятих."""
        taken = 0
        with self._lock:
            for _ in range(n):
                tx = next(self._stream, None)
                if tx is None:
                    self.finished = True
                    break
                name = tx["company"]
                self.series[name].append((tx["time"], tx["price"], tx["volume"]))
                self.tape.append(tx)
                self.counts[name] += 1
                self.volumes[name] += tx["volume"]
                self.last[name] = tx
                self.first_price.setdefault(name, tx["price"])
                self.total += 1
                taken += 1
        return taken

    def snapshot(self):
        """Копія стану для малювання: списки, а не живі deque."""
        with self._lock:
            return {
                "series": {name: list(points) for name, points in self.series.items()},
                "tape": list(self.tape),
                "counts": dict(self.counts),
                "volumes": dict(self.volumes),
                "last": dict(self.last),
                "first_price": dict(self.first_price),
                "total": self.total,
                "finished": self.finished,
            }


def moving_average(values, window):
    """Ковзне середнє: для кожної точки — середнє останніх window значень."""
    result = []
    running = deque()
    total = 0.0
    for value in values:
        running.append(value)
        total += value
        if len(running) > window:
            total -= running.popleft()
        result.append(round(total / len(running), 2))
    return result
