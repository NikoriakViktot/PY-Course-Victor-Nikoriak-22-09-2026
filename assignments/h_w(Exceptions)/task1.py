# AI log: використала, щоб розібратися з роботою raise
# Спочатку функція oops викликає IndexError, а функція an_func
# перехоплює цю помилку, бо ми вказали в except IndexError
# далі ми змінюємо IndexError на KeyError, в except залишаємо IndexError
# KeyError він не перехоплює помилку
# тому KeyError залишається необробленою помилкою і програма завершується
def oops():
    raise KeyError

def an_func():
    try:
        oops()
    except IndexError:
        print(f"Перехопив IndexError")

an_func()