#Task 2

#AI log: Not used


have_umbrella = False
rain_level = 5
have_hood = True
is_workday = False

prepared = have_umbrella or (rain_level < 5 and have_hood) or (rain_level > 0 and is_workday)
print(prepared)

#Bug: prepared = have_umbrella or (rain_level < 5 and have_hood) or (rain_level > 0 and is_workday) это исправленое выражение,
# ошибка была в нераставленых скобках, а также not перед rain level в 3 условии.
# После всех этих изменений при изменении входящих параметров мы можем получить False