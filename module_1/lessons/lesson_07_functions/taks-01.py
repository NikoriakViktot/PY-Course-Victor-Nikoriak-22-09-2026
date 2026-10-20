# Task 1

# AI log: Not used


def favorite_movie(movie):
    return f"My favorite movie is named {movie}"


new_string = "2025: F1"

print(favorite_movie(new_string))


def favorite_movie_2(movie):
    print(f"My favorite movie is named {movie}")


print(favorite_movie_2(new_string))

# В favorite_movie_2 вместо return мы используем print то есть функция ничего не возращает
# если функции нечего возращать она возвращает параметр по умолчанию
# По умолчанию функция всегда возращает None что мы и получили при вызове функции по мимо print
