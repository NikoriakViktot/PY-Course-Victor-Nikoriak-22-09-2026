"""
taxi_core.py — логіка лабораторії «Таксі: хеш-таблиці зсередини» (урок 17, П3. Хеш-структури).

Застосунок app.py лише викликає ці функції й показує результат. Чотири частини:

    1. TeachingHashTable — навчальна хеш-таблиця, яку видно наскрізь:
       кошики (як у ноутбуці) або відкрита адресація (як справжній dict),
       колізії, коефіцієнт заповнення, розширення таблиці, погані хеш-функції.
    2. list / tuple / set / dict — властивості, хешованість, швидкість `in`.
    3. Пам'ять — sys.getsizeof, глибокий розмір, tracemalloc, вартість int і str.
    4. Справжні дані NYC Taxi + DuckDB — ті самі задачі в Python (dict, set, Counter)
       і в SQL (GROUP BY, COUNT DISTINCT, JOIN); EXPLAIN показує хеш-таблиці всередині бази.

Частини 1–3 — чиста стандартна бібліотека. Частина 4 потребує duckdb
(і geopandas — лише для карти); без файлу NYC вона працює на згенерованих поїздках.
"""
import random
import sys
import time
import tracemalloc
import urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# 1. Навчальна хеш-таблиця
# ---------------------------------------------------------------------------

EMPTY = None


class TeachingHashTable:
    """Хеш-таблиця, у якої видно кожну комірку.

    mode="chaining" — кожна комірка є кошиком-списком (модель з ноутбука);
    mode="probing"  — у комірці один ключ; при колізії йдемо до наступної
                      вільної комірки (відкрита адресація — так влаштовані dict і set у CPython,
                      лише крок там не +1, а «перемішаний»).

    Коли таблиця заповнена більше ніж на max_load, вона подвоюється, і всі ключі
    перераховуються в нові комірки (rehash) — як у справжнього dict.
    """

    def __init__(self, capacity=8, mode="probing", hash_func=hash, max_load=2 / 3, grow=True):
        self.mode = mode
        self.hash_func = hash_func
        self.max_load = max_load
        self.grow = grow
        self.size = 0
        self.resizes = []                     # (стара місткість, нова місткість, при скількох ключах)
        self._make_slots(capacity)

    def _make_slots(self, capacity):
        self.capacity = capacity
        if self.mode == "chaining":
            self.slots = [[] for _ in range(capacity)]
        else:
            self.slots = [EMPTY] * capacity

    def home(self, key):
        """Номер «домашньої» комірки: hash(key) % capacity."""
        return self.hash_func(key) % self.capacity

    @property
    def load(self):
        return self.size / self.capacity

    def keys(self):
        if self.mode == "chaining":
            return [key for bucket in self.slots for key in bucket]
        return [key for key in self.slots if key is not EMPTY]

    def contains(self, key):
        """Повертає (знайдено, порівнянь)."""
        index = self.home(key)
        probes = 0
        if self.mode == "chaining":
            for item in self.slots[index]:
                probes += 1
                if item == key:
                    return True, probes
            return False, probes
        for _ in range(self.capacity):
            item = self.slots[index]
            probes += 1
            if item is EMPTY:
                return False, probes
            if item == key:
                return True, probes
            index = (index + 1) % self.capacity
        return False, probes

    def add(self, key):
        """Додає ключ. Повертає, скільки комірок довелося переглянути."""
        found, probes = self.contains(key)
        if found:
            return probes
        if self.grow and (self.size + 1) / self.capacity > self.max_load:
            self._resize(self.capacity * 2)
        index = self.home(key)
        if self.mode == "chaining":
            self.slots[index].append(key)
            probes = len(self.slots[index])
        else:
            probes = 1
            while self.slots[index] is not EMPTY:
                index = (index + 1) % self.capacity
                probes += 1
            self.slots[index] = key
        self.size += 1
        return probes

    def _resize(self, new_capacity):
        old_keys = self.keys()
        self.resizes.append((self.capacity, new_capacity, self.size))
        self._make_slots(new_capacity)
        self.size = 0
        grow, self.grow = self.grow, False
        for key in old_keys:
            self.add(key)
        self.grow = grow


