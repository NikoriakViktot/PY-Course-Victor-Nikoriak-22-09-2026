# AI log:
# мені було складно зрозуміти, як поєднати всі інші функції в одну програму (тому розбиралися з функцією main)
# також AI допоміг мені розібратися з помилками під час запуску та з детальним розумінням самого завдання
import sys
import json

def load_phonebook(filename):
    try:
        with open(filename, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        return data

    except FileNotFoundError:
        raise FileNotFoundError(f"File '{filename}' was not found")


def search_first_name(phonebook, name):
    for contact in phonebook:
        first_name = contact["first_name"]
        if first_name == name:
            return (f"{contact}")

    return f"Contact not found '{name}'"


def search_last_name(phonebook, name):
    for contact in phonebook:
        last_name = contact["last_name"]
        if last_name == name:
            return f"{contact}"

    return f"Contact not found '{name}'"


def search_by_phone(phonebook, phone_contact):
    for contact in phonebook:
        phone = contact["phone"]
        if phone == phone_contact:
            return f"{contact}"

    return f"Contact not found '{phone_contact}'"


def search_by_city(phonebook, city_contact):
    for contact in phonebook:
        city = contact["city"]
        if city == city_contact:
            return f"{contact}"

    return f"Contact not found '{city_contact}'"

def search_by_state(phonebook, state_contact):
    for contact in phonebook:
        state = contact["state"]
        if state == state_contact:
            return f"{contact}"

    return f"Contact not found '{state_contact}'"

# після видалення Ann у файлі залишаться інші контакти
def delete_by_phone(phonebook, search_phone):
    for index, contact in enumerate(phonebook):
        if contact["phone"] == search_phone:
            phonebook.pop(index)
            return f"Contact with phone '{search_phone}' deleted successfully"
    return f"Contact with phone '{search_phone}' not found"

def update_by_phone(phonebook, search_phone, field, new_value):
    for index, contact in enumerate(phonebook):
        if contact["phone"] == search_phone:
            contact[field] = new_value
            return f"Contact with phone '{search_phone}' update successfully"
    return f"Contact with phone '{search_phone}' not found"

def save_phonebook(filename, phonebook):
    with open(filename, "w", encoding="utf-8") as json_f:
        json.dump(phonebook, json_f, indent=2)


def main():
    filename = sys.argv[1]
    phonebook = load_phonebook(filename)
    while True:
        choice = int(input(
            "Choose what you want to do:\n"
            "1 - Search by first name\n"
            "2 - Search by last name\n"
            "3 - Search by phone\n"
            "4 - Search by city\n"
            "5 - Search by state\n"
            "6 - Delete contact\n"
            "7 - Update contact\n"
            "0 - Exit\n"
            "Your choice: "
        ))
        if choice == 1:
            name = input("Enter name: ")
            print(search_first_name(phonebook, name))
        elif choice == 2:
            last_name = input("Enter last name: ")
            print(search_last_name(phonebook, last_name))
        elif choice == 3:
            phone = input("Enter phone: ")
            print(search_by_phone(phonebook, phone))
        elif choice == 4:
            city = input("Enter city: ")
            print(search_by_city(phonebook, city))
        elif choice == 5:
            state = input("Enter state: ")
            print(search_by_state(phonebook, state))
        elif choice == 6:
            phone = input("Enter phone to delete: ")
            print(delete_by_phone(phonebook, phone))
        elif choice == 7:
            phone = input("Enter phone to update: ")
            field = input("Enter field to update: ")
            new_value = input("Enter new value: ")
            print(update_by_phone(phonebook, phone, field, new_value))
        elif choice == 0:
            save_phonebook(filename, phonebook)
            break

        else:
            print("Select an existing option")

main()