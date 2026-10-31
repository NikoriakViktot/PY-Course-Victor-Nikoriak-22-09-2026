def with_discount(price, percent):
    '''возвращает цену после применения процентной скидки, округлённую до двух знаков после запятой.'''
    new_price = price * (1 - (percent / 100))
    return round(new_price, 2)


def total(prices):
    '''возвращает сумму списка цен, округлённую до двух знаков после запятой.'''
    return round(float(sum(prices)),2)


if __name__ == "__main__":
    print(with_discount(100, 21))
    print(total([1, 42321.223, 32313, 23213]))