# Хеш-функції для дослідів. Добра розкидає ключі рівномірно, погані — ні.

def python_hash(key):
    """Вбудований hash(): ключі розкидані рівномірно."""
    return hash(key)


def length_hash(key):
    """Погана: довжина рядка. Усі назви однакової довжини — в одну комірку."""
    return len(str(key))


def first_letter_hash(key):
    """Погана: код першої літери. Усі «Bay…» і «Bro…» зіштовхуються."""
    text = str(key)
    return ord(text[0]) if text else 0


def constant_hash(key):
    """Найгірша: завжди 0. Таблиця вироджується в список — пошук O(n)."""
    return 0


HASH_FUNCS = {
    "hash() — вбудований": python_hash,
    "перша літера": first_letter_hash,
    "довжина рядка": length_hash,
    "завжди 0": constant_hash,
}


def probe_stats(keys, hash_func=python_hash, mode="probing"):
    """Будує таблицю з keys і повертає середню кількість порівнянь на пошук
    наявного й відсутнього ключа, а також саму таблицю."""
    table = TeachingHashTable(mode=mode, hash_func=hash_func)
    for key in keys:
        table.add(key)
    hit = sum(table.contains(key)[1] for key in keys) / max(len(keys), 1)
    misses = [f"__немає__{i}" if isinstance(keys[0], str) else -1 - i for i in range(50)] if keys else []
    miss = sum(table.contains(key)[1] for key in misses) / max(len(misses), 1)
    return {"hit": hit, "miss": miss, "table": table}


def probe_growth(make_keys, sizes, hash_func=python_hash, mode="probing"):
    """Для кожного n: середня кількість порівнянь на успішний пошук."""
    return [(n, probe_stats(make_keys(n), hash_func, mode)["hit"]) for n in sizes]


# ---------------------------------------------------------------------------
# Дані: справжні зони NYC з taxi_zones.dbf (чистий Python, без geopandas)
# ---------------------------------------------------------------------------

ZONES_DBF = HERE / "taxi_zones" / "taxi_zones.dbf"
ZONES_SHP = HERE / "taxi_zones" / "taxi_zones.shp"

FALLBACK_ZONES = [
    (1, "Newark Airport", "EWR"), (4, "Alphabet City", "Manhattan"),
    (132, "JFK Airport", "Queens"), (138, "LaGuardia Airport", "Queens"),
    (161, "Midtown Center", "Manhattan"), (162, "Midtown East", "Manhattan"),
    (230, "Times Sq/Theatre District", "Manhattan"), (236, "Upper East Side North", "Manhattan"),
    (237, "Upper East Side South", "Manhattan"), (79, "East Village", "Manhattan"),
]


def read_dbf(path):
    """Мінімальний читач .dbf (таблиця атрибутів shapefile): список словників."""
    with open(path, "rb") as f:
        header = f.read(32)
        n_records = int.from_bytes(header[4:8], "little")
        header_len = int.from_bytes(header[8:10], "little")
        record_len = int.from_bytes(header[10:12], "little")
        fields = []
        while True:
            descriptor = f.read(32)
            if descriptor[0] == 0x0D:
                break
            name = descriptor[:11].split(b"\0")[0].decode("ascii")
            fields.append((name, chr(descriptor[11]), descriptor[16]))
        f.seek(header_len)
        rows = []
        for _ in range(n_records):
            record = f.read(record_len)
            if record[:1] == b"*":            # видалений запис
                continue
            row, pos = {}, 1
            for name, kind, length in fields:
                raw = record[pos:pos + length].decode("latin-1").strip()
                pos += length
                if kind in "NF":
                    row[name] = (float(raw) if "." in raw else int(raw)) if raw else None
                else:
                    row[name] = raw
            rows.append(row)
    return rows


