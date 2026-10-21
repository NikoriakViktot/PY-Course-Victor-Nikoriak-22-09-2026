# AI log: під час виконання завдання я спочатку неправильно організувала перевірку книжок на дублікати
# порівнювала назву нової книжки зі списком словників неправильно, тому перевірка не працювала
# помітила під час тестування й зрозуміла, що потрібно порівнювати значення поля "title"
# нової книжки зі значенням "title" кожної книжки
# також вдосконалила функцію "add_book()", щоб вона могла приймати кілька книжок одночасно та перевіряти кожну

import json


def load(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{path}' was not found")



def save(path, records):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def add_book(list_data, new_data):
    for book in new_data:
        found = False

        for book_in_list in list_data:
            if book["title"] == book_in_list["title"]:
                found = True
                break

        if not found:
            list_data.append(book)

    return list_data


def list_books(records):
    for book in records:
        print(book["title"])


def remove_book(records, title):
    for index, book in enumerate(records):
        if book["title"] == title:
            records.pop(index)
            return (f"Book {title} deleted successfully")
    return f"Book {title} not found"

records = load("my_book.json")
list_books(records)

new_data = [

{
    "title": "Atomic Habits",
    "author": "James Clear",
    "status": "to read"
},
  {
    "title": "The Poppy War",
    "author": "R. F. Kuang",
    "status": "to read"
  },
    {
        "title": "Automate the Boring Stuff with Python",
        "author": "Al Sweigart",
        "status": "to read"
    }
]
add_book(records, new_data)

print("_" * 40)
list_books(records)

print(remove_book(records, "Death Kaleidoscope"))
save("my_book.json", records)


