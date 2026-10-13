def with_discount(price, percent):
    result = price - price * percent
    return round(result, 2)


def total(prices):
    result = sum(prices)
    return round(result, 2)


def t():
    print('-' * 50)


if __name__ == '__main__':
    print(with_discount(250, 0.5))
    print(total([35, 6, 17]))

# AI log: none
