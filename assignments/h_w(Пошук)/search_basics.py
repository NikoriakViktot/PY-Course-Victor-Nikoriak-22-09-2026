# AI log: none
def linear_search(items, target):
    comparisons = 0
    for i in range(len(items)):
        comparisons += 1
        if items[i] == target:
            return i, comparisons
    return -1, comparisons


def binary_search(items, target):
    low, high = 0, len(items) - 1
    comparisons = 0
    while low <= high:
        mid = (low + high)// 2
        comparisons += 1
        if items[mid] == target:
            return mid, comparisons
        elif items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1, comparisons


numbers = list(range(0, 200, 2))

for target in [198, 42, 7]:
    # Передбачення:
    # для 198 лінійний пошук - 100 порівнянь(перевіряє елементи по черзі)
    # бінарний пошук - 7 порівнянь (щоразу ділить діапазон пошуку навпіл)
    # для 42: лінійний пошук - 22 порівняння, бінарний пошук - 7
    # для 7: лінійний пошук - 100 порівнянь(бо в списку немає 7, а перевірка буде всіх чисел)
    # бінарний пошук — 7 порівнянь.

    linear_index, linear_comparisons = linear_search(numbers, target)
    binary_index, binary_comparisons = binary_search(numbers, target)

    print(
        f"{target} -> linear: index {linear_index}, "
        f"{linear_comparisons} comparisons | "
        f"binary: index {binary_index}, "
        f"{binary_comparisons} comparisons"
    )