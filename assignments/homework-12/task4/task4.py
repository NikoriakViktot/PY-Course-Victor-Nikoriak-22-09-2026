# AI log: Попросив допомогти з помилками у функціях додавання та видалення. Разом із ментором (AI) розібрав,
# як безпечно створювати словники через None та як працює пошук елемента у списку.
# Самостійно переписав логіку видалення через метод .remove() із зупинкою циклу (break), а також виправив неймінг змінних для кращої читабельності.

import json


def load(path):

    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save(path, records):

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def add_book(path, records=None):

    load_list = load(path)

    if not records:

        records = {}

        name_book = input("Введіть назву книги: ")
        records["назва книги"] = name_book

        author = input("Введіть автора: ")
        records["автор"] = author

    load_list.append(records)

    save(path, load_list)


def add_movie(path, records=None):

    load_list = load(path)

    if not records:

        records = {}

        name_movie = input("Введіть назву фільму: ")
        records["назва фільму"] = name_movie

        author = input("Введіть автора: ")
        records["автор"] = author

    load_list.append(records)

    save(path, load_list)


def remove_book(path, name_book):

    load_list = load(path)

    if not name_book:

        name_book = input("Введіть назву книги для видалення: ")

    for record in load_list:

        if record['назва книги'] == name_book:
            load_list.remove(record)
            break

    save(path, load_list)


def remove_movie(path, name_movie):

    load_list = load(path)

    if not name_movie:

        name_movie = input("Введіть назву фільму для видалення: ")

    for record in load_list:

        if record['назва фільму'] == name_movie:
            load_list.remove(record)
            break

    save(path, load_list)


def list_p(path):   # змінив назву ф-ції на list_p(), щоб не перекривати стандартну ф-цію list()
    for dict_ in load(path):
        print(dict_)


# Список улюблених книжок
favorite_books = [
    {
        "назва книги": "Інститут",
        "автор": "Стівен Хокінг"
    },
    {
        "назва книги": "Точка Обману",
        "автор": "Ден Браун"
    },
    {
        "назва книги": "Казка",
        "автор": "Стівен Кінг"
    },
    {
        "назва книги": "Рекурсія",
        "автор": "Блейк Крауч"
    }
]

# Список улюблених фільмів
favorite_movies = [
    {
        "назва фільму": "Інтерселлар",
        "автор": "Крістофер Нолан"
    },
    {
        "назва фільму": "Хатіко: Вірний друг",
        "автор": "Лассе Гальстрем"
    },
    {
        "назва фільму": "Гаррі Поттер",
        "автор": "Кріс Коламбус"
    },
    {
        "назва фільму": "Таксі",
        "автор": "Жерар Пірес"
    }
]

print('Улюблені книги:', '-' * 40)
save('my_books.json', favorite_books)
# my_books = load('my_books.json')
# print(my_books)
# remove_book('my_books.json', name_book='Казка')
list_p('my_books.json')

print('')

print('Улюблені фільми:', '-' * 40)
save('my_movies.json', favorite_movies)
# my_movies = load('my_movies.json')
# print(my_movies)
# remove_movie('my_movies.json', name_movie='Гаррі Поттер')
list_p('my_movies.json')

print('')
