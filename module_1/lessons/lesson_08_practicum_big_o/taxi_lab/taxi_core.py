"""
taxi_core.py — логіка лабораторії «Таксі: Big O на практиці» (урок 8, П1).

Чистий Python без сторонніх бібліотек. Ці самі функції є в ноутбуці
lab_lesson_08_taxi_big_o.ipynb (щоб він працював у Colab без файлів поруч),
а застосунок app.py лише викликає їх і показує результат.

Кожне рішення повертає пару (відповідь, кроки):
    кроки — скільки базових дій виконав алгоритм (порівнянь або
    перевірок у множині/словнику). Кроки не залежать від швидкості
    комп'ютера, тому їх можна порівнювати чесно.

Чотири задачі диспетчера, для кожної — повільне і швидке рішення:
    1. has_duplicate_ids   — чи є два однакові номери поїздки;
    2. common_drivers      — водії, що працювали в обидві зміни;
    3. unique_clients      — клієнти без повторів у порядку першої поїздки;
    4. nearest_repeat      — найкоротша відстань між двома поїздками одного клієнта.
"""
import random
import time
from typing import NamedTuple

ZONES = [
    "Поділ", "Оболонь", "Печерськ", "Лук'янівка", "Троєщина", "Позняки",
    "Виноградар", "Теремки", "Святошин", "Голосіїв", "Дарниця", "Нивки",
]


class Trip(NamedTuple):
    trip_id: int
    driver: str
    client: str
    zone: str
    fare: float


# ---------------------------------------------------------------------------
# Дані: генеруються з фіксованим seed — однакові на кожному запуску
# ---------------------------------------------------------------------------

