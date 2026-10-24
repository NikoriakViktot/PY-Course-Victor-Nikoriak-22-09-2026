"""Перевірки taxi_core.py: python test_taxi_core.py (або pytest)."""
import inspect
import json
from bisect import bisect_left
from pathlib import Path

import taxi_core
from taxi_core import (
    EXPERIMENTS, PER_HOUR, READY_TOOLS, binary_search, busiest_window, busiest_window_naive,
    doubling_table, first_at_or_after, human_time, make_fares, make_start_times, make_streets,
    measure_tools, pair_with_sum, pair_with_sum_brute, race, race_data, suggest, suggest_slow,
    unsorted_trap,
)

STARTS = [425, 510, 612, 700, 845, 930, 1035, 1120, 1210, 1290, 1375]
FARES = [120, 150, 180, 230, 270, 320, 410]
STREETS = sorted(["Богдана Хмельницького", "Велика Васильківська", "Верхній Вал",
                  "Володимирська", "Хрещатик", "Хорива", "Шота Руставелі"])


def test_data_is_reproducible_and_sorted():
    for make in (make_start_times, make_fares, make_streets):
        assert make(200) == make(200)
        assert make(200) == sorted(make(200))
        assert make(200, seed=1) != make(200, seed=2)
    times = make_start_times(500)
    assert len(set(times)) == 500 and all(t % 2 == 0 for t in times)


def test_examples_from_lesson_notebook():
    assert binary_search(STARTS, 1120) == (7, 4)
    assert binary_search(STARTS, 1000)[0] == -1
    assert pair_with_sum(FARES, 500) == ((180, 320), 4)
    assert pair_with_sum(FARES, 10_000) == (None, 6)
    assert pair_with_sum([], 500) == (None, 0)
    assert busiest_window(PER_HOUR, 3)[0] == (17, 135)
    assert suggest(STREETS, "В")[0] == ["Велика Васильківська", "Верхній Вал", "Володимирська"]
    assert suggest(STREETS, "Х")[0] == ["Хорива", "Хрещатик"]
    assert suggest(STREETS, "Я")[0] == []
    assert suggest(STREETS, "В", limit=1)[0] == ["Велика Васильківська"]


def test_slow_fast_and_ready_tools_give_same_answers():
    for key, exp in EXPERIMENTS.items():
        for n in (1, 2, 7, 50, 300):
            args = exp["make_input"](n)
            slow = exp["normalize"](exp["slow"](*args)[0])
            fast = exp["normalize"](exp["fast"](*args)[0])
            assert slow == fast, (key, n)
            for tool in READY_TOOLS[key]:
                assert tool["run"](*tool["prepare"](*args)) == slow, (key, n, tool["name"])


def test_tools_on_cases_with_an_answer():
    """Найгірші випадки в місіях не мають відповіді — перевіримо й випадки, де вона є."""
    def run_all(key, args):
        return {t["name"]: t["run"](*t["prepare"](*args)) for t in READY_TOOLS[key]}

    assert set(run_all("time", (STARTS, 1120)).values()) == {True}
    assert set(run_all("voucher", (FARES, 500)).values()) == {True}
    assert set(run_all("voucher", ([250, 300], 500)).values()) == {False}    # одна поїздка двічі не рахується
    assert set(run_all("voucher", ([250, 250], 500)).values()) == {True}
    for k in range(1, 25):
        expected = busiest_window_naive(PER_HOUR, k)[0]
        assert busiest_window(PER_HOUR, k)[0] == expected
        assert all(answer == expected for answer in run_all("peak", (PER_HOUR, k)).values()), k
    for prefix in ("В", "Ве", "Х", "Я", ""):
        expected = suggest_slow(STREETS, prefix)[0]
        assert suggest(STREETS, prefix)[0] == expected
        assert all(answer == expected for answer in run_all("suggest", (STREETS, prefix)).values()), prefix


def test_doubling_ratios():
    sizes = [400, 800, 1600]
    expected = {"O(n)": (1.9, 2.1), "O(n²)": (3.5, 4.5), "O(n·k)": (3.5, 4.5), "O(log n)": (1.0, 1.2)}
    for key, exp in EXPERIMENTS.items():
        for side in ("slow", "fast"):
            low, high = expected[exp[f"{side}_o"]]
            ratios = [r[2] for r in doubling_table(exp[side], exp["make_input"], sizes)][1:]
            assert all(low <= r <= high for r in ratios), (key, side, ratios)


def test_binary_search_adds_one_step_per_doubling():
    for n, steps in ((1000, 9), (2000, 10), (4000, 11), (1_000_000, 19)):   # як у ноутбуці уроку
        assert binary_search(race_data(n), -1)[1] == steps


def test_first_at_or_after_matches_bisect():
    assert first_at_or_after([], 5)[0] == 0
    for t in range(400, 1401):
        index, steps = first_at_or_after(STARTS, t)
        assert index == bisect_left(STARTS, t), t
        assert steps <= len(STARTS).bit_length() + 1


def test_race_and_measurements():
    data = race_data(1000)
    rows = race(data, data[500])
    assert all(r["found"] for r in rows)
    assert all(not r["found"] for r in race(data, -1))
    for key, exp in EXPERIMENTS.items():
        for row in measure_tools(key, exp["make_input"](50)):
            assert row["seconds"] > 0


def test_unsorted_trap_misses_existing_value():
    data, target, linear_result, binary_result = unsorted_trap()
    assert target in data
    assert linear_result[0] == data.index(target)
    assert binary_result[0] == -1


def test_human_time():
    assert human_time(0.0000123) == "12.3 мкс"
    assert human_time(0.0123) == "12.3 мс"
    assert human_time(90) == "1.5 хв"
    assert human_time(3 * 24 * 3600) == "3.0 дн."


def test_same_code_as_lesson_notebook():
    """Пошукові функції застосунку — ті самі, що в ноутбуці уроку 12."""
    notebook = Path(__file__).parent.parent / "note_lesson_12_search.ipynb"
    cells = json.loads(notebook.read_text(encoding="utf-8"))["cells"]
    code = "\n".join("".join(c["source"]) for c in cells if c["cell_type"] == "code")
    for func in (taxi_core.linear_search, binary_search, pair_with_sum_brute):
        assert inspect.getsource(func).strip() in code, func.__name__


if __name__ == "__main__":
    for name, func in list(globals().items()):
        if name.startswith("test_"):
            func()
            print("OK", name)
