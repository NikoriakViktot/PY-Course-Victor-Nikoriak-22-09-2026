# AI log: після перевірки на 0 та -7 звернулася з проханням пояснити чому не працює код
# також попросила пояснити як працює перевірка isdigit

number = input("Введіть число ").strip()

if number.isdigit():
     is_even = int(number) % 2 == 0
     if is_even:
       print("Число парне /", is_even)
     else:
       print("Число не парне /", number)
else:
    print("Введіть число цифрами ")