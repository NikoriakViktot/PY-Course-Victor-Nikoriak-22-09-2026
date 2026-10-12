# Task 3
from turtledemo.penrose import start

# AI log:Not used

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

week = {number: item for number, item in enumerate(days, start=1)}

reverse_week = {item: number for number, item in enumerate(days, start=1)}

print(days)
print(week)
print(reverse_week)
