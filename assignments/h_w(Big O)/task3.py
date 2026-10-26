# AI log: використовувала детального пояснення завдання,
# розуміння де саме поставити ch.isupper() і ch.lower()
import sys
ALPHABET = "abcdefghijklmnopqrstuvwxyz"

def caesar(text, shift):
    if not isinstance(shift, int):
        raise TypeError("Shift must be an integer")
    result = ""
    for ch in text:
        upper = ch.isupper()
        ch = ch.lower()
        if ch in ALPHABET:
            position = (ALPHABET.index(ch) + shift) % 26
            char = ALPHABET[position]
            if upper:
                char = char.upper()
            result += char

        else:
            result += ch
    return result

# Складність функції crack - O(n)
# функція завжди перевіряє 26 варіантів розшифрування
# кожен варіант обробляє весь текст
def crack(text):
    for i in range(26):
        decoded = caesar(text, -i)
        print(f"Shift {i}: {decoded}")

print("1 - Encrypt")
print("2 - Decrypt")
print("3 - Exit")
print("4 - Crack")

choice = input("Choose an option: ")

try:
    if choice == "1":
        text = input("Enter text: ")
        shift = int(input("Enter shift: "))
        print(caesar(text, shift))
    elif choice == "2":
        text = input("Enter text: ")
        shift = int(input("Enter shift: "))
        print(caesar(text, -shift))
    elif choice == "3":
        print("Goodbye!")
        sys.exit()
    elif choice == "4":
        text = input("Enter text: ")
        crack(text)

except TypeError as t:
    print(t)
except ValueError as v:
    print('Shift must be a whole number.')


