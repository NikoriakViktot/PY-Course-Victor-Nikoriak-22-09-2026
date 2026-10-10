# В favorite_movie ми повертаємо результат і можемо в подальшому його зберегти в якусь змінну

# В favorite_movie_2 ми лише виводимо результат щоб його побачити, а сам результат нікуди не зберігається,
# тому коли визиваэмо print(favorite_movie_2(new_string)) отримуємо None, бо ми не повернули результат з тіла функції

def favorite_movie(name):
    return f"Мій улюблений фільм називається {name}"


new_string = 'Інтерстеллар'

print(favorite_movie(new_string))
favorite_movie('Dune')


def favorite_movie_2(name):
    print(f"Мій улюблений фільм називається {name}")


favorite_movie_2(new_string)
print(favorite_movie_2(new_string))

# AI log: none
