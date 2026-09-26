import heapq
import random

import pytest

from dispatch.structures import EmptyError, MinHeap


def test_pop_returns_smallest_first():
    heap = MinHeap([5, 1, 4, 2, 3])
    assert [heap.pop() for _ in range(5)] == [1, 2, 3, 4, 5]


def test_key_function():
    heap = MinHeap([("#2", "09:40"), ("#1", "09:25"), ("#3", "10:05")], key=lambda o: o[1])
    assert heap.pop() == ("#1", "09:25")


def test_peek_and_len():
    heap = MinHeap([3, 1, 2])
    assert heap.peek() == 1
    assert len(heap) == 3


def test_empty_pop_raises():
    with pytest.raises(EmptyError):
        MinHeap().pop()


@pytest.mark.parametrize("seed", range(20))
def test_matches_sorted_and_heapq(seed):
    """Властивість: купа видає елементи в тому самому порядку, що й sorted і heapq."""
    rng = random.Random(seed)
    items = [rng.randint(0, 50) for _ in range(rng.randint(0, 40))]
    heap = MinHeap(items)
    ours = [heap.pop() for _ in range(len(heap))]

    std = list(items)
    heapq.heapify(std)
    theirs = [heapq.heappop(std) for _ in range(len(std))]

    assert ours == sorted(items) == theirs
