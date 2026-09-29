# ============================================================
#  🍽️  Bistro Analytics — логіка дашборда (без інтерфейсу)
#  Урок 7: Функції — реальний міні-проєкт
# ============================================================
#
#  ЗВ'ЯЗОК З УРОКАМИ:
#
#  ← Урок 5–6: Order(NamedTuple), список чеків, словники,
#              патерни «рахувати, підсумовувати, групувати»
#
#  ← Урок 7: note_lesson_07_functions.ipynb, notes_functions.ipynb
#       чисті функції · predicate · transformer · reducer
#       декомпозиція · pipeline
#
#  PIPELINE:
#
#  seaborn tips
#      │
#      ▼  load_orders()           ← DataFrame → list[Order]  (Transformer)
#  list[Order]
#      │
#      ▼  apply_filters()         ← Predicates (фейсконтроль)
#  list[Order]  (відфільтрований)
#      │
#      ▼  enrich_all()            ← Transformer (збагачення кожного чека)
#  list[RichOrder]
#      │
#      ├─► calc_kpis()            ← Reducer  (KPI)
#      ├─► group_by_day()         ← Reducer  (виручка по днях)
#      ├─► group_by_time()        ← Reducer  (обід vs вечеря)
#      ├─► group_by_size()        ← Reducer  (розмір столу)
#      ├─► group_by_sex()         ← Reducer  (стать клієнтів)
#      └─► top_by_tip_pct()       ← Reducer  (топ чеки)
#
#  Жодна функція тут нічого не друкує і не малює:
#  інтерфейс (app.py) лише викликає run_pipeline() і показує результат.
# ============================================================

from collections import defaultdict
from typing import NamedTuple


# ─────────────────────────────────────────────────────────────────────────────
#  БЛОК 1: СТРУКТУРА ДАНИХ
# ─────────────────────────────────────────────────────────────────────────────
class Order(NamedTuple):
    """Один чек ресторану — той самий NamedTuple, що в уроках 5–7."""
    total_bill: float
    tip:        float
    sex:        str
    smoker:     str
    day:        str
    time:       str
    size:       int


class RichOrder(NamedTuple):
    """Збагачений чек — Order + обчислені поля. Його повертає enrich_order()."""
    total_bill:      float
    tip:             float
    sex:             str
    smoker:          str
    day:             str
    time:            str
    size:            int
    tip_pct:         float   # ← нове поле: % чайових
    bill_per_person: float   # ← нове поле: $ на людину
    day_ua:          str     # ← нове поле: день українською
    time_ua:         str     # ← нове поле: зміна українською


DAY_UA  = {"Thur": "Четвер", "Fri": "П'ятниця", "Sat": "Субота", "Sun": "Неділя"}
TIME_UA = {"Lunch": "Обід", "Dinner": "Вечеря"}
SEX_UA = {"Male": "Чоловіки", "Female": "Жінки"}
SMOKER_UA = {"No": "Некурці", "Yes": "Курці"}


# ─────────────────────────────────────────────────────────────────────────────
#  БЛОК 2: ЗАВАНТАЖЕННЯ ДАНИХ
#  DataFrame → list[Order]  (Transformer)
# ─────────────────────────────────────────────────────────────────────────────
def orders_from_rows(rows) -> list[Order]:
    """Transformer: будь-які рядки з потрібними ключами → list[Order]."""
    return [
        Order(
            total_bill = float(row["total_bill"]),
            tip        = float(row["tip"]),
            sex        = str(row["sex"]),
            smoker     = str(row["smoker"]),
            day        = str(row["day"]),
            time       = str(row["time"]),
            size       = int(row["size"]),
        )
        for row in rows
    ]


def load_orders() -> list[Order]:
    """Завантажує набір seaborn tips (244 чеки) і перетворює рядки на Order."""
    import seaborn as sns   # імпорт тут: тести pipeline.py працюють і без seaborn

    tips_df = sns.load_dataset("tips")
    return orders_from_rows(row for _, row in tips_df.iterrows())


