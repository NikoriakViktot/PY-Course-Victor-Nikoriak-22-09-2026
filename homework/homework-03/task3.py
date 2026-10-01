# AI log: використала, щоб нагадати команди для перевірки символів у рядку
# (.isalpha(), .isdigit(), .isspace());
sentence = input("Enter string: ")
chars_count = 0
digits_count = 0
punctuations_count = 0
n = 0
while n < len(sentence):

    if sentence[n].isalpha():
        chars_count += 1

    if sentence[n].isdigit():
        digits_count += 1

    if not sentence[n].isalpha() and not sentence[n].isdigit() and not sentence[n].isspace():
        punctuations_count += 1
    n += 1

print("Chars:", chars_count, "Digits:", digits_count, "Punctuations:", punctuations_count)