# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні,
# також для допомоги з розумінням помилок в моєму коді,
# також допомагав підказками з "склеюванням" до купи клаптиків коду
# так як код працював не коректно на початку, допомагав поправляти прогалини, підказував керунок виправлень коду
# допоміг придумати другу функцію перевірки

from functools import wraps
def string_arg_rules(max_length=1, contains=(), exclude=()):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
          for arg in args:
            if not isinstance(arg, str):
              raise TypeError("Arguments must be string")
            if len(arg) > max_length:
              raise ValueError(f"Argument {arg} is longer than {max_length}")
            for sub in contains:
                if sub not in arg:
                    raise ValueError(f"Arguments must contain {sub}")
            for sub in exclude:
                if sub in arg:
                    raise ValueError(f"Arguments must not contain {sub}")
          return func(*args, **kwargs)
        return wrapper
    return decorator


@string_arg_rules(max_length=15, contains=('05', '@'), exclude=("S", 's'))
def create_slogan(name):
    return f"{name} drinks pepsi in his brand new BMW!"

@string_arg_rules(max_length=10, contains=('.',), exclude=('!',))
def full_name(first, last):
    return f"{first} {last}"


if __name__ == "__main__":
  print(create_slogan('peter@05'))
  try:
    create_slogan('peter@06')
  except ValueError as e:
    print("ValueError:", e)
  try:
    create_slogan('Seter@05')
  except ValueError as e:
    print("ValueError:", e)


  print(full_name('A.', 'Smith.'))
  try:
    full_name('A.', 123)
  except TypeError as e:
    print("TypeError:", e)
  try:
    full_name('A.', 'Smithsonian.')
  except ValueError as e:
    print("ValueError:", e)