# ─────────────────────────────────────────────────────────────────────────────
#  БЛОК 3: ПРЕДИКАТИ (Predicates) — чиста функція → True / False
# ─────────────────────────────────────────────────────────────────────────────
def pred_day(order: Order, days: list[str]) -> bool:
    """Предикат: чи входить день чека до вибраних днів."""
    return order.day in days


def pred_time(order: Order, times: list[str]) -> bool:
    """Предикат: обід / вечеря / обидва."""
    return order.time in times


def pred_smoker(order: Order, smoker: list[str]) -> bool:
    """Предикат: курці / некурці / всі."""
    return order.smoker in smoker


def pred_size(order: Order, lo: int, hi: int) -> bool:
    """Предикат: розмір столу в діапазоні [lo, hi]."""
    return lo <= order.size <= hi


def pred_bill(order: Order, lo: float, hi: float) -> bool:
    """Предикат: сума рахунку в діапазоні [lo, hi]."""
    return lo <= order.total_bill <= hi


def pred_sex(order: Order, sexes: list[str]) -> bool:
    """Предикат: чи входить стать клієнта до вибраних."""
    return order.sex in sexes


def apply_filters(
    orders:     list[Order],
    days:       list[str],
    times:      list[str],
    smoker:     list[str],
    size_range: tuple[int, int],
    bill_range: tuple[float, float],
    sexes:      list[str],
) -> list[Order]:
    """
    Комбінує всі предикати через AND — залишає тільки потрібні чеки.
    Патерн: [x for x in data if predicate(x)]. Вхідний список не змінюється.
    """
    lo_s, hi_s = size_range
    lo_b, hi_b = bill_range
    return [
        o for o in orders
        if pred_day(o, days)
        and pred_time(o, times)
        and pred_smoker(o, smoker)
        and pred_size(o, lo_s, hi_s)
        and pred_bill(o, lo_b, hi_b)
        and pred_sex(o, sexes)
    ]


# ─────────────────────────────────────────────────────────────────────────────
#  БЛОК 4: ТРАНСФОРМЕРИ (Transformers) — len(вхід) == len(вихід)
# ─────────────────────────────────────────────────────────────────────────────
def enrich_order(o: Order) -> RichOrder:
    """Transformer: Order → RichOrder. Додає обчислені поля, оригінал не змінюється."""
    return RichOrder(
        total_bill      = o.total_bill,
        tip             = o.tip,
        sex             = o.sex,
        smoker          = o.smoker,
        day             = o.day,
        time            = o.time,
        size            = o.size,
        tip_pct         = round((o.tip / o.total_bill) * 100, 1),
        bill_per_person = round(o.total_bill / o.size, 2),
        day_ua          = DAY_UA.get(o.day, o.day),
        time_ua         = TIME_UA.get(o.time, o.time),
    )


def enrich_all(orders: list[Order]) -> list[RichOrder]:
    """Застосовує enrich_order до кожного чека."""
    return [enrich_order(o) for o in orders]


# ─────────────────────────────────────────────────────────────────────────────
#  БЛОК 5: РЕДЬЮСЕРИ (Reducers) — багато елементів → одне значення / агрегат
# ─────────────────────────────────────────────────────────────────────────────
def calc_kpis(orders: list[RichOrder]) -> dict:
    """Reducer: ключові показники через sum() і len()."""
    if not orders:
        return {"revenue": 0, "tips": 0, "avg_bill": 0,
                "avg_tip_pct": 0, "count": 0, "avg_size": 0}
    bills = [o.total_bill for o in orders]
    tips  = [o.tip        for o in orders]
    sizes = [o.size       for o in orders]
    pcts  = [o.tip_pct    for o in orders]
    return {
        "revenue":     round(sum(bills), 2),
        "tips":        round(sum(tips), 2),
        "avg_bill":    round(sum(bills) / len(bills), 2),
        "avg_tip_pct": round(sum(pcts)  / len(pcts),  1),
        "count":       len(orders),
        "avg_size":    round(sum(sizes) / len(sizes), 1),
    }


