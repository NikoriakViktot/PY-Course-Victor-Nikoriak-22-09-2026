# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні,
# також для допомоги з розумінням помилок в моєму коді
# файл myfile.txt створився не біля папки із скриптом, який його створив,
# а в тій папці це актуально був запущений код з термілалу

def create_file(file_name="myfile.txt"):
    f = open(file_name, "w", encoding="utf-8")
    f.write("Hello file world!")
    f.close()


def read_file(file_name="myfile.txt"):
    f = open(file_name, "r", encoding="utf-8")
    content = f.read()
    f.close()
    return content


create_file()
print(read_file())

def create_file_v2(file_name="myfile.txt"):
    with open(file_name, "w", encoding="utf-8") as f:
      f.write("Hello file world!")

def read_file_v2(file_name="myfile.txt"):
    with open(file_name, "r", encoding="utf-8") as f:
      return f.read()

create_file_v2()
print(read_file_v2())
