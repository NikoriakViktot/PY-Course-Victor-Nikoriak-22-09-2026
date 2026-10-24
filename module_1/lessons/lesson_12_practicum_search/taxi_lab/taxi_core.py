"""
taxi_core.py — логіка лабораторії «Таксі: чи треба перебирати все?» (урок 12, П2. Пошук).

Чистий Python без сторонніх бібліотек. Застосунок app.py лише викликає ці функції
й показує результат. Пошукові функції — ті самі, що в ноутбуці уроку
note_lesson_12_search.ipynb (тест перевіряє, що код збігається).

Кожне рішення повертає пару (відповідь, кроки):
    кроки — скільки базових дій виконав алгоритм (порівнянь або додавань).
    Кроки не залежать від швидкості комп'ютера, тому їх можна порівнювати чесно.

Чотири місії диспетчера, для кожної — повільне і швидке рішення:
    1. time    — чи була поїздка в певний момент (лінійний / бінарний пошук);
    2. voucher — дві поїздки на рівну суму ваучера (перебір пар / два вказівники);
    3. peak    — найзавантаженіший відрізок часу (перерахунок / ковзне вікно);
    4. suggest — автодоповнення адреси (перевірити всі / бінарний пошук + сусіди).

Плюс готові інструменти: стандартна бібліотека Python (`in`, `bisect`, `itertools`)
і сторонні бібліотеки (`numpy`, `pandas`, `sortedcontainers`). Сторонні необов'язкові:
якщо бібліотеки немає, її рядок просто не показується.
"""
import math
import random
import time
from bisect import bisect_left
from itertools import accumulate, islice

try:
    import numpy as np
except ImportError:          # pragma: no cover
    np = None
try:
    import pandas as pd
except ImportError:          # pragma: no cover
    pd = None
try:
    from sortedcontainers import SortedList
except ImportError:          # pragma: no cover
    SortedList = None

# ---------------------------------------------------------------------------
# Пошукові функції — копії з ноутбука уроку 12
# ---------------------------------------------------------------------------

def linear_search(items, target):
    steps = 0
    for i in range(len(items)):
        steps += 1
        if items[i] == target:
            return i, steps
    return -1, steps


def binary_search(items, target):
    low, high = 0, len(items) - 1
    steps = 0
    while low <= high:
        mid = (low + high) // 2
        steps += 1
        if items[mid] == target:
            return mid, steps
        if items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1, steps


def pair_with_sum_brute(items, target):
    steps = 0
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            steps += 1
            if items[i] + items[j] == target:
                return (items[i], items[j]), steps
    return None, steps


def pair_with_sum(items, target):
    left, right = 0, len(items) - 1
    steps = 0
    while left < right:
        steps += 1
        total = items[left] + items[right]
        if total == target:
            return (items[left], items[right]), steps
        if total < target:
            left += 1
        else:
            right -= 1
    return None, steps


def busiest_window_naive(counts, k):
    """Рахує суму кожного вікна заново: k додавань на вікно, O(n·k)."""
    steps = k
    best_start, best_sum = 0, sum(counts[0:k])
    for start in range(1, len(counts) - k + 1):
        steps += k
        window_sum = sum(counts[start:start + k])
        if window_sum > best_sum:
            best_start, best_sum = start, window_sum
    return (best_start, best_sum), steps


def busiest_window(counts, k):
    """Ковзне вікно: одне значення випадає зліва, одне додається справа — O(n)."""
    steps = k
    window_sum = sum(counts[0:k])
    best_start, best_sum = 0, window_sum
    for end in range(k, len(counts)):
        steps += 1
        window_sum += counts[end] - counts[end - k]
        if window_sum > best_sum:
            best_start, best_sum = end - k + 1, window_sum
    return (best_start, best_sum), steps


def first_at_or_after(items, target):
    """Свій bisect_left: індекс першого елемента >= target. Повертає (індекс, кроки)."""
    steps = 0
    low, high = 0, len(items)
    while low < high:
        mid = (low + high) // 2
        steps += 1
        if items[mid] < target:
            low = mid + 1
        else:
            high = mid
    return low, steps


def suggest_slow(streets, prefix, limit=3):
    """Перевіряє кожну вулицю зі startswith і бере перші limit: O(n)."""
    steps = 0
    matches = []
    for street in streets:
        steps += 1
        if street.startswith(prefix):
            matches.append(street)
    return matches[:limit], steps