def load_zone_rows():
    """Рядки таблиці зон: (LocationID, zone, borough). У файлі є повтори ключів."""
    if ZONES_DBF.exists():
        return [(r["LocationID"], r["zone"], r["borough"]) for r in read_dbf(ZONES_DBF)]
    return list(FALLBACK_ZONES)


def zone_lookup(rows):
    """dict «LocationID → (зона, район)». Повторний ключ перезаписує попередній."""
    return {location_id: (zone, borough) for location_id, zone, borough in rows}


def zone_names():
    """Унікальні назви зон NYC — ключі для навчальної таблиці."""
    seen = set()
    names = []
    for _, zone, _ in load_zone_rows():
        if zone not in seen:
            seen.add(zone)
            names.append(zone)
    return names


def make_keys(n, seed=17):
    """n різних ключів-рядків: справжні назви зон, далі — «Зона 264», «Зона 265», …"""
    names = zone_names()
    keys = names[:n] + [f"Зона {i}" for i in range(len(names) + 1, n + 1)]
    random.Random(seed).shuffle(keys)
    return keys[:n]


# ---------------------------------------------------------------------------
# 2. list / tuple / set / dict
# ---------------------------------------------------------------------------

CONTAINER_PROPERTIES = [
    # тип, приклад, впорядкований, змінюваний, повтори, сам hashable, пошук `in`, доступ
    ("list", "[237, 236, 237]", "так", "так", "так", "ні", "O(n)", "за індексом O(1)"),
    ("tuple", "(237, 236, 237)", "так", "ні", "так", "так*", "O(n)", "за індексом O(1)"),
    ("set", "{237, 236}", "ні", "так", "ні", "ні", "O(1)", "немає"),
    ("frozenset", "frozenset({237, 236})", "ні", "ні", "ні", "так", "O(1)", "немає"),
    ("dict", "{237: 'UES South'}", "порядок вставки", "так", "ключі — ні", "ні", "O(1) за ключем", "за ключем O(1)"),
]

BUILDERS = {
    "list": list,
    "tuple": tuple,
    "set": set,
    "dict": dict.fromkeys,
}


def time_per_call(func, *args, budget=0.02):
    """Середній час одного виклику: швидкі функції викликаються багато разів."""
    calls = 1
    while True:
        start = time.perf_counter()
        for _ in range(calls):
            func(*args)
        elapsed = time.perf_counter() - start
        if elapsed >= budget or calls >= 1_000_000:
            return elapsed / calls
        calls *= 4


def make_ids(n, seed=17):
    """n різних номерів поїздок у випадковому порядку."""
    return random.Random(seed).sample(range(10 * n + 10), n)


def contains(container, key):
    return key in container


def membership_race(sizes, seed=17):
    """Для кожного n і кожного типу: час побудови і час одного `in` для відсутнього ключа."""
    rows = []
    for n in sizes:
        ids = make_ids(n, seed)
        for name, build in BUILDERS.items():
            start = time.perf_counter()
            container = build(ids)
            build_s = time.perf_counter() - start
            rows.append({
                "n": n, "type": name, "build": build_s,
                "lookup": time_per_call(contains, container, -1),
            })
    return rows


HASHABILITY_CASES = [
    ("int", "1120"),
    ("float", "12.5"),
    ("str", "'Midtown Center'"),
    ("None", "None"),
    ("tuple з чисел", "(237, 236)"),
    ("frozenset", "frozenset({237, 236})"),
    ("tuple зі списком", "(237, [236])"),
    ("list", "[237, 236]"),
    ("set", "{237, 236}"),
    ("dict", "{237: 'UES South'}"),
]


def hashability_report():
    """Для кожного прикладу: чи можна взяти hash() і яке повідомлення помилки."""
    report = []
    for name, expression in HASHABILITY_CASES:
        value = eval(expression, {"__builtins__": {}, "frozenset": frozenset})
        try:
            result = f"hash = {hash(value)}"
            ok = True
        except TypeError as error:
            result = f"TypeError: {error}"
            ok = False
        report.append({"тип": name, "вираз": expression, "hashable": ok, "результат": result})
    return report


