# AI log: Мої відповіді щодо складності question1 та question3 збіглися з відповіддю ШІ (O(n²) для обох).
# Також ментор допоміг мені розібратися з прихованими циклами (оператор in), правилом відкидання числових множників (2N² -> O(n²)),
# розпізнаванням константного часу O(1) у циклах із фіксованою кількістю кроків,
# та логарифмічною складністю O(log n) для алгоритмів, що постійно відсікають половину даних.


def question1(first_list, second_list):
    res = []

    for el_first_list in first_list:

        if el_first_list in second_list:
            res.append(el_first_list)

    return res

    # якщо first_list, second_list = ['first', 'second','third'], то ми отримаємо res = ['first', 'second','third'],
    # це буде складність O(n²), бо ми маємо подвоєнний цикл (for + in)


def question2(n):
    for _ in range(10):
        n *= 3

    return n

    # це складність O(1), бо ми вже знаємо точну к-ть циклів(range(10)), а величина числа(n) тут не буде грати ролі


def question3(first_list, second_list):
    temp = first_list[:]

    for el_second_list in second_list:
        flag = False

        for check in temp:
            if el_second_list == check:
                flag = True
                break

        if not flag:
            temp.append(el_second_list)

    return temp

    # це складність O(n²), бо ми маємо подвоєнний цикл for(цикл в циклі), O(2n²) = O(n²)


def question4(input_list):
    res = input_list[0]

    for el in input_list:
        if el > res:
            res = el

    return res

    # це складність O(n), бо ми маємо один цикл for, в якому шукаємо найбільше значення


def question5(n):
    res = []

    for i in range(n):
        for j in range(n):
            res.append((i, j))

    return res

    # це складність O(n²), бо ми маємо подвоєнний цикл for(цикл в циклі)


def question6(n):
    while n > 1:
        n //= 2

    return n

    # це складність O(log n), бо ми відсікаємо половину значень
