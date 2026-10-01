#Task 3

# AI log: not used

message = input("Введите сообщение: ")

i,chars_count,digits_count,punctuations_count = 0, 0, 0, 0
while i < len(message):
    if message[i].isalpha():
        chars_count+=1
    elif message[i].isdigit():
        digits_count+=1
    elif message[i] != " ":
        punctuations_count+=1

    i+=1


print("Chars:", chars_count, "Digits:", digits_count, "Punctuations:", punctuations_count)


# Hi,2026! ожидаемый результат
# Chars: 2 Digital:4 Punctuations: 2
