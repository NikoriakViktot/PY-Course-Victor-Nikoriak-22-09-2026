from collections import OrderedDict


class LRUCache:
    """Кеш на capacity записів; коли місця немає, викидає той, до якого найдовше не зверталися.

    OrderedDict пам'ятає порядок: на початку — найдавніший, у кінці — найсвіжіший.
    get і put — O(1).
    """

    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity має бути хоча б 1")
        self.capacity = capacity
        self._data = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key, default=None):
        if key not in self._data:
            self.misses += 1
            return default
        self.hits += 1
        self._data.move_to_end(key)          # щойно використаний — у кінець
        return self._data[key]

    def put(self, key, value):
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = value
        if len(self._data) > self.capacity:
            self._data.popitem(last=False)   # найдавніший — з початку

    def __contains__(self, key):
        """Перевірка без зміни порядку і статистики."""
        return key in self._data

    def __len__(self):
        return len(self._data)

    def keys(self):
        """Ключі від найдавнішого до найсвіжішого."""
        return list(self._data)

    def __repr__(self):
        return f"LRUCache(capacity={self.capacity}, keys={self.keys()!r})"
