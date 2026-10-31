def max_window_sum(items, k):
    current_sum, max_sum = sum(items[0:k]), sum(items[0:k])
    for i in range(k, len(items)):
        current_sum += items[i] - items[i - k]
        if current_sum > max_sum:
            max_sum = current_sum
    return max_sum


items = [12, 4, 9, 20, 3, 15, 7]
k = 3
print(max_window_sum(items, k))

# ШІ частина:
# def max_window_sum(items, k):
#     current_sum = sum(items[:k])
#     max_sum = current_sum
#
#     for i in range(k, len(items)):
#         current_sum += items[i] - items[i - k]
#         max_sum = max(max_sum, current_sum)
#
#     return max_sum
#
# print(max_window_sum([1, 2, 3], 5))
# # Очікуваний результат: помилка, бо k більший за довжину списку
# # Фактичний результат: 6, функція підсумувала всі елементи списку, хоча в ньому немає 5 елементів
# print(max_window_sum([1, 2, 3], 0))
# # Очікуваний результат: помилка, бо некоректне значення k
# # Фактичний результат: 0, функція прийняла значення 0
# print(max_window_sum([], 1))
# # Очікуваний результат: помилка тому, що список порожній
# # Фактичний результат: 0
#
# # ШІ не перевірив коректність значення k та чи порожній список
