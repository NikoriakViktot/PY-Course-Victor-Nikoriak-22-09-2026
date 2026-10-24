# AI log: none
def find_square():
    try:
        a = int(input("Enter number: "))
        b = int(input("Enter number: "))
        return round((a ** 2 / b), 2)
    except ZeroDivisionError:
        return "ZeroDivisionError"
    except ValueError:
        return "ValueError"

print(find_square())
