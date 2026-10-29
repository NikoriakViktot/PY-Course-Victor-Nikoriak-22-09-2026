# AI log: За допомогою підказок від ментора протестував ШІ-код і виявив два баги: нульовий старт ламав пошук від'ємних рекордів,
# а сума найпершого вікна ігнорувалася. Зрозумівши ці вразливості, самостійно виправив власну функцію,
# правильно задавши стартові значення для змінного вікна (window) та рекорду (best).

def max_window_sum(items, k):
    best = sum(items[:k])
    window = sum(items[:k])

    for i in range(k, len(items)):
        window = window + items[i] - items[i - k]

        if window > best:
            best = window

    return best


print(max_window_sum([12, 4, 9, 20, 3, 15, 7], 3))  # 38
print(max_window_sum([-10, -5, -2, -8], 2))  # -7
print(max_window_sum([100, 2, 1, 5], 2))  # 102
print(max_window_sum([], 3))  # 0

## код від ШІ:

# def max_window_sum(items, k):
#     max_sum = 0
#     current_window = sum(items[:k])
#
#     for i in range(1, len(items) - k + 1):
#         current_window = current_window - items[i - 1] + items[i + k - 1]
#
#         if current_window > max_sum:
#             max_sum = current_window
#
#     return max_sum


# # очікував отримати -7, отримав 0
# # отримуємо 0 через те що, в перевірці наше мінусове значення(-7) порівнюється з max_sum = 0, -7 > 0, тому умова не виконується
# # прибрати проблему можна надавши max_sum суму першого вікна
# print(max_window_sum([-10, -5, -2, -8], 2))

# # очікував отримати 102, отримав 6
# # отримуємо 6 через те що, в циклі сума першого вікна пропускається, проблема прибирається надавши max_sum суму першого вікна
# print(max_window_sum([100, 2, 1, 5], 2))

# # очікував отримати 0, отримав 0
# print(max_window_sum([], 3))
