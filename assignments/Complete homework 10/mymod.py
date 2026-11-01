# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні,
# також для допомоги з розумінням помилок в моєму коді
# доповнення домашки з уроку 13

def count_lines(lines):
    return len(lines)

def count_chars(lines):
    total = 0
    for line in lines:
        total += len(line)
    return total

def test(lines):
    print("Lines:", count_lines(lines))
    print("Chars:", count_chars(lines))

if __name__ == "__main__":
    example = ["Hello", "my name is Lena", "I learn Python"]
    test(example)

# count_lines і count_chars це функції із 13-го заняття,
# тому нові версії названо count_lines_new і count_chars_new

def count_lines_new(file_name):
    with open(file_name, encoding="utf-8") as f:
        return len(f.readlines())

def count_chars_new(file_name):
    with open(file_name, encoding="utf-8") as f:
        return len(f.read())

if __name__ == "__main__":
    print("Lines_new:", count_lines_new("mymod.py"))
    print("Chars_new:", count_chars_new("mymod.py"))

# мій результат: Lines_new: 34, Chars_new: 988
# wc -l -c mymod.py: 34 1146 mymod.py
# перевірка через wc -l -c дала більше байтів, тому що порахувала кожен знак кирилиці як 2 байти
# len() порахувала кількість знаків у файлі