from dispatch.structures.errors import EmptyError


class Stack:
    """Стек (LIFO): останнім поклали — першим узяли. Усі операції O(1)."""

    def __init__(self, items=()):
        self._items = list(items)       # вершина стеку — кінець списку

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if not self._items:
            raise EmptyError("стек порожній")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise EmptyError("стек порожній")
        return self._items[-1]

    def __len__(self):
        return len(self._items)

    def __bool__(self):
        return bool(self._items)

    def __iter__(self):
        """Від вершини до дна — у тому порядку, в якому їх діставатиме pop()."""
        return reversed(self._items)

    def __repr__(self):
        return f"Stack({self._items!r})"
