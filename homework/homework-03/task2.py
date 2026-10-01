#AI log: none
have_umbrella = True
rain_level = 0.0
have_hood = True
is_workday = True

prepared = have_umbrella or rain_level < 5 and have_hood or not rain_level > 0 and is_workday
# Expected: True
print(prepared)

have_umbrella = False
rain_level = 0.0
have_hood = False
is_workday = False

prepared = have_umbrella or rain_level < 5 and have_hood or not rain_level > 0 and is_workday
# Expected: True
print(prepared)
# Bug: not має вищий пріоритет, тому спочатку спрацьовує умова (not rain_level > 0), а за умовою потрібно перевірити
# не йде дощ (rain_level > 0) і це робочий день, а потім not до об'єднаного результату (rain_level > 0 and is_workday)

prepared = have_umbrella or (rain_level < 5 and have_hood) or not (rain_level > 0 and is_workday)
# Expected: True
print(prepared)