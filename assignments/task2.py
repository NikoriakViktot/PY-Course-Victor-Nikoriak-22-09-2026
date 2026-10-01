# Expected: True
have_umbrella = False
rain_level = 6.0
have_hood = True
is_workday = False

prepared = have_umbrella or rain_level < 5 and have_hood or not (rain_level > 0 and is_workday)
print(prepared)
# Bug: parentheses were missing, so `not` applied only to one condition instead of both.