DISTANCES_KM = {
    frozenset({"Поділ", "Оболонь"}): 7,
    frozenset({"Поділ", "Центр"}): 3,
    frozenset({"Центр", "Оболонь"}): 9,
    frozenset({"Центр", "Лівобережна"}): 8,
    frozenset({"Поділ", "Лівобережна"}): 10,
    frozenset({"Оболонь", "Лівобережна"}): 14,
}


def estimate_price(origin, destination):
    """Ціна поїздки між районами: посадка 60 грн + 15 грн/км.

    У справжньому сервісі тут був би повільний запит до картографічного API —
    тому результати кешуємо (Dispatcher.route_price).
    """
    if origin == destination:
        return 60
    return 60 + 15 * DISTANCES_KM[frozenset({origin, destination})]
