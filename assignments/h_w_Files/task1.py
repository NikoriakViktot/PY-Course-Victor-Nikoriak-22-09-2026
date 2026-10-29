# AI log: запитувала, що означає команда wc -l -c у терміналі
def create_file(file_name="myfile.txt"):
    file = open(file_name, "w", encoding="utf-8")
    try:
        file.write("Hello file world!")
    finally:
        file.close()


def read_file(file_name="myfile.txt"):
    file =  open(file_name, "r", encoding="utf-8")
    try:
        text = file.read()
    finally:
        file.close()
    return text


create_file("myfile.txt")
print(read_file("myfile.txt"))


def create_file_v2(file_name="myfile.txt"):
    with open(file_name, "w", encoding="utf-8") as file:
        file.write("Hello file world! ")



def read_file_v2(file_name="myfile.txt"):
    with open(file_name, "r", encoding="utf-8") as file:
        text = file.read()
        return text

create_file_v2("myfile.txt")
print(read_file_v2("myfile.txt"))

# Файл зʼявиться в папці файлу який ми запускаємо для створення та перезапису
create_file("data/myfile.txt")
# якщо вказати шлях data/myfile.txt то файл створиться в папці data, якщо ця папка вже існує