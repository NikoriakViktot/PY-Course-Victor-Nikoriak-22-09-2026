# AI log: використовувала для перекладу завдання, пояснень що саме від мене потрібно, та для допомоги з помилками при створенні comprehension
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
#1
week = {}
for i, day in enumerate(days, start=1):
  week[i] = day
print(week)
#2
week = {i: day for i, day in enumerate(days, start=1)}
print(week)

#3
reverse_week = {day: number for number, day in week.items()}
print(reverse_week)