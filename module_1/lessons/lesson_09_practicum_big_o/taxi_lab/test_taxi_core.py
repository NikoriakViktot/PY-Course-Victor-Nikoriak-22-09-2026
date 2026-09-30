"""Перевірки taxi_core.py: python test_taxi_core.py (або pytest)."""
import inspect
import json
from pathlib import Path

import taxi_core
from taxi_core import (
    EXPERIMENTS, Trip, doubling_table, has_duplicate_ids_fast, has_duplicate_ids_slow,
    human_time, make_shifts, make_trips, nearest_repeat_fast, nearest_repeat_slow,
)


def test_data_is_reproducible():
    assert make_trips(50) == make_trips(50)
    assert make_trips(50, seed=1) != make_trips(50, seed=2)
    trips = make_trips(200)
    assert all(isinstance(t, Trip) for t in trips)
    assert len({t.trip_id for t in trips}) == 200


def test_shifts():
    monday, tuesday = make_shifts(100)
    assert len(monday) == len(set(monday)) == 100
    assert len(tuesday) == len(set(tuesday)) == 100
    assert len(set(monday) & set(tuesday)) == 20


def test_slow_and_fast_give_same_answers():
    for key, exp in EXPERIMENTS.items():
        for n in (1, 2, 7, 50, 300):
            args = exp["make_input"](n)
            slow, _ = exp["slow"](*args)
            fast, _ = exp["fast"](*args)
            assert slow == fast, (key, n)


def test_small_cases_by_hand():
    assert has_duplicate_ids_slow([5, 1, 5]) == (True, 2)
    assert has_duplicate_ids_fast([5, 1, 5]) == (True, 3)
    assert has_duplicate_ids_slow([1, 2, 3, 4]) == (False, 6)
    assert has_duplicate_ids_fast([]) == (False, 0)
    assert nearest_repeat_slow(["a", "b", "a", "a"])[0] == 1
    assert nearest_repeat_fast(["a", "b", "c"])[0] == -1


def test_doubling_ratios():
    sizes = [200, 400, 800]
    for key, exp in EXPERIMENTS.items():
        slow = [r[2] for r in doubling_table(exp["slow"], exp["make_input"], sizes)][1:]
        fast = [r[2] for r in doubling_table(exp["fast"], exp["make_input"], sizes)][1:]
        assert all(3.5 < r < 4.5 for r in slow), (key, slow)
        assert all(r == 2.0 for r in fast), (key, fast)


def test_human_time():
    assert human_time(0.0123) == "12.3 мс"
    assert human_time(90) == "1.5 хв"
    assert human_time(3 * 24 * 3600) == "3.0 дн."


def test_lab_notebook_uses_the_same_code():
    """Ноутбук містить копії функцій (для Colab) — вони мають збігатися з taxi_core.py."""
    notebook = Path(__file__).parent.parent / "lab_lesson_08_taxi_big_o.ipynb"
    cells = json.loads(notebook.read_text(encoding="utf-8"))["cells"]
    code = "\n".join("".join(c["source"]) for c in cells if c["cell_type"] == "code")
    for name, obj in vars(taxi_core).items():
        if inspect.isfunction(obj) and obj.__module__ == "taxi_core" and not name.startswith("input_"):
            assert inspect.getsource(obj).strip() in code, name


if __name__ == "__main__":
    for name, func in list(globals().items()):
        if name.startswith("test_"):
            func()
            print("OK", name)
