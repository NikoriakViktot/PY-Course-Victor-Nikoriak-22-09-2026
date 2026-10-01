text = input("input your text: ")
chars_count = 0
digits_count = 0
punctuations_count = 0
i = 0

while i < len(text):
    if text[i].isdigit():
        digits_count += 1
    elif text[i].isalpha():
        chars_count += 1
    elif text[i] == " ":
        pass
    else:
        punctuations_count += 1

    i += 1

print("Chars:", chars_count, "Digits:", digits_count, "Punctuations:", punctuations_count)
# Expected: Chars: 2 Digits: 4 Punctuations: 2