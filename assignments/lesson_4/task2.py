have_umbrella = False
rain_level = 0
have_hood = False
is_workday = False
# ожидаемый результат : True
prepared = have_umbrella or (rain_level < 5 and have_hood) or not (rain_level > 0 and is_workday)
print(prepared)
# Bag : not  применялся только к дождю,а должен был применятся к дождю и рабочему дню вмести.
# Ai log :C помощью AI разобрал  логические операторы  not,or и приоритет их выполнения
#Нашел ошибку  в исходном  выражение  и исправил ее с помощью скобок.