from dispatch.structures.errors import EmptyError


class MinHeap:
    """Купа з мінімумом на вершині: push і pop — O(log n), peek — O(1).

    Елементи зберігаються в списку як повне бінарне дерево:
    діти вузла i — на позиціях 2*i + 1 і 2*i + 2, батько — (i - 1) // 2.
    Правило купи: батько не більший за своїх дітей.
    key — функція, за якою порівнюємо елементи (як key у sorted).
    """

    def __init__(self, items=(), key=None):
        self._key = key if key is not None else (lambda item: item)
        self._items = []
        for item in items:
            self.push(item)

    def push(self, item):
        self._items.append(item)
        self._sift_up(len(self._items) - 1)

    def pop(self):
        if not self._items:
            raise EmptyError("купа порожня")
        top = self._items[0]
        last = self._items.pop()
        if self._items:
            self._items[0] = last
            self._sift_down(0)
        return top

    def peek(self):
        if not self._items:
            raise EmptyError("купа порожня")
        return self._items[0]

    def _less(self, i, j):
        return self._key(self._items[i]) < self._key(self._items[j])

    def _sift_up(self, i):
        """Новий елемент піднімається, доки батько більший за нього."""
        while i > 0:
            parent = (i - 1) // 2
            if not self._less(i, parent):
                break
            self._items[i], self._items[parent] = self._items[parent], self._items[i]
            i = parent

    def _sift_down(self, i):
        """Елемент на вершині опускається до меншої дитини, доки вона менша за нього."""
        n = len(self._items)
        while True:
            smallest = i
            for child in (2 * i + 1, 2 * i + 2):
                if child < n and self._less(child, smallest):
                    smallest = child
            if smallest == i:
                break
            self._items[i], self._items[smallest] = self._items[smallest], self._items[i]
            i = smallest

    def __len__(self):
        return len(self._items)

    def __bool__(self):
        return bool(self._items)

    def __repr__(self):
        return f"MinHeap({self._items!r})"