def suggest(streets, prefix, limit=3):
    """Бінарний пошук початку + кілька сусідів праворуч: O(log n + limit)."""
    i, steps = first_at_or_after(streets, prefix)
    result = []
    while i < len(streets) and streets[i].startswith(prefix) and len(result) < limit:
        steps += 1
        result.append(streets[i])
        i += 1
    return result, steps


# ---------------------------------------------------------------------------
# Дані: генеруються з фіксованим seed — однакові на кожному запуску
# ---------------------------------------------------------------------------

PER_HOUR = [3, 1, 0, 0, 1, 4, 12, 30, 41, 25, 18, 20,
            22, 19, 17, 21, 33, 45, 52, 38, 24, 15, 9, 6]

STREET_STEMS = [
    "Антоновича", "Басейна", "Богдана Хмельницького", "Велика Васильківська",
    "Верхній Вал", "Володимирська", "Гончара", "Дегтярівська", "Жилянська",
    "Ярославів Вал", "Костянтинівська", "Лаврська", "Мечникова", "Михайлівська",
    "Набережно-Хрещатицька", "Саксаганського", "Січових Стрільців", "Хорива",
    "Хрещатик", "Шота Руставелі",
]


def make_start_times(n, seed=12):
    """n відсортованих моментів початку поїздок (секунди від початку місяця), усі парні й різні."""
    rng = random.Random(seed)
    return sorted(2 * x for x in rng.sample(range(5 * n + 10), n))


def make_fares(n, seed=12):
    """n відсортованих сум поїздок, кратних 10 грн."""
    rng = random.Random(seed)
    return sorted(10 * rng.randrange(8, 61) for _ in range(n))


