# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні, опрацьовуванні помилок в моєму коді

def _add(a, b):
  return a + b

def _sub(a, b):
  return a - b

def _mul(a, b):
  return a * b

def _div(a, b):
  return a / b

def _pow(a,b):
  return a ** b



def operation_mapper(operation):
    if operation == "+":
        return _add
    elif operation == "-":
        return _sub
    elif operation == "*":
        return _mul
    elif operation == "/":
        return _div
    elif operation == "**":
        return _pow
    else:
        return lambda a, b: None

print(operation_mapper("+")(1, 2))
#3
print(operation_mapper("/")(7, 2))
#3.5 - після ділення отримуємо float
print(operation_mapper("**")(2, 10))
#1024

#operation_mapper не є декоратором: він приймає не функцію, а рядок і обирає потрібну ф-цію
