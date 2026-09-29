"""Перевірки stream_core.py: python test_stream_core.py (або pytest)."""
import json
import sys
import tempfile
import threading
from itertools import islice
from pathlib import Path

from stream_core import (
    COMPANIES, MarketState, moving_average, only_companies, read_ndjson, replay_ndjson,
    transaction_stream,
)


def test_stream_is_deterministic_and_ordered():
    first = list(islice(transaction_stream(seed=1), 200))
    again = list(islice(transaction_stream(seed=1), 200))
    other = list(islice(transaction_stream(seed=2), 200))
    assert first == again and first != other
    assert [tx["id"] for tx in first] == list(range(1, 201))
    times = [tx["time"] for tx in first]
    assert times == sorted(times) and len(set(times)) == len(times)
    assert {tx["company"] for tx in first} == set(COMPANIES)


def _write_blocks(path, per_company=5):
    """Файл як у ноутбуці: угоди кожної компанії окремим блоком."""
    with open(path, "w", encoding="utf-8") as f:
        for name in ("Нафтогаз", "Розетка"):
            for i in range(per_company):
                tx = {"id": i + 1, "company": name, "price": 100.0 + i, "volume": 10,
                      "timestamp": f"2024-01-01T09:00:{i:02d}"}
                f.write(json.dumps(tx, ensure_ascii=False) + "\n")


def test_read_ndjson_is_lazy():
    missing = read_ndjson("no/such/file.ndjson")   # файл ще не відкривається
    try:
        next(missing)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("очікували FileNotFoundError лише на next()")


def test_replay_interleaves_and_repeats():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "tx.ndjson"
        _write_blocks(path)
        first = list(islice(replay_ndjson(path, ["Нафтогаз", "Розетка"]), 14))
        names = [tx["company"] for tx in first[:4]]
        assert names == ["Нафтогаз", "Розетка", "Нафтогаз", "Розетка"]
        assert len(first) == 14                             # після 10 угод файл пішов на друге коло
        assert [tx["id"] for tx in first] == list(range(1, 15))
        empty = list(replay_ndjson(path, ["Київстар"]))     # компанії немає — потік завершується
        assert empty == []


def test_only_companies():
    picked = list(islice(only_companies(transaction_stream(seed=3), {"Розетка"}), 20))
    assert len(picked) == 20 and all(tx["company"] == "Розетка" for tx in picked)


def test_state_is_thread_safe():
    state = MarketState(transaction_stream(seed=4), window=50)
    errors = []

    def worker():
        for _ in range(200):
            try:
                state.advance(5)
                state.snapshot()
            except Exception as exc:          # noqa: BLE001 — тест збирає будь-яку помилку
                errors.append(exc)

    old = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    sys.setswitchinterval(old)
    snap = state.snapshot()
    assert errors == []
    assert snap["total"] == 8 * 200 * 5 == sum(snap["counts"].values())
    assert all(len(points) <= 50 for points in snap["series"].values())


def test_shared_generator_without_lock_breaks():
    """Так працював старий застосунок: один генератор, next() з кількох потоків без замка."""
    import time

    def slow_stream():
        n = 0
        while True:
            time.sleep(0.001)       # імітує роботу всередині генератора
            n += 1
            yield n

    gen = slow_stream()
    errors = []

    def worker():
        for _ in range(50):
            try:
                next(gen)
            except ValueError as exc:
                errors.append(str(exc))

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert "generator already executing" in errors


def test_window_resize_keeps_latest():
    state = MarketState(only_companies(transaction_stream(seed=5), {"Київстар"}), window=30)
    state.advance(30)
    before = state.snapshot()["series"]["Київстар"]
    state.set_window(10)
    after = state.snapshot()["series"]["Київстар"]
    assert after == before[-10:]


def test_finished_stream():
    state = MarketState(iter([]))
    assert state.advance(5) == 0 and state.snapshot()["finished"] is True


def test_moving_average():
    assert moving_average([1, 2, 3, 4], 2) == [1.0, 1.5, 2.5, 3.5]
    assert moving_average([], 3) == []


if __name__ == "__main__":
    for name, func in list(globals().items()):
        if name.startswith("test_"):
            func()
            print("OK", name)
