def favorite_movie(movie):
    return f"Мій улюблений фільм називається {movie}"
new_string = "2001: Космічна одіссея"
print(favorite_movie(new_string))
# Функція повертає рядок, але без print він не виводиться на екран.
favorite_movie("Дюна")
def favorite_movie_2(movie):
    print(f"Мій улюблений фільм називається {movie}")
# Функція виводить текст, а зовнішній print виводить None.
print(favorite_movie_2(new_string))
# Al log :Попросив ШІ пояснити різницю між return i print