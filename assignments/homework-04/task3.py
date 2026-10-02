# AI log:
# - Сумнів: як обробити пробіли та розділові знаки без зависання циклу while.
# - Питав: чому виникали помилки IndexError, KeyboardInterrupt та некоректний підрахунок символів.
# - Допомога AI: перейшли від декількох окремих if до ланцюжка if/elif/else, прибрали continue,
#   замінили фіксовану довжину i <= 8 на len(word)

# word = "Hi, 2026"
word = input()

chars_count = 0
digits_count = 0
punctuations_count = 0

i = 0

while i < len(word):

    if word[i].isalpha():
        chars_count += 1
    elif word[i].isdigit():
        digits_count += 1
    elif word[i].isspace():
        # chars_count += 1
        pass
    else:
        punctuations_count += 1

    i += 1

print("Символів:", chars_count, "Цифр:", digits_count, "Розділових знаків:", punctuations_count)
