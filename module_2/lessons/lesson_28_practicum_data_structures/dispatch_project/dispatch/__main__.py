"""Демо: python -m dispatch"""

from dispatch import Dispatcher, Order

ADDRESSES = ["Хрещатик, 1", "Хрещатик, 22", "Хорива, 5", "Оболонська, 12", "Олегівська, 3", "Поділ, Контрактова, 2"]


def main():
    d = Dispatcher(ADDRESSES)
    d.receive(Order(101, "Оболонська, 12"))
    d.receive(Order(102, "Хорива, 5"))
    d.receive(Order(103, "Хрещатик, 22", deadline="09:40"), urgent=True)
    d.receive(Order(104, "Олегівська, 3", deadline="09:25"), urgent=True)
    print(d)

    for courier in ["Оксана", "Тарас", "Ігор"]:
        print(f"{courier} ← {d.assign(courier)}")

    courier, order = d.undo()
    print(f"скасовано: {courier} ← {order}")
    print(f"Марія ← {d.assign('Марія')}")
    print(f"Оксана ← {d.assign('Оксана')}")
    print(d)

    print("Хр… →", d.suggest("Хр"))
    print("О… →", d.suggest("О"))

    for route in [("Поділ", "Оболонь"), ("Центр", "Поділ"), ("Поділ", "Оболонь")]:
        print(" → ".join(route), d.route_price(*route), "грн")
    print(d.cache_stats)


if __name__ == "__main__":
    main()
