# days[0] = Monday
# week[1] = Monday
# reverse_week["Sunday"] = 7

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

week = {number: item for number, item in enumerate(days, start=1)}
# print(week)

reverse_week = {item: number for number, item in enumerate(days, start=1)}
# print(reverse_week)

# print(days[0])
# print(week[1])
# print(reverse_week["Sunday"])

# AI log: Структуру dict comprehension прописав самостійно, але забув назву функції enumerate().
# За допомогою ментора розібрав помилку TypeError у словниковому виразі.
# Зрозумів, що enumerate() повертає готовий рядок (назву дня), тому намагатися
# використати його як індекс (days[item]) було помилкою.
