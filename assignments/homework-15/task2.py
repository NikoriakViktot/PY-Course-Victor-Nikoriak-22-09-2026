# AI log: Ментор вказав на логічну помилку у використанні time.perf_counter(), запропонував застосувати принцип DRY (винести заміри у зовнішній цикл)
# та підштовхнув математично вирахувати точний час виконання O(n²) для 400 000 елементів (~11 хвилин).


# коли довжина списків подвоїться, час виконання функції question1 збільшиться в 4 рази, а common_elements_fast в 2 рази

# порівнюючи результати з моїми припущеннями, все так й склалось, при подвоєнні повільна ф-ція O(n²), зростає в 4 рази, а швидка O(n) в 2 рази

# спробувавши запустити повільну ф-цію на 400 000 чисел, через декілька секунд вже стане зрозуміло, що вона не виконається швидко,
# тому що в O(n²) час буде збільшуватись квадратично збільшенню даних, а саме в 10_000 разів(400k/4k ** 2), що займе приблизно 11 хв

import time


def question1(first_list, second_list):
    res = []

    for el_first_list in first_list:

        if el_first_list in second_list:
            res.append(el_first_list)

    return res


def common_elements_fast(first_list, second_list):
    res = []
    s_list = set(second_list)

    for el_first in first_list:

        if el_first in s_list:
            res.append(el_first)

    return res


def test_low_func():
    sizes_low = [1_000, 2_000, 4_000]

    for size in sizes_low:

        times_low = []

        first = list(range(size))
        second = list(range(size))

        for _ in range(5):
            start = time.perf_counter()
            question1(first, second)

            times_low.append(time.perf_counter() - start)

        print(f"question1, {size}:, {min(times_low):.10f}")


def test_fast_func():
    sizes_fast = [1_000, 100_000, 200_000]

    for size in sizes_fast:

        first = list(range(size))
        second = list(range(size))

        times_fast = []

        for _ in range(5):
            start = time.perf_counter()
            common_elements_fast(first, second)

            times_fast.append(time.perf_counter() - start)

        print(f"common_elements_fast, {size}:, {min(times_fast):.10f}")


test_low_func()
test_fast_func()

# Результати:
# question1, 1000:, 0.0043081000
# question1, 2000:, 0.0171125000
# question1, 4000:, 0.0682997000
# common_elements_fast, 1000:, 0.0000691000
# common_elements_fast, 100000:, 0.0088735000
# common_elements_fast, 200000:, 0.0192028000
# common_elements_fast, 400000:, 0.0403835000
