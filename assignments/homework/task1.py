# AI log: none
def favorite_movie(name):
    return f"My favorite movie is named {name}"


new_string = "Supernatural"
print(favorite_movie(new_string))

# Нічого не виведе, тому що функція повертає значення через return, але ми його нікуди не виводимо
favorite_movie("Dune")

# Спочатку виконується print всередині функції та виводить
# "My favorite movie is named Supernatural"
# А так, як функція не має return, останній print при виклику функції виведе None
def favorite_movie_2(name):
    print(f"My favorite movie is named {name}")

print(favorite_movie_2(new_string))