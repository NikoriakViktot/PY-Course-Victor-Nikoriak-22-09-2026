# AI log: просила перевірити порядок обчислення коду

have_umbrella = True
rain_level = 0.0
have_hood = True
is_workday = True

prepared = have_umbrella or (rain_level < 5 and have_hood) or not (rain_level > 0 and is_workday)

print(prepared)