def group_by_day(orders: list[RichOrder]) -> list[dict]:
    """Reducer: виручка, чайові й кількість чеків по днях (від найбільшої виручки)."""
    rev  = defaultdict(float)
    tips = defaultdict(float)
    cnt  = defaultdict(int)
    for o in orders:
        rev[o.day]  += o.total_bill
        tips[o.day] += o.tip
        cnt[o.day]  += 1
    return sorted([
        {"day": d, "day_ua": DAY_UA.get(d, d),
         "revenue":  round(rev[d], 2),
         "tips":     round(tips[d], 2),
         "orders":   cnt[d],
         "avg_bill": round(rev[d] / cnt[d], 2)}
        for d in rev
    ], key=lambda x: x["revenue"], reverse=True)


def group_by_time(orders: list[RichOrder]) -> list[dict]:
    """Reducer: середній % чайових і середній чек для обіду й вечері."""
    tip_pcts = defaultdict(list)
    bills    = defaultdict(list)
    for o in orders:
        tip_pcts[o.time].append(o.tip_pct)
        bills[o.time].append(o.total_bill)
    result = []
    for t in tip_pcts:
        p = tip_pcts[t]
        b = bills[t]
        result.append({
            "time":        t,
            "time_ua":     TIME_UA.get(t, t),
            "avg_tip_pct": round(sum(p) / len(p), 1),
            "avg_bill":    round(sum(b) / len(b), 2),
            "orders":      len(p),
        })
    return sorted(result, key=lambda x: x["avg_tip_pct"], reverse=True)


def group_by_size(orders: list[RichOrder]) -> list[dict]:
    """Reducer: виручка і середній % чайових за розміром столу."""
    rev  = defaultdict(float)
    pcts = defaultdict(list)
    for o in orders:
        rev[o.size] += o.total_bill
        pcts[o.size].append(o.tip_pct)
    return sorted([
        {"size":        s,
         "size_label":  f"{s} {'особа' if s == 1 else 'особи' if s <= 4 else 'осіб'}",
         "revenue":     round(rev[s], 2),
         "avg_tip_pct": round(sum(pcts[s]) / len(pcts[s]), 1),
         "orders":      len(pcts[s])}
        for s in rev
    ], key=lambda x: x["size"])


def group_by_sex(orders: list[RichOrder]) -> list[dict]:
    """Reducer: виручка і середній % чайових за статтю клієнта."""
    rev  = defaultdict(float)
    pcts = defaultdict(list)
    for o in orders:
        rev[o.sex] += o.total_bill
        pcts[o.sex].append(o.tip_pct)
    return [
        {"sex":         s,
         "sex_ua":      SEX_UA.get(s, s),
         "revenue":     round(rev[s], 2),
         "avg_tip_pct": round(sum(pcts[s]) / len(pcts[s]), 1),
         "orders":      len(pcts[s])}
        for s in rev
    ]


def top_by_tip_pct(orders: list[RichOrder], n: int = 5) -> list[RichOrder]:
    """Reducer: топ-N чеків за % чайових (sorted() → перші n)."""
    return sorted(orders, key=lambda o: o.tip_pct, reverse=True)[:n]


# ─────────────────────────────────────────────────────────────────────────────
#  БЛОК 6: ПОВНИЙ PIPELINE — маленькі чисті функції в одному оркестраторі
# ─────────────────────────────────────────────────────────────────────────────
def run_pipeline(
    orders:     list[Order],
    days:       list[str],
    times:      list[str],
    smoker:     list[str],
    size_range: tuple[int, int],
    bill_range: tuple[float, float],
    sexes:      list[str],
) -> dict:
    """
    Головний pipeline:
      1. Filter   (predicates)  → list[Order]
      2. Enrich   (transformer) → list[RichOrder]
      3. Reduce   (reducers)    → аналітика
    Отримує чеки параметром і повертає новий словник — чиста функція.
    """
    filtered = apply_filters(orders, days, times, smoker, size_range, bill_range, sexes)
    enriched = enrich_all(filtered)
    return {
        "count":    len(enriched),
        "enriched": enriched,
        "kpis":     calc_kpis(enriched),
        "by_day":   group_by_day(enriched),
        "by_time":  group_by_time(enriched),
        "by_size":  group_by_size(enriched),
        "by_sex":   group_by_sex(enriched),
        "top_tips": top_by_tip_pct(enriched, n=5),
    }
