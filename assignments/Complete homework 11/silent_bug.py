# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні,
# також для допомоги з розумінням помилок в моєму коді

"""
def total_of(numbers):
    total = 0
    for n in numbers:
        try:
            total += nubmer
        except Exception as e:
          print(type(e).__name__ + ":", e)
          raise
    return total

print(total_of([1, 2, 3]))
"""
# не вірно вказано назву аргумент в тілі функціїї (nubmer)
# що видав python:
"""
NameError: name 'nubmer' is not defined
---------------------------------------------------------------------------
NameError                                 Traceback (most recent call last)
/tmp/ipykernel_5292/1904692166.py in <cell line: 0>()
      9     return total
     10 
---> 11 print(total_of([1, 2, 3]))

/tmp/ipykernel_5292/1904692166.py in total_of(numbers)
      3     for n in numbers:
      4         try:
----> 5             total += nubmer
      6         except Exception as e:
      7           print(type(e).__name__ + ":", e)

NameError: name 'nubmer' is not defined
"""

# nubmer не визначене, немає змінної з такою назвою
# далі бачимо що помилка в 5 рядку, а викликана в 11, коли ми викликали ф-цію


def total_of(numbers):
    total = 0
    for n in numbers:
      if not isinstance(n, (int, float)):
        raise TypeError(f"Expected a number")
      total += n
    return total


try:
    print(total_of([1, 2, 'l']))
except TypeError as e:
    print("TypeError:", e)

# змінила nubmer на n, прибрала except Exception (надто загальна)
# додала перевірку типу, яка видасть TypeError, тому що на мою думку це важливо
# якби ф-ція обробляла 10 000 записів, вона б щоразу мовчки пропускала помилку