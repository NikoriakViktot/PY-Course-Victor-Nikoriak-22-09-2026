# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні, опрацьовуванні помилок в моєму коді

def get_greeter():
    def sey_hi(name):
        return f'Hello {name}!'
    return sey_hi
greeter = get_greeter()

print(greeter('Lena'))


print(get_greeter())
# видасть помилку, бо print показує "саму функцію"

print(get_greeter()("Olena"))
# Hello Olena! другі дужки спрацювали