def equal_keys_demo():
    """1, 1.0 і True рівні й мають однаковий hash — тож це ОДИН ключ."""
    demo = {}
    demo[1] = "int"
    demo[1.0] = "float"
    demo[True] = "bool"
    return demo


# ---------------------------------------------------------------------------
# 3. Пам'ять
# ---------------------------------------------------------------------------

def getsizeof_curve(max_n=64):
    """sys.getsizeof контейнера (без елементів) для n = 0…max_n.

    list росте через append — видно запас (over-allocation); set і dict
    стрибають, коли таблиця розширюється.
    """
    rows = []
    grown = []
    for n in range(max_n + 1):
        if n:
            grown.append(n - 1)
        data = list(range(n))
        rows.append({
            "n": n,
            "list": sys.getsizeof(grown),
            "tuple": sys.getsizeof(tuple(data)),
            "set": sys.getsizeof(set(data)),
            "dict": sys.getsizeof(dict.fromkeys(data)),
        })
    return rows


def deep_size(obj, seen=None):
    """Розмір об'єкта разом з усім, на що він посилається. Кожен об'єкт рахується один раз:
    множина seen зберігає id() уже порахованих — та сама хеш-таблиця в дії."""
    if seen is None:
        seen = set()
    if id(obj) in seen:
        return 0
    seen.add(id(obj))
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum(deep_size(k, seen) + deep_size(v, seen) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(deep_size(item, seen) for item in obj)
    return size


def traced_bytes(build, *args):
    """Скільки байтів реально виділила функція build(*args) — через tracemalloc."""
    tracemalloc.start()
    try:
        before = tracemalloc.get_traced_memory()[0]
        result = build(*args)
        after = tracemalloc.get_traced_memory()[0]
    finally:
        tracemalloc.stop()
    del result
    return after - before


def memory_table(n, seed=17):
    """Для n номерів поїздок: розмір контейнера, глибокий розмір, tracemalloc, байт на елемент."""
    ids = [10_000_000 + i for i in make_ids(n, seed)]       # великі int — не з кешу малих чисел
    rows = []
    for name, build in BUILDERS.items():
        container = build(ids)
        shallow = sys.getsizeof(container)
        rows.append({
            "тип": name,
            "контейнер (getsizeof)": shallow,
            "разом з числами (deep_size)": deep_size(container),
            "tracemalloc": traced_bytes(build, ids),
            "байт на елемент (контейнер)": shallow / n,
        })
    return rows


def string_sizes():
    """Скільки важить рядок: латиниця — 1 байт на символ, кирилиця — 2, емодзі — 4."""
    samples = ["", "Midtown", "Мідтаун", "Мідтаун🚕", "Midtown" * 10, "Мідтаун" * 10]
    return [{"рядок": repr(s if len(s) < 25 else s[:20] + "…"), "символів": len(s),
             "getsizeof": sys.getsizeof(s)} for s in samples]


def int_sizes():
    samples = [0, 1, 237, 2 ** 30, 2 ** 62, 2 ** 100]
    return [{"число": f"{x:,}" if x < 2 ** 64 else "2**100", "getsizeof": sys.getsizeof(x)} for x in samples]


def small_int_cache():
    """Python заздалегідь створює числа від -5 до 256 і повторно їх використовує."""
    a, b = int("256"), int("256")
    c, d = int("257"), int("257")
    return {"256 is 256": a is b, "257 is 257": c is d}


# ---------------------------------------------------------------------------
# 4. Справжні дані NYC Taxi + DuckDB
# ---------------------------------------------------------------------------

DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet"
PARQUET = HERE / "data" / "yellow_tripdata_2023-01.parquet"


def parquet_ready():
    return PARQUET.exists() and PARQUET.stat().st_size > 1_000_000


def download_parquet(on_progress=None):
    """Завантажує parquet NYC TLC (~45 МБ) у data/. Спершу у .tmp, потім перейменовує,
    щоб обірване завантаження не залишило «битий» файл."""
    PARQUET.parent.mkdir(exist_ok=True)
    tmp = PARQUET.with_suffix(".tmp")

    def hook(blocks, block_size, total):
        if on_progress and total > 0:
            on_progress(min(1.0, blocks * block_size / total))

    urllib.request.urlretrieve(DATA_URL, tmp, hook)
    tmp.replace(PARQUET)
    return PARQUET


def _sql_path(path):
    return str(path).replace("\\", "/").replace("'", "''")


def connect(use_nyc=None, synthetic_rows=500_000):
    """DuckDB у пам'яті з двома таблицями:

    trips — поїздки (pu_id, do_id, fare, distance): справжній parquet NYC або згенеровані;
    zones — довідник зон з taxi_zones.dbf (location_id, zone, borough), без повторів ключа;
    zones_raw — той самий довідник як є у файлі, з повторами.
    """
    import duckdb

    con = duckdb.connect(":memory:")
    if use_nyc is None:
        use_nyc = parquet_ready()
    if use_nyc:
        con.execute(f"""
            CREATE VIEW trips AS
            SELECT PULocationID AS pu_id, DOLocationID AS do_id,
                   fare_amount AS fare, trip_distance AS distance
            FROM read_parquet('{_sql_path(PARQUET)}')
        """)
    else:
        con.execute("SELECT setseed(0.17)")
        con.execute(f"""
            CREATE TABLE trips AS
            SELECT CAST(1 + floor(263 * pow(random(), 3)) AS INTEGER) AS pu_id,
                   CAST(1 + floor(263 * pow(random(), 3)) AS INTEGER) AS do_id,
                   round(5 + 60 * random(), 2) AS fare,
                   round(0.3 + 15 * random(), 2) AS distance
            FROM range({int(synthetic_rows)})
        """)
    rows = load_zone_rows()
    con.execute("CREATE TABLE zones_raw (location_id INTEGER, zone VARCHAR, borough VARCHAR)")
    con.executemany("INSERT INTO zones_raw VALUES (?, ?, ?)", rows)
    lookup = zone_lookup(rows)
    con.execute("CREATE TABLE zones (location_id INTEGER PRIMARY KEY, zone VARCHAR, borough VARCHAR)")
    con.executemany("INSERT INTO zones VALUES (?, ?, ?)", [(k, z, b) for k, (z, b) in lookup.items()])
    return con


def total_trips(con):
    return con.execute("SELECT count(*) FROM trips").fetchone()[0]


def take_sample(con, n):
    """Таблиця sample з n поїздок (відтворювано) і ті самі рядки як список кортежів Python."""
    con.execute("DROP TABLE IF EXISTS sample")
    con.execute(f"CREATE TABLE sample AS SELECT * FROM trips USING SAMPLE reservoir({int(n)} ROWS) REPEATABLE (17)")
    start = time.perf_counter()
    rows = con.execute("SELECT pu_id, do_id, fare FROM sample").fetchall()
    fetch_s = time.perf_counter() - start
    return rows, fetch_s


def _timed(func, *args):
    start = time.perf_counter()
    result = func(*args)
    return result, time.perf_counter() - start


# Ті самі питання — у Python і в SQL

def py_top_routes(rows, k=10):
    return Counter((pu, do) for pu, do, _ in rows).most_common(k)


SQL_TOP_ROUTES = """
SELECT pu_id, do_id, count(*) AS trips
FROM sample
GROUP BY pu_id, do_id
ORDER BY trips DESC, pu_id, do_id
LIMIT {k}
"""


def py_distinct_zones(rows):
    return len({pu for pu, _, _ in rows} | {do for _, do, _ in rows})


SQL_DISTINCT_ZONES = """
SELECT count(DISTINCT zone_id) FROM (
    SELECT pu_id AS zone_id FROM sample
    UNION ALL
    SELECT do_id FROM sample
)
"""


def py_top_pickup_zones(rows, lookup, k=10):
    unknown = ("Невідома зона", "—")
    return Counter(lookup.get(pu, unknown)[0] for pu, _, _ in rows).most_common(k)


SQL_TOP_PICKUP_ZONES = """
SELECT coalesce(z.zone, 'Невідома зона') AS zone, count(*) AS trips
FROM sample AS s
LEFT JOIN zones AS z ON s.pu_id = z.location_id
GROUP BY 1
ORDER BY trips DESC, zone
LIMIT {k}
"""


def py_avg_fare_by_borough(rows, lookup):
    totals, counts = {}, {}
    for pu, _, fare in rows:
        borough = lookup.get(pu, ("", "Невідомо"))[1]
        totals[borough] = totals.get(borough, 0) + fare
        counts[borough] = counts.get(borough, 0) + 1
    return sorted(((b, round(totals[b] / counts[b], 2)) for b in totals), key=lambda x: -x[1])


SQL_AVG_FARE_BY_BOROUGH = """
SELECT coalesce(z.borough, 'Невідомо') AS borough, round(avg(s.fare), 2) AS avg_fare
FROM sample AS s
LEFT JOIN zones AS z ON s.pu_id = z.location_id
GROUP BY 1
ORDER BY avg_fare DESC
"""


def compare_python_sql(con, rows, k=10):
    """Чотири питання двома способами. Повертає список словників з відповідями й часом."""
    lookup = {zid: (zone, borough) for zid, zone, borough in con.execute("SELECT * FROM zones").fetchall()}
    tasks = [
        ("Топ маршрутів «звідки → куди»", "Counter((pu, do))", lambda: py_top_routes(rows, k),
         SQL_TOP_ROUTES.format(k=k)),
        ("Скільки різних зон", "len(set | set)", lambda: py_distinct_zones(rows), SQL_DISTINCT_ZONES),
        ("Топ зон посадки з назвами", "dict.get + Counter", lambda: py_top_pickup_zones(rows, lookup, k),
         SQL_TOP_PICKUP_ZONES.format(k=k)),
        ("Середній тариф за районом", "два dict-и", lambda: py_avg_fare_by_borough(rows, lookup),
         SQL_AVG_FARE_BY_BOROUGH),
    ]
    results = []
    for (title, py_tool, py_func, sql), normalize in zip(tasks, NORMALIZERS):
        py_answer, py_s = _timed(py_func)
        sql_answer, sql_s = _timed(lambda: con.execute(sql).fetchall())
        results.append({"title": title, "py_tool": py_tool, "py": py_answer, "py_s": py_s,
                        "sql": sql.strip(), "sql_answer": sql_answer, "sql_s": sql_s,
                        "match": _same(normalize(py_answer), [tuple(r) for r in sql_answer])})
    return results


# Відповіді Python → форма рядків SQL, щоб звірити
NORMALIZERS = [
    lambda answer: [(pu, do, count) for (pu, do), count in answer],
    lambda answer: [(answer,)],
    lambda answer: [tuple(item) for item in answer],
    lambda answer: [tuple(item) for item in answer],
]


def _same(a, b):
    """Збіг відповідей. Дробові — з допуском. У топ-k на межі можуть стояти різні рядки
    з однаковим лічильником, тому рядки з найменшим значенням звіряємо лише за значенням."""
    if len(a) != len(b):
        return False

    def key(row):
        return tuple(round(x, 1) if isinstance(x, float) else x for x in row)

    a, b = [key(row) for row in a], [key(row) for row in b]
    if sorted(row[-1] for row in a) != sorted(row[-1] for row in b):
        return False
    cutoff = min((row[-1] for row in a), default=None)
    return {row for row in a if row[-1] != cutoff} == {row for row in b if row[-1] != cutoff}


def full_table_timing(con, k=10):
    """Та сама агрегація SQL на ВСІХ поїздках (для NYC — 3 млн рядків просто з parquet)."""
    sql = SQL_TOP_ROUTES.format(k=k).replace("FROM sample", "FROM trips")
    answer, seconds = _timed(lambda: con.execute(sql).fetchall())
    return answer, seconds


def explain(con, sql):
    """План виконання DuckDB — текстом. Оператори HASH_* — це хеш-таблиці всередині бази."""
    return con.execute("EXPLAIN " + sql).fetchall()[0][1]


def hash_operators(plan_text):
    names = ("HASH_GROUP_BY", "PERFECT_HASH_GROUP_BY", "HASH_JOIN")
    return sorted({name for name in names if name in plan_text})


def duplicate_keys(con):
    """Скільки рядків у zones_raw і скільки унікальних ключів; які ключі повторюються."""
    raw = con.execute("SELECT count(*) FROM zones_raw").fetchone()[0]
    unique = con.execute("SELECT count(DISTINCT location_id) FROM zones_raw").fetchone()[0]
    dupes = con.execute("""
        SELECT location_id, any_value(zone), count(*) FROM zones_raw
        GROUP BY location_id HAVING count(*) > 1 ORDER BY location_id
    """).fetchall()
    return raw, unique, dupes


def join_inflation(con):
    """JOIN з довідником, у якому ключ повторюється, «розмножує» поїздки."""
    clean = con.execute("SELECT count(*) FROM sample s JOIN zones z ON s.pu_id = z.location_id").fetchone()[0]
    raw = con.execute("SELECT count(*) FROM sample s JOIN zones_raw z ON s.pu_id = z.location_id").fetchone()[0]
    missing = con.execute("""
        SELECT s.pu_id, count(*) FROM sample s LEFT JOIN zones z ON s.pu_id = z.location_id
        WHERE z.location_id IS NULL GROUP BY 1 ORDER BY 2 DESC
    """).fetchall()
    return {"clean": clean, "raw": raw, "missing": missing}


def pickups_by_zone(con, table="trips"):
    return con.execute(f"SELECT pu_id, count(*) FROM {table} GROUP BY 1").fetchall()


def row_memory(con, rows):
    """Скільки важить одна поїздка: у Python (кортеж з трьох об'єктів), у numpy-колонках, у parquet."""
    sample = rows[:2000]
    per_row_python = deep_size(sample) / max(len(sample), 1)
    numpy_cols = con.execute("SELECT pu_id, do_id, fare FROM sample LIMIT 2000").fetchnumpy()
    per_row_numpy = sum(col.nbytes for col in numpy_cols.values()) / max(len(sample), 1)
    total = total_trips(con)
    parquet_bytes = PARQUET.stat().st_size if parquet_ready() else None
    return {"python": per_row_python, "numpy": per_row_numpy, "total": total, "parquet": parquet_bytes}


def zones_geojson(simplify=0.0005):
    """GeoJSON зон для карти (потрібен geopandas). Повтори ключа об'єднуються dissolve."""
    import geopandas as gpd

    gdf = gpd.read_file(ZONES_SHP)[["LocationID", "zone", "borough", "geometry"]]
    gdf = gdf.dissolve(by="LocationID", as_index=False, aggfunc="first").to_crs(4326)
    gdf["geometry"] = gdf.geometry.simplify(simplify)
    return gdf.__geo_interface__


def human_time(total_seconds):
    if total_seconds < 0.000001:
        return f"{total_seconds * 1_000_000_000:.0f} нс"
    if total_seconds < 0.001:
        return f"{total_seconds * 1_000_000:.1f} мкс"
    if total_seconds < 1:
        return f"{total_seconds * 1000:.1f} мс"
    return f"{total_seconds:.2f} с"


def human_bytes(n):
    for unit, size in (("ГБ", 1024 ** 3), ("МБ", 1024 ** 2), ("КБ", 1024)):
        if n >= size:
            return f"{n / size:.1f} {unit}"
    return f"{n:.0f} Б"
