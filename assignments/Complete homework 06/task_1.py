# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні

def favorite_movie(name):
    return f"My favorite movie is named {name}"

new_string = "2001: A Space Odyssey"
print(favorite_movie(new_string))
#My favorite movie is named 2001: A Space Odyssey

favorite_movie("Dune")
#nothing - without print

def favorite_movie_2(name):
    print (f"My favorite movie is named {name}")

print(favorite_movie_2(new_string))
#My favorite movie is named 2001: A Space Odyssey (друк з функції)
#та None - тому що без return функція нічого не повернула, і ми намагаємось друкувати "нічого"

