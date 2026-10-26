def question1(first_list, second_list):
    res = []
    for el_first_list in first_list:
        if el_first_list in second_list:
            # O(n²) бо маємо два цикли, зовнішній цикл проходить по першому списку
            # та, ще перевірка проходить по другому списку
            res.append(el_first_list)
    return res

def question2(n):
    for _ in range(10):
        # O(1) цикл виконується рівно 10 разів
        # незалежно від значення n
        n *= 3
    return n

def question3(first_list, second_list):
    temp = first_list[:]
    for el_second_list in second_list:
        flag = False
        for check in temp:
            if el_second_list == check:
                # O(n²) бо для кожного елемента second_list перебираємо
                # елементи temp
                flag = True
                break
        if not flag:
            temp.append(el_second_list)
    return temp

def question4(input_list):
    res = input_list[0]
    for el in input_list:
        if el > res:
            # O(n) цикл проходить по всіх елементах списку один раз
            res = el
    return res

def question5(n):
    res = []
    for i in range(n):
        for j in range(n):
            res.append((i, j))
        # O(n²) бо два вкладені цикли
    return res

def question6(n):
    while n > 1:
        n //= 2
    # O(log n) на кожному проході значення n ділиться на 2
    return n

# AI log:
# AI визначив складність question1 як O(n²), оскільки для кожного елемента
# першого списку перевірка in може переглянути весь другий список
# Складність question3 також O(n²), оскільки для кожного елемента другого
# списку виконується пошук у temp, який може збільшуватися.
# Відповіді ШІ збіглися з моїми