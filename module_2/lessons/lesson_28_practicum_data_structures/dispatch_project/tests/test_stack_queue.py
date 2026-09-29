import pytest

from dispatch.structures import EmptyError, Queue, Stack


def test_stack_is_lifo():
    stack = Stack()
    for item in ["a", "b", "c"]:
        stack.push(item)
    assert [stack.pop(), stack.pop(), stack.pop()] == ["c", "b", "a"]


def test_stack_peek_does_not_remove():
    stack = Stack([1, 2])
    assert stack.peek() == 2
    assert len(stack) == 2


def test_stack_iterates_from_top():
    assert list(Stack([1, 2, 3])) == [3, 2, 1]


def test_queue_is_fifo():
    queue = Queue()
    for item in ["a", "b", "c"]:
        queue.enqueue(item)
    assert [queue.dequeue(), queue.dequeue(), queue.dequeue()] == ["a", "b", "c"]


@pytest.mark.parametrize("structure, take", [
    (Stack(), Stack.pop), (Stack(), Stack.peek),
    (Queue(), Queue.dequeue), (Queue(), Queue.peek),
])
def test_empty_raises(structure, take):
    assert not structure
    with pytest.raises(EmptyError):
        take(structure)


def test_empty_error_is_lookup_error():
    """EmptyError — нащадок LookupError, як IndexError і KeyError (урок 13)."""
    with pytest.raises(LookupError):
        Stack().pop()
