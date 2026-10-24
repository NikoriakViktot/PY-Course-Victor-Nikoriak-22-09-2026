# AI log: за допомогою ментора розібрав причину PermissionError (спроба відкрити теку на запис).

# при запуску програми через (Run Code або через Run Python File) файл створюється в головній папці проектів
# з уроками(D:\VisualStudioProject\BeetRoot Academy\), а не в самій папці домашнього завдання(BeetRoot Academy\lesson 12 files\homework-12\task1)
# а коли запускаєш через термінал, файл створюється в папці з скриптом який запустив

def create_file(file_name='myfile.txt'):

    f = open(file_name, 'w', encoding='utf-8')

    f.write("Hello file world!")
    f.close()


def read_file(file_name='myfile.txt'):

    f = open(file_name, encoding='utf-8')

    print(f.read())
    f.close()


create_file()
read_file()


def create_file_v2(file_name='myfile.txt'):

    with open(file_name, 'w', encoding='utf-8') as f:
        f.write("Hello file world!")


def read_file_v2(file_name='myfile.txt'):

    with open(file_name, encoding='utf-8') as f:
        print(f.read())


create_file_v2()
read_file_v2()

# передавши назву папки, створився файл task1, поруч з скриптом який запускався:

# create_file_v2(file_name='task1')
# read_file_v2(file_name='task1')

# піднявшись на рівень вище, і спробувавши знову, отримав помилку: ( PermissionError: [Errno 13] Permission denied: 'task1' )
# для виправлення данної поимлки треба явно передати шлях до файлу через (r"lesson 12 files\homework-12\task1\myfile.txt")

# create_file_v2(file_name=r"lesson 12 files\homework-12\task1\myfile.txt")
# read_file_v2(file_name=r"lesson 12 files\homework-12\task1\myfile.txt")
