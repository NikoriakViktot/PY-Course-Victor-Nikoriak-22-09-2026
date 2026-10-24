"""Перевірки taxi_core.py: python test_taxi_core.py (або pytest).

Частина з DuckDB пропускається, якщо duckdb не встановлено.
"""
import sys

from taxi_core import (
    HASH_FUNCS, TeachingHashTable, constant_hash, deep_size, equal_keys_demo, getsizeof_curve,
    hashability_report, human_bytes, human_time, load_zone_rows, make_ids, make_keys, memory_table,
    probe_growth, probe_stats, small_int_cache, zone_lookup, zone_names,
)


def test_chaining_matches_notebook_buckets():
    """Модель з ноутбука: 8 кошиків, 1128 потрапляє в кошик до 1120."""
    table = TeachingHashTable(capacity=8, mode="chaining", grow=False)
    for key in [1120, 425, 930, 612, 845, 1128]:
        table.add(key)
    assert table.slots[0] == [1120, 1128]
    assert table.contains(1128) == (True, 2)
    assert table.contains(845) == (True, 1)
    assert table.contains(999)[0] is False


def test_probing_moves_colliding_key_to_next_slot():
    table = TeachingHashTable(capacity=8, mode="probing", grow=False)
    for key in [8, 16, 3]:            # 8 і 16 — обидва в комірку 0
        table.add(key)
    assert table.slots[0] == 8 and table.slots[1] == 16 and table.slots[3] == 3
    assert table.contains(16) == (True, 2)
    assert table.contains(24) == (False, 3)   # 0 → 1 → 2 (порожня)


def test_table_grows_and_keeps_all_keys():
    for mode in ("probing", "chaining"):
        table = TeachingHashTable(mode=mode)
        keys = list(range(0, 1000, 7))
        for key in keys:
            table.add(key)
            assert table.load <= 2 / 3
        assert table.size == len(keys) == len(set(table.keys()))
        assert all(table.contains(key)[0] for key in keys)
        assert [old * 2 for old, _, _ in table.resizes] == [new for _, new, _ in table.resizes]
        table.add(7)                                  # повтор не додається
        assert table.size == len(keys)


def test_good_hash_is_constant_bad_hash_is_linear():
    sizes = [32, 64, 128, 256]
    good = [p for _, p in probe_growth(make_keys, sizes)]
    bad = [p for _, p in probe_growth(make_keys, sizes, constant_hash)]
    assert all(p < 2.5 for p in good), good
    assert bad == [(n + 1) / 2 for n in sizes], bad
    for func in HASH_FUNCS.values():
        assert probe_stats(make_keys(100), func)["table"].size == 100


def test_zones():
    rows = load_zone_rows()
    lookup = zone_lookup(rows)
    names = zone_names()
    assert len(names) == len(set(names))
    if len(rows) == 263:                              # справжній taxi_zones.dbf
        assert len(lookup) == 260
        assert lookup[132][0] == "JFK Airport"
    keys = make_keys(300)
    assert len(keys) == len(set(keys)) == 300
    assert make_keys(50) == make_keys(50)


def test_types_and_hashability():
    report = {r["тип"]: r["hashable"] for r in hashability_report()}
    assert report["tuple з чисел"] and report["frozenset"] and report["str"]
    assert not report["list"] and not report["dict"] and not report["set"] and not report["tuple зі списком"]
    assert equal_keys_demo() == {1: "bool"}
    assert small_int_cache() == {"256 is 256": True, "257 is 257": False}


def test_memory():
    curve = getsizeof_curve(20)
    assert all(b["tuple"] - a["tuple"] == 8 for a, b in zip(curve, curve[1:]))
    rows = {r["тип"]: r for r in memory_table(10_000)}
    assert rows["set"]["контейнер (getsizeof)"] > 3 * rows["list"]["контейнер (getsizeof)"]
    assert rows["list"]["tracemalloc"] == rows["list"]["контейнер (getsizeof)"]
    shared = [10 ** 9 + 1] * 3
    assert deep_size(shared) == sys.getsizeof(shared) + sys.getsizeof(shared[0])
    assert len(make_ids(500)) == len(set(make_ids(500))) == 500


def test_human_units():
    assert human_time(3e-8) == "30 нс"
    assert human_time(0.0123) == "12.3 мс"
    assert human_bytes(2048) == "2.0 КБ"


def test_python_and_sql_agree():
    try:
        import duckdb  # noqa: F401
    except ImportError:
        print("  (duckdb не встановлено — пропущено)")
        return
    from taxi_core import (
        compare_python_sql, connect, duplicate_keys, explain, hash_operators, join_inflation, take_sample,
        SQL_TOP_PICKUP_ZONES,
    )
    for use_nyc in (False, True):
        try:
            con = connect(use_nyc=use_nyc, synthetic_rows=50_000)
        except Exception:
            continue                                   # немає parquet — пропускаємо справжні дані
        rows, _ = take_sample(con, 20_000)
        assert len(rows) == 20_000
        results = compare_python_sql(con, rows)
        assert all(r["match"] for r in results), [r["title"] for r in results if not r["match"]]
        assert "HASH_JOIN" in hash_operators(explain(con, SQL_TOP_PICKUP_ZONES.format(k=5)))
        raw, unique, _ = duplicate_keys(con)
        assert raw >= unique
        inflation = join_inflation(con)
        assert inflation["raw"] >= inflation["clean"]


if __name__ == "__main__":
    for name, func in list(globals().items()):
        if name.startswith("test_"):
            func()
            print("OK", name)