def make_per_minute(n, seed=12):
    """Завантаження за добу, поділену на n проміжків: денний профіль + шум."""
    rng = random.Random(seed)
    return [PER_HOUR[i * 24 // n] + rng.randrange(5) for i in range(n)]


def make_streets(n, seed=12):
    """n відсортованих адрес «Вулиця, будинок»."""
    rng = random.Random(seed)
    return sorted(f"{rng.choice(STREET_STEMS)}, {i + 1}" for i in range(n))


# Вхідні дані розміру n для кожної місії — найгірший випадок для повільного рішення

def input_time(n):
    times = make_start_times(n)
    return times, times[-1] + 1          # такої поїздки немає: усі моменти парні


def input_voucher(n):
    return make_fares(n), 505            # суми кратні 10, тож пари на 505 грн немає


def input_peak(n):
    return make_per_minute(n), max(1, n // 4)   # найзавантаженіша чверть доби


def input_suggest(n):
    return make_streets(n), "Хр"


# ---------------------------------------------------------------------------
# Готові інструменти: Python і бібліотеки
#
# Кожен інструмент = prepare (один раз: перетворити дані, напр. список → масив numpy)
# + run (сам запит). Час підготовки і час запиту міряються окремо.
# run повертає «нормалізовану» відповідь, яку можна звірити з нашими функціями.
# ---------------------------------------------------------------------------

def as_is(*args):
    return args


# --- 1. Чи є момент у журналі ---

def time_in(times, target):
    return target in times


def time_bisect(times, target):
    i = bisect_left(times, target)
    return i < len(times) and times[i] == target


def to_numpy(items, *rest):
    return (np.asarray(items), *rest)


def time_numpy(times, target):
    i = np.searchsorted(times, target)
    return bool(i < len(times) and times[i] == target)


def to_sorted_list(items, *rest):
    return (SortedList(items), *rest)


def time_sorted_list(times, target):
    return target in times                # SortedList: in працює за O(log n)


# --- 2. Пара на суму ваучера ---

def voucher_bisect(fares, target):
    """Для кожної поїздки шукаємо «доповнення» бінарним пошуком: O(n log n)."""
    for i, fare in enumerate(fares):
        j = bisect_left(fares, target - fare, i + 1)
        if j < len(fares) and fares[j] == target - fare:
            return True
    return False


def voucher_numpy(fares, target):
    """Те саме, але всі доповнення шукаються одним викликом searchsorted."""
    complements = target - fares
    j = np.searchsorted(fares, complements, side="right") - 1
    j = np.clip(j, 0, len(fares) - 1)
    return bool(np.any((fares[j] == complements) & (j > np.arange(len(fares)))))


# --- 3. Пікове вікно ---

def peak_accumulate(counts, k):
    """Префіксні суми з itertools.accumulate: сума вікна = різниця двох префіксів."""
    prefix = [0, *accumulate(counts)]
    start = max(range(len(counts) - k + 1), key=lambda s: prefix[s + k] - prefix[s])
    return start, prefix[start + k] - prefix[start]


def peak_numpy(counts, k):
    prefix = np.concatenate(([0], np.cumsum(counts)))
    sums = prefix[k:] - prefix[:-k]
    start = int(np.argmax(sums))           # argmax бере перший максимум
    return start, int(sums[start])


def to_series(counts, *rest):
    return (pd.Series(counts), *rest)


def peak_pandas(counts, k):
    sums = counts.rolling(k).sum()          # сума кожного вікна, що закінчується на індексі
    end = int(sums.idxmax())
    return end - k + 1, int(sums[end])


# --- 4. Автодоповнення ---

def suggest_bisect(streets, prefix, limit=3):
    i = bisect_left(streets, prefix)
    return list(islice((s for s in streets[i:i + limit] if s.startswith(prefix)), limit))


def suggest_sorted_list(streets, prefix, limit=3):
    # irange віддає елементи між двома межами; "￿" — «більше за будь-яку літеру»
    return list(islice(streets.irange(prefix, prefix + "￿"), limit))


def suggest_numpy(streets, prefix, limit=3):
    i = int(np.searchsorted(streets, prefix))
    return [str(s) for s in streets[i:i + limit] if str(s).startswith(prefix)]


def suggest_pandas(streets, prefix, limit=3):
    """Векторизовано, на C, — але все одно перевіряє КОЖЕН рядок: O(n)."""
    return streets[streets.str.startswith(prefix)].head(limit).tolist()


def _available_tools(rows):
    """rows: (назва, бібліотека, Big O, run, prepare, модуль або None для стандартної бібліотеки)."""
    tools = []
    for name, lib, o, run, prepare, module in rows:
        if lib != "Python" and module is None:
            continue                      # бібліотеку не встановлено
        tools.append({"name": name, "lib": lib, "o": o, "run": run, "prepare": prepare})
    return tools


READY_TOOLS = {
    "time": _available_tools([
        ("x in list", "Python", "O(n)", time_in, as_is, None),
        ("bisect.bisect_left", "Python", "O(log n)", time_bisect, as_is, None),
        ("numpy.searchsorted", "numpy", "O(log n)", time_numpy, to_numpy, np),
        ("SortedList: x in", "sortedcontainers", "O(log n)", time_sorted_list, to_sorted_list, SortedList),
    ]),
    "voucher": _available_tools([
        ("bisect для кожної поїздки", "Python", "O(n log n)", voucher_bisect, as_is, None),
        ("numpy.searchsorted разом", "numpy", "O(n log n)", voucher_numpy, to_numpy, np),
    ]),
    "peak": _available_tools([
        ("itertools.accumulate", "Python", "O(n)", peak_accumulate, as_is, None),
        ("numpy.cumsum", "numpy", "O(n)", peak_numpy, to_numpy, np),
        ("pandas rolling(k).sum()", "pandas", "O(n)", peak_pandas, to_series, pd),
    ]),
    "suggest": _available_tools([
        ("bisect + startswith", "Python", "O(log n)", suggest_bisect, as_is, None),
        ("SortedList.irange", "sortedcontainers", "O(log n)", suggest_sorted_list, to_sorted_list, SortedList),
        ("numpy.searchsorted", "numpy", "O(log n)", suggest_numpy, to_numpy, np),
        ("pandas str.startswith", "pandas", "O(n)", suggest_pandas, to_series, pd),
    ]),
}


def measure_tools(key, args):
    """Для кожного готового інструмента: відповідь, час підготовки й час одного запиту."""
    rows = []
    for tool in READY_TOOLS[key]:
        start = time.perf_counter()
        prepared = tool["prepare"](*args)
        prepare_s = time.perf_counter() - start
        rows.append({
            "name": tool["name"], "lib": tool["lib"], "o": tool["o"],
            "answer": tool["run"](*prepared),
            "prepare": prepare_s,
            "seconds": time_per_call(tool["run"], *prepared),
        })
    return rows


# ---------------------------------------------------------------------------
# Місії
# ---------------------------------------------------------------------------

GROWTH = {
    "O(n)": lambda n: n,
    "O(n²)": lambda n: n * n,
    "O(n·k)": lambda n: n * n,           # k = n/4 росте разом з n
    "O(log n)": lambda n: math.log2(max(n, 2)),
}

EXPERIMENTS = {
    "time": {
        "title": "Чи була поїздка в цей момент?",
        "question": "Клієнт каже, що їхав у конкретну секунду. Чи є така поїздка в журналі?",
        "property": 1,
        "slow": linear_search, "fast": binary_search,
        "slow_o": "O(n)", "fast_o": "O(log n)",
        "make_input": input_time,
        "normalize": lambda answer: answer != -1,
        "sizes": [8_000, 80_000, 800_000],
    },
    "voucher": {
        "title": "Ваучер на рівну суму",
        "question": "Які дві поїздки разом дають рівно суму ваучера?",
        "property": 2,
        "slow": pair_with_sum_brute, "fast": pair_with_sum,
        "slow_o": "O(n²)", "fast_o": "O(n)",
        "make_input": input_voucher,
        "normalize": lambda answer: answer is not None,
        "sizes": [800, 1600, 3200, 6400],
    },
    "peak": {
        "title": "Пікові години",
        "question": "Яка чверть доби поспіль найзавантаженіша — коли виводити більше водіїв?",
        "property": 3,
        "slow": busiest_window_naive, "fast": busiest_window,
        "slow_o": "O(n·k)", "fast_o": "O(n)",
        "make_input": input_peak,
        "normalize": lambda answer: answer,
        "sizes": [800, 1600, 3200, 6400],
    },
    "suggest": {
        "title": "Автодоповнення адреси",
        "question": "Пасажир набрав «Хр». Які три адреси підказати?",
        "property": 1,
        "slow": suggest_slow, "fast": suggest,
        "slow_o": "O(n)", "fast_o": "O(log n)",
        "make_input": input_suggest,
        "normalize": lambda answer: answer,
        "sizes": [8_000, 80_000, 800_000],
    },
}


# ---------------------------------------------------------------------------
# Інструменти вимірювання
# ---------------------------------------------------------------------------

def count_steps(func, make_input, sizes):
    """Для кожного n: (n, кроки). Дані для кожного n генеруються наново."""
    rows = []
    for n in sizes:
        _, steps = func(*make_input(n))
        rows.append((n, steps))
    return rows


def doubling_table(func, make_input, sizes):
    """Рядки (n, кроки, у скільки разів більше, ніж для попереднього n).

    Якщо n щоразу подвоюється: ≈1 — O(log n), ≈2 — O(n), ≈4 — O(n²).
    """
    rows = []
    previous = None
    for n, steps in count_steps(func, make_input, sizes):
        ratio = None if previous is None else round(steps / previous, 2)
        rows.append((n, steps, ratio))
        previous = steps
    return rows


def print_doubling_table(rows):
    print(f"{'n':>8} {'кроки':>14} {'× до попереднього':>18}")
    for n, steps, ratio in rows:
        shown = "—" if ratio is None else f"×{ratio}"
        print(f"{n:>8} {steps:>14,} {shown:>18}")


def seconds(func, *args, repeat=3):
    """Найкращий із кількох замірів часу, у секундах."""
    best = None
    for _ in range(repeat):
        start = time.perf_counter()
        func(*args)
        elapsed = time.perf_counter() - start
        if best is None or elapsed < best:
            best = elapsed
    return best


def time_per_call(func, *args, budget=0.03):
    """Середній час одного виклику. Швидкі функції викликаються багато разів,
    поки не набереться budget секунд, — інакше мікросекунди тонуть у шумі."""
    calls = 1
    while True:
        start = time.perf_counter()
        for _ in range(calls):
            func(*args)
        elapsed = time.perf_counter() - start
        if elapsed >= budget or calls >= 1_000_000:
            return elapsed / calls
        calls *= 4


def human_time(total_seconds):
    """Секунди → зрозумілий рядок: мкс, мс, с, хв, год, дні, роки."""
    units = [
        (365 * 24 * 3600, "р."), (24 * 3600, "дн."), (3600, "год"),
        (60, "хв"), (1, "с"),
    ]
    if total_seconds < 0.001:
        return f"{total_seconds * 1_000_000:.1f} мкс"
    if total_seconds < 1:
        return f"{total_seconds * 1000:.1f} мс"
    for size, name in units:
        if total_seconds >= size:
            return f"{total_seconds / size:.1f} {name}"
    return f"{total_seconds:.1f} с"


# ---------------------------------------------------------------------------
# Гонка пошуків: чотири способи на одному відсортованому списку
# ---------------------------------------------------------------------------

def builtin_in(items, target):
    """Оператор in для списку — той самий лінійний пошук, але написаний на C."""
    return target in items


def bisect_contains(items, target):
    """Бінарний пошук з модуля bisect (теж написаний на C)."""
    i = bisect_left(items, target)
    return i < len(items) and items[i] == target


RACERS = [
    {"name": "Свій лінійний пошук", "lib": "наш код", "o": "O(n)", "func": linear_search,
     "prepare": as_is, "counts_steps": True},
    {"name": "x in list", "lib": "Python", "o": "O(n)", "func": builtin_in,
     "prepare": as_is, "counts_steps": False},
    {"name": "Свій бінарний пошук", "lib": "наш код", "o": "O(log n)", "func": binary_search,
     "prepare": as_is, "counts_steps": True},
    {"name": "bisect.bisect_left", "lib": "Python", "o": "O(log n)", "func": bisect_contains,
     "prepare": as_is, "counts_steps": False},
]
if np is not None:
    RACERS.append({"name": "numpy.searchsorted", "lib": "numpy", "o": "O(log n)", "func": time_numpy,
                   "prepare": to_numpy, "counts_steps": False})
if SortedList is not None:
    RACERS.append({"name": "SortedList: x in", "lib": "sortedcontainers", "o": "O(log n)",
                   "func": time_sorted_list, "prepare": to_sorted_list, "counts_steps": False})

POSITIONS = {
    "на початку": lambda data: data[0],
    "посередині": lambda data: data[len(data) // 2],
    "в кінці": lambda data: data[-1],
    "немає в журналі": lambda data: data[-1] + 1,
}


def race_data(n):
    """Відсортований журнал: моменти 0, 2, 4, … — n записів."""
    return list(range(0, 2 * n, 2))


def race(data, target):
    """Для кожного способу: знайдено?, кроки (якщо рахуються), час підготовки і одного пошуку."""
    rows = []
    for racer in RACERS:
        start = time.perf_counter()
        prepared = racer["prepare"](data, target)
        prepare_s = time.perf_counter() - start
        answer = racer["func"](*prepared)
        if racer["counts_steps"]:
            index, steps = answer
            found = index != -1
        else:
            found, steps = answer, None
        rows.append({
            "name": racer["name"], "lib": racer["lib"], "o": racer["o"],
            "found": found, "steps": steps, "prepare": prepare_s,
            "seconds": time_per_call(racer["func"], *prepared),
        })
    return rows


def batch_race(n, queries=10_000, seed=12):
    """Багато запитів одразу: цикл з bisect проти одного виклику numpy.searchsorted.

    Повертає словник {назва: секунди на всі запити}. Тут numpy розкривається:
    один виклик обробляє весь масив запитів на C, без циклу Python.
    """
    rng = random.Random(seed)
    data = race_data(n)
    targets = [rng.randrange(2 * n) for _ in range(queries)]

    def loop_bisect():
        return [bisect_contains(data, t) for t in targets]

    result = {"цикл Python + bisect": seconds(loop_bisect)}
    if np is not None:
        array, target_array = np.asarray(data), np.asarray(targets)

        def vector_numpy():
            i = np.searchsorted(array, target_array)
            i = np.clip(i, 0, len(array) - 1)
            return array[i] == target_array

        assert list(vector_numpy()) == loop_bisect()
        result["numpy.searchsorted(масив запитів)"] = seconds(vector_numpy)
    return result


def unsorted_trap(n=15, seed=12):
    """Перемішаний журнал і момент, який у ньому Є, але бінарний пошук його не знаходить.

    Повертає (дані, ціль, результат лінійного, результат бінарного).
    """
    rng = random.Random(seed)
    data = list(range(0, 2 * n, 2))
    rng.shuffle(data)
    for target in data:
        if binary_search(data, target)[0] == -1:
            return data, target, linear_search(data, target), binary_search(data, target)
    return data, data[0], linear_search(data, data[0]), binary_search(data, data[0])


def sort_payoff(n, seed=12):
    """Чи варто сортувати? Час sorted() один раз, одного `in` і одного bisect на n записах.

    Повертає словник із часами й кількістю пошуків, після якої сортування окупається.
    """
    rng = random.Random(seed)
    data = race_data(n)
    shuffled = data[:]
    rng.shuffle(shuffled)
    target = data[-1] + 1                 # найгірший випадок для лінійного пошуку
    sort_s = seconds(sorted, shuffled, repeat=3)
    linear_s = time_per_call(builtin_in, shuffled, target)
    binary_s = time_per_call(bisect_contains, data, target)
    gain = linear_s - binary_s
    breakeven = math.inf if gain <= 0 else math.ceil(sort_s / gain)
    return {"sort": sort_s, "linear": linear_s, "binary": binary_s, "breakeven": breakeven}
