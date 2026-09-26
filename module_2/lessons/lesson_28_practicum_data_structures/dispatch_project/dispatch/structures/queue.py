from collections import deque

from dispatch.structures.errors import EmptyError


class Queue:
    """Черга (FIFO): першим прийшов — першим обслужений.

    Всередині deque: додавання в кінець і взяття з початку — O(1).
    У звичайному списку list.pop(0) зсуває всі елементи — O(n).
    """

    def __init__(self, items=()):
        self._items = deque(items)

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        if not self._items:
            raise EmptyError("черга порожня")
        return self._items.popleft()

    def peek(self):
        if not self._items:
            raise EmptyError("черга порожня")
        return self._items[0]

    def __len__(self):
        return len(self._items)

    def __bool__(self):
        return bool(self._items)

    def __iter__(self):
        """Від голови до хвоста — у порядку обслуговування."""
        return iter(self._items)

    def __repr__(self):
        return f"Queue({list(self._items)!r})"
