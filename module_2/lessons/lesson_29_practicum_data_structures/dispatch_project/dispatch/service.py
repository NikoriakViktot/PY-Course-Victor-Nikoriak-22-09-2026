from dispatch.pricing import estimate_price
from dispatch.structures import EmptyError, LRUCache, MinHeap, Queue, Stack, Trie


class Dispatcher:
    """Диспетчерська: приймає замовлення, видає їх кур'єрам, вміє скасувати дію.

    Кожна структура відповідає за одне питання:
      Queue   — звичайні замовлення: хто раніше прийшов, того раніше обслужать;
      MinHeap — термінові: першим — той, у кого найраніший дедлайн;
      Stack   — історія дій для «скасувати» (і повернуті замовлення);
      Trie    — автодоповнення адрес;
      LRUCache — ціни маршрутів, щоб не питати повільний сервіс двічі.
    """

    def __init__(self, addresses=(), price_function=estimate_price, cache_size=3):
        self._regular = Queue()
        self._urgent = MinHeap(key=lambda order: order.deadline)
        self._returned = Stack()          # скасовані призначення — видаємо першими
        self._history = Stack()
        self._addresses = Trie(addresses)
        self._price_function = price_function
        self._prices = LRUCache(cache_size)
        self._assigned = {}               # кур'єр -> список замовлень

    # --- замовлення -------------------------------------------------------

    def receive(self, order, urgent=False):
        if urgent:
            if order.deadline is None:
                raise ValueError(f"термінове замовлення #{order.order_id} без дедлайну")
            self._urgent.push(order)
        else:
            self._regular.enqueue(order)

    def next_order(self):
        """Хто наступний: повернуте → найтерміновіше → найстаріше звичайне."""
        if self._returned:
            return self._returned.pop()
        if self._urgent:
            return self._urgent.pop()
        if self._regular:
            return self._regular.dequeue()
        raise EmptyError("немає замовлень")

    def assign(self, courier):
        order = self.next_order()
        self._assigned.setdefault(courier, []).append(order)
        self._history.push((courier, order))
        return order

    def undo(self):
        """Скасувати останнє призначення: замовлення повертається і буде видане першим."""
        courier, order = self._history.pop()
        self._assigned[courier].remove(order)
        self._returned.push(order)
        return courier, order

    def assigned_to(self, courier):
        return list(self._assigned.get(courier, []))

    def __len__(self):
        """Скільки замовлень чекає на кур'єра."""
        return len(self._returned) + len(self._urgent) + len(self._regular)

    # --- адреси й ціни ----------------------------------------------------

    def suggest(self, prefix, limit=5):
        return self._addresses.starts_with(prefix, limit)

    def route_price(self, origin, destination):
        key = (origin, destination)
        price = self._prices.get(key)
        if price is None:
            price = self._price_function(origin, destination)
            self._prices.put(key, price)
        return price

    @property
    def cache_stats(self):
        return {"hits": self._prices.hits, "misses": self._prices.misses, "size": len(self._prices)}

    def __repr__(self):
        return f"Dispatcher(очікують={len(self)}, адрес={len(self._addresses)})"
