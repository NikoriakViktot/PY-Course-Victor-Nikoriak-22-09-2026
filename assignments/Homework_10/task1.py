# 1. print(get_greeter()) виведе: <function get_greeter.<locals>.greet at 0x...>
# 2. print(get_greeter()("Olena")) виведе: Hello, Olena!

def get_greeter():
    def greet(name):
        return f"Hello, {name}"
    return greet


print(get_greeter())
print(get_greeter()("Olena"))

# AI log: not used
