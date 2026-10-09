# make_operation('-', 10) поверне 10
# make_operation('*', 2, 0.5, 3) поверне 3

def make_operation(operator, *args):

    result = args[0]

    if operator == '+':
        return sum(args)

    if operator == '-':
        for num in args[1:]:
            result = result - num
        return result

    if operator == '*':
        for num in args[1:]:
            result = result * num
        return result


# print(make_operation('-', 10))            # 10
# print(make_operation('*', 2, 0.5, 3))     # 3

print(make_operation('+', 7, 7, 2))
print(make_operation('-', 5, 5, -10, -20))
print(make_operation('*', 7, 6))

# AI log: сам створив функцію, написав умови, прописав умову для оператора '+' через sum(), а для інших застопорився,
# не міг придумати, чи є такіж функції по типу sum(), для віднімання та множення,
# ментор(AI) допоміг розібрати логіку накопичення результату в окрему змінну, виокристання зрізів (щоб не віднімати перше число саме від себе)
# і виправити помилку, коли функція зупинялася на першому ж кроці через return усередині циклу.
