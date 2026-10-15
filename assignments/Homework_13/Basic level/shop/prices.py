def with_discount(price, percent):
    return round(price * (1 - (percent / 100)), 2)

def total(prices):
    return round(sum(prices), 2)

if __name__ == "__main__":
    print(with_discount(100, 20))
    print(total([100, 569, 257, 789]))

# AI log: no AI