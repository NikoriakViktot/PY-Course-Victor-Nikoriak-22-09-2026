# Ожидаемый результат Hi- 2 буквы ,2026 -4 цифры , ,!-  2 знака
text = input()
chars_count = 0
digits_count = 0
punctuations_count =0
index = 0
while index <len(text):
    char =text[index]

    if char.isalpha():
        chars_count = chars_count + 1

    elif char.isdigit():
        digits_count = digits_count + 1

    elif char!=" ":
        punctuations_count = punctuations_count + 1
    index = index + 1
print("Chars:", chars_count, "Digits:", digits_count, "Punctuations:", punctuations_count)
# AI log : с помощью Ai hfp,разбирал код и задание,большую часть логики пока не понял полносью))