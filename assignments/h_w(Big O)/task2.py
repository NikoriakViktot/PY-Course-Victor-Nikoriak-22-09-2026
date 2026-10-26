# AI log: none
import time

def common_elements_fast(first, second):
    seen = set(second)
    result = []
    for i in first:
        if i in seen:
            result.append(i)
    return  result

# question1 буде повільніша при збільшенні списков, бо кожного разу проходить по двум спискам
# у question1 складність - O(n²), тому час зросле у 4 рази, а у common_elements_fast - O(n) у 2 рази
def question1(first, second):
    res = []
    for el_first_list in first:
        if el_first_list in second:
            res.append(el_first_list)
    return res


first = list(range(2000))
second = list(range(500, 2000))

times = []
for _ in range(5):
    start = time.perf_counter()
    question1(first, second)
    times.append(time.perf_counter() - start)
print("question1, 2 000:", min(times))