def make_trips(n, seed=8):
    """Список з n поїздок. Номери поїздок унікальні, клієнти повторюються."""
    rng = random.Random(seed)
    trip_ids = rng.sample(range(100_000, 100_000 + 10 * n), n)
    drivers = max(1, n // 10)
    clients = max(1, n // 2)
    return [
        Trip(
            trip_id=trip_ids[i],
            driver=f"D-{rng.randrange(drivers):05d}",
            client=f"C-{rng.randrange(clients):06d}",
            zone=rng.choice(ZONES),
            fare=round(rng.uniform(80, 600), 2),
        )
        for i in range(n)
    ]


def make_shifts(n, seed=8):
    """Два списки по n різних водіїв (понеділок, вівторок); спільних — приблизно 20 %."""
    rng = random.Random(seed)
    pool = [f"D-{i:05d}" for i in range(2 * n)]
    monday = rng.sample(pool, n)
    common = rng.sample(monday, n // 5)
    monday_set = set(monday)
    others = [d for d in pool if d not in monday_set]
    tuesday = common + rng.sample(others, n - len(common))
    rng.shuffle(tuesday)
    return monday, tuesday


# ---------------------------------------------------------------------------
# 1. Чи є два однакові номери поїздки?
# ---------------------------------------------------------------------------

def has_duplicate_ids_slow(ids):
    """Порівнює кожну пару номерів: O(n²)."""
    steps = 0
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            steps += 1
            if ids[i] == ids[j]:
                return True, steps
    return False, steps


def has_duplicate_ids_fast(ids):
    """Один прохід і множина вже побачених номерів: O(n)."""
    steps = 0
    seen = set()
    for trip_id in ids:
        steps += 1
        if trip_id in seen:
            return True, steps
        seen.add(trip_id)
    return False, steps


# ---------------------------------------------------------------------------
# 2. Які водії працювали і в понеділок, і у вівторок?
# ---------------------------------------------------------------------------

def common_drivers_slow(monday, tuesday):
    """`driver in tuesday` для списку — прихований цикл: O(n·m).

    Цикл по tuesday нижче робить те саме, що `in` для списку,
    лише з лічильником, щоб прихована робота стала видимою.
    """
    steps = 0
    result = []
    for driver in monday:
        for other in tuesday:
            steps += 1
            if other == driver:
                result.append(driver)
                break
    return result, steps


def common_drivers_fast(monday, tuesday):
    """Множина вівторка будується один раз, далі кожна перевірка — один крок: O(n + m)."""
    steps = 0
    tuesday_set = set()
    for driver in tuesday:
        steps += 1
        tuesday_set.add(driver)
    result = []
    for driver in monday:
        steps += 1
        if driver in tuesday_set:
            result.append(driver)
    return result, steps


# ---------------------------------------------------------------------------
# 3. Клієнти без повторів у порядку першої поїздки (для розсилки)
# ---------------------------------------------------------------------------

def unique_clients_slow(clients):
    """`client not in result` для списку, що росте: O(n²)."""
    steps = 0
    result = []
    for client in clients:
        found = False
        for known in result:
            steps += 1
            if known == client:
                found = True
                break
        if not found:
            result.append(client)
    return result, steps


def unique_clients_fast(clients):
    """Допоміжна множина для перевірки і список для порядку: O(n)."""
    steps = 0
    result = []
    seen = set()
    for client in clients:
        steps += 1
        if client not in seen:
            seen.add(client)
            result.append(client)
    return result, steps


# ---------------------------------------------------------------------------
# 4. Найшвидше повернення клієнта: найменша відстань між двома його поїздками
# ---------------------------------------------------------------------------

def nearest_repeat_slow(clients):
    """Перебирає всі пари поїздок: O(n²). Повертає -1, якщо повторів немає."""
    steps = 0
    best = -1
    for i in range(len(clients)):
        for j in range(i + 1, len(clients)):
            steps += 1
            if clients[i] == clients[j] and (best == -1 or j - i < best):
                best = j - i
    return best, steps


def nearest_repeat_fast(clients):
    """Словник «клієнт → остання поїздка»: один прохід, O(n)."""
    steps = 0
    best = -1
    last_seen = {}
    for i, client in enumerate(clients):
        steps += 1
        if client in last_seen and (best == -1 or i - last_seen[client] < best):
            best = i - last_seen[client]
        last_seen[client] = i
    return best, steps


# ---------------------------------------------------------------------------
# Експерименти: вхідні дані розміру n для кожної задачі
# ---------------------------------------------------------------------------

def input_ids(n):
    return ([t.trip_id for t in make_trips(n)],)


def input_shifts(n):
    return make_shifts(n)


def input_clients(n):
    return ([t.client for t in make_trips(n)],)


EXPERIMENTS = {
    "ids": {
        "title": "Повторний номер поїздки",
        "question": "Чи є в журналі дві поїздки з однаковим номером?",
        "slow": has_duplicate_ids_slow,
        "fast": has_duplicate_ids_fast,
        "make_input": input_ids,
    },
    "drivers": {
        "title": "Водії двох змін",
        "question": "Які водії працювали і в понеділок, і у вівторок?",
        "slow": common_drivers_slow,
        "fast": common_drivers_fast,
        "make_input": input_shifts,
    },
    "clients": {
        "title": "Клієнти для розсилки",
        "question": "Список клієнтів без повторів у порядку їхньої першої поїздки.",
        "slow": unique_clients_slow,
        "fast": unique_clients_fast,
        "make_input": input_clients,
    },
    "repeat": {
        "title": "Найшвидше повернення",
        "question": "Через скільки поїздок найшвидше повернувся хтось із клієнтів?",
        "slow": nearest_repeat_slow,
        "fast": nearest_repeat_fast,
        "make_input": input_clients,
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

    Якщо n щоразу подвоюється, відношення ≈ 2 означає O(n), ≈ 4 — O(n²).
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


def human_time(total_seconds):
    """Секунди → зрозумілий рядок: мс, с, хв, год, дні, роки."""
    units = [
        (365 * 24 * 3600, "р."), (24 * 3600, "дн."), (3600, "год"),
        (60, "хв"), (1, "с"),
    ]
    if total_seconds < 1:
        return f"{total_seconds * 1000:.1f} мс"
    for size, name in units:
        if total_seconds >= size:
            return f"{total_seconds / size:.1f} {name}"
    return f"{total_seconds:.1f} с"
