# days[0] = Monday: первый день
# week[1] =Monday: первый день недели
# reverse_week["Sunday"] = 7 день
days = ["Monday", "Thuesday" ,"Wedneday", "Thursday", "friday", "Saturday", "Sunday"]
week = {number: day for number, day in enumerate(days, 1)}
reverse_week = {day: number for number, day in enumerate(days, 1)}
print(days[0])
print(week[1])
print(reverse_week["Sunday"])
# Все три проверки получились
# Al log : С помощью Ai разбирал задание и писал код самостоятельно.