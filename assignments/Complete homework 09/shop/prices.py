# AI log: Claude,використано для перекладу завдання та пояснення що саме потрібно зробити в завданні,
# також для допомоги з розумінням помилок в моєму коді

def with_discount(price, percent):
  return round(price * (1 - percent / 100), 2)


def total(prices):
  return sum(prices)


if __name__ == "__main__":
  print(with_discount(100, 25))
  print(total([100, 200, 700]))