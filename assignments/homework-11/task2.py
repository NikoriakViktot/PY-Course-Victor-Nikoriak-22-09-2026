# AI log: написав все сам, ментор(AI) допоміг придумати, як отримувати назву помилки через type(error).__name__, а не писати вручу

def m_operation():

    try:

        a = int(input("Введіть перше число: "))
        b = int(input("Введіть друге число: "))

        result = (a*a) / b

    except ValueError as error:
        print(f"Помилка ({type(error).__name__}): значення повинно бути числом")

    except ZeroDivisionError as error:
        print(f"Помилка ({type(error).__name__}): на нуль ділити не можна")

    else:
        return result


m_operation()
