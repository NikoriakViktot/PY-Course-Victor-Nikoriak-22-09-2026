# AI log: За допомогою підказок від ментора оптимізував linear_search, замінивши прихований цикл .index() на enumerate().
# Проаналізував реальну складність binary_search (O(log n)) та виправив математичну помилку в розрахунку кроків,
# усвідомивши принцип ділення діапазону індексів.

# лінійній ф-ції знадобиться перевірити всі елементи списку(100 кроків), бо це O(n)
# бінарній ф-ції знадобиться декілька кроків(4-5), бо це O(log n)

# я помилився з бінарною ф-єю, бо не правильно розрахував ділення індексів


def linear_search(items, target):
    comparisons = 0

    for index, item in enumerate(items):
        comparisons += 1

        if item == target:
            return (index, comparisons)

    return (-1, comparisons)


def binary_search(items, target):
    low, high = 0, len(items) - 1
    comparisons = 0

    while low <= high:
        index = (low + high) // 2
        comparisons += 1

        if items[index] == target:
            return (index, comparisons)

        if items[index] < target:
            low = index + 1

        if items[index] > target:
            high = index - 1

    return (-1, comparisons)


numbers = list(range(0, 200, 2))

num_set = [198, 42, 7]

for num in num_set:
    l_s = linear_search(numbers, num)
    b_s = binary_search(numbers, num)

    print(f"{num} -> linear: index {l_s[0]}, {l_s[1]} comparisons"
          f" | binary: index {b_s[0]}, {b_s[1]} comparisons")
