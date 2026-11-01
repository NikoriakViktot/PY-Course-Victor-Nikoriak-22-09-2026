# AI log: За допомогою підказок від ментора подолав плутанину з індексами, що спричиняла нескінченні цикли.
# Самостійно виправив off-by-one помилку та оновлення меж (mid +/- 1) у бінарному пошуку, а також реалізував правильний рух "двох покажчиків" із
# коректною умовою зупинки (low < high) у pair_sum_sorted.

# ми отримуємо вічний цикл при пошуку 7, коли ми доходимо до high = 4, ми отримуємо вічний цикл, становляться незмінними (mid = 3, high = 4),
# щоб це виправити треба в умові items[mid] < target додати зміну значення low


def binary_search_broken(items, target):
    low = 0

    # ми не пройдемо всі значення, бо індекси починаються з 0, а len() видає кількість елементів починаючи з 1, тому -1
    high = len(items) - 1

    # додав знак дорівнює, щоб коли low = high ми могли дістати це значення
    while low <= high:
        mid = (low + high) // 2

        if items[mid] == target:
            print(f"Виконано, знайшли {mid}")
            return mid

        if items[mid] < target:
            print(f"Наше число менше за необхідне {mid}")

            # додаємо одиницю, щоб прибрати вічний цикл
            low = mid + 1

        else:
            print(f"Наше число більше за необхідне {mid}")

            # відсікаємо mid який вже не підійшов, -1
            high = mid - 1

            print(
                f"index low -> {low} ({items[low]}), index mid -> {mid} ({items[mid]}), "
                f"index high -> {high} ({items[high]})")

    return -1


def pair_sum_sorted(items, target):
    low, high = 0, len(items) - 1

    while low < high:

        if items[low] + items[high] == target:
            return low, high

        if items[low] + items[high] < target:
            low += 1

        else:
            high -= 1

    return None


list1 = list(range(0, 200, 2))

print(list1)

print(binary_search_broken(list1, 198))
print('-' * 25)
print(binary_search_broken(list1, 7))

list2 = [2, 7, 11, 15, 19, 26]
print('-' * 25)
print(pair_sum_sorted(list2, 30))
