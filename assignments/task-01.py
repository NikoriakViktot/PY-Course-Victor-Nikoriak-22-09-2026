# Task 1

# AI log: not used

def get_greeter(greeting):
    def get_greeting(name):
        return f'{greeting} {name}'
    return get_greeting



print(get_greeter("Hello"))
print(get_greeter("Hello")("Olena"))

# первый вариант вывода напечатает нам обьект функции, если говорить о втором то мы он напечатает уже Helo Olena
# второй это уже полноценый вызов функции