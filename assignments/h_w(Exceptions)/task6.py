# попросила додати обробку помилок до функції get_balance()
# та пояснити, які винятки перехоплює запропонований код
class BalanceError(Exception):
    pass


def get_balance(balance):
    if balance < 0:
        raise BalanceError("Balance cannot be below zero")
    else:
        return balance

def check_balance(balance):
    try:
        get_balance(balance)
    except BalanceError as b:
        return f"Error: the balance cannot be negative {b}"
    else:
        return balance
    finally:
        print("Balance check completed.")

print(check_balance(-10))
print(check_balance(100))

# Ось варіант із доданою обробкою помилок:

#class BalanceError(Exception):
    #pass


# def get_balance(balance):
    # try:
        # if balance < 0:
            # raise BalanceError("Balance cannot be below zero")
        # return balance
   # except Exception as e:
        # print(f"An error occurred: {e}")
        # return None

# except Exception перехоплює всі помилки, наприклад TypeError і BalanceError
# якщо помилитися в назві змінної, обробник може приховати NameError і повернути None
# краще перехоплювати лише ті помилки, які ми можемо обробити