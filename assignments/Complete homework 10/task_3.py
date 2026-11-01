# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні,
# також для допомоги з розумінням помилок в моєму коді, допомагав з написанням правильної функції

# під час введення міста я перемкнула розкладку посеред слова, і в запис потрапив кириличний символ який ось так �Rivne виглядав в терміналі
# під час збереження `json.dump` не зміг записати його в UTF-8 і впав з `UnicodeEncodeError`, файл залишився недописаним.
# розібрала цю помилку з AI агентом і додала перевірку: тепер текст спершу готується через json.dumps, перевіряється text.encode("utf-8"),
# і лише потім відкривається файл, тож у разі помилки він залишиться цілим.
# пізніше виявилося що при створенні імені Iryna я випадково знову написала Ш замість I,
# в терміналі я це видалила але python зберіг цей символ всерівно, довелося розбирати з агентом як це виправити
# довелося додати import readline та опції "Показати запис і попросити підтвердження"

# перед видаленням (+380634406677): видалить повність запис Kateryna Pavliuk, інші записи без змін
# Loaded 6 records - перед видаленням
# Loaded 5 records - після видалення

import json
import os
import sys
import readline


def load_book(file_name):
    if not os.path.exists(file_name):
        raise FileNotFoundError(f"Phonebook file '{file_name}' not found")
    with open(file_name, encoding="utf-8") as f:
        return json.load(f)


def save_book(file_name, book):
    text = json.dumps(book, ensure_ascii=False, indent=2)
    text.encode("utf-8")
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(text)


def print_records(records):
    if not records:
        print("Nothing found")
        return
    for r in records:
        print(f"{r['first']} {r['last']}, {r['phone']}, {r['city']}, {r['state']}")


def add_record(book):
    record = {
        "first": input("First name: "),
        "last": input("Last name: "),
        "phone": input("Phone: "),
        "city": input("City: "),
        "state": input("State: "),
    }
    print("You entered:")
    print_records([record])
    if input("Save? (y/n): ") == "y":
        book.append(record)
        print("Record added")
    else:
        print("Cancelled")


def search_full_name(book):
    first = input("First name: ")
    last = input("Last name: ")
    found = [r for r in book if r["first"] == first and r["last"] == last]
    print_records(found)

def search_first(book):
    first = input("First name: ")
    found = [r for r in book if r["first"] == first]
    print_records(found)


def search_last(book):
    last = input("Last name: ")
    found = [r for r in book if r["last"] == last]
    print_records(found)


def search_phone(book):
    phone = input("Phone: ")
    found = [r for r in book if r["phone"] == phone]
    print_records(found)

def search_place(book):
    place = input("City or state: ")
    found = [r for r in book if r["city"] == place or r["state"] == place]
    print_records(found)

def find_by_phone(book, phone):
    for r in book:
        if r["phone"] == phone:
            return r
    return None

def delete_record(book):
    phone = input("Phone of record to delete: ")
    record = find_by_phone(book, phone)
    if record is None:
        print("Not found")
        return
    print_records([record])
    if input("Delete? (y/n): ") == "y":
        book.remove(record)
        print("Record deleted")
    else:
        print("Cancelled")


def update_record(book):
    phone = input("Phone of record to update: ")
    record = find_by_phone(book, phone)
    if record is None:
        print("Not found")
        return
    print("Press Enter to keep the current value")
    for field in ["first", "last", "phone", "city", "state"]:
        new_value = input(f"{field} [{record[field]}]: ")
        if new_value:
            record[field] = new_value
    print("Record updated")

def main():
    if len(sys.argv) < 2:
        raise ValueError("Usage: python3 task_3.py book.json")
    file_name = sys.argv[1]
    book = load_book(file_name)
    print(f"Loaded {len(book)} records")

    while True:
        print("\n1 - add, 2 - full name, 3 - first name, 4 - last name, "
              "5 - phone, 6 - city/state, 7 - delete, 8 - update, 0 - exit")
        choice = input("Choose: ")
        if choice == "1":
            add_record(book)
        elif choice == "2":
            search_full_name(book)
        elif choice == "3":
            search_first(book)
        elif choice == "4":
            search_last(book)
        elif choice == "5":
            search_phone(book)
        elif choice == "6":
            search_place(book)
        elif choice == "7":
            delete_record(book)
        elif choice == "8":
            update_record(book)
        elif choice == "0":
            save_book(file_name, book)
            print("Saved. Bye!")
            break
        else:
            print("Unknown command")


if __name__ == "__main__":
    main()

# Передбачення перед видаленням (+380931112233):
#