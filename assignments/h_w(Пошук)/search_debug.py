# AI log:
# просила пояснити щодо роботи двох вказівників у функції pair_sum_sorted() та перевіряла
# правильність своєї логіки

def binary_search_broken(items, target):
    low = 0
    high = len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
# Було: high = len(items) - індекс виходив за межі списку
# Стало: high = len(items) - 1  використовуємо індекс останнього елемента

# Було: low = mid - цикл зациклювався ба межа могла не змінюватися, під час пошуку числа 7 програма зациклюється
# Стало: low = mid + 1

# Було: high = mid - теж межа не змінюється
# Стало: high = mid - 1
numbers = list(range(0, 200, 2))
target = 198
target_2 = 7

print(binary_search_broken(numbers, target))
print(binary_search_broken(numbers, target_2))

items = [2, 7, 11, 15, 19, 26]


def pair_sum_sorted(items, target):
    left, right = 0, len(items) - 1
    while left < right:
        total = items[left] + items[right]
        if total == target:
            return (left, right)
        elif total < target:
            left += 1
        else:
            right -= 1
    return None

print(pair_sum_sorted(items, 26))
print(pair_sum_sorted(items, 9))
print(pair_sum_sorted(items, 100))