# create_slogan("BMW") поверне "* drinks * in his brand new *!"
# create_slogan("Pepsi") поверне "Pepsi drinks * in his brand new *!"

import functools

def stop_words(words: list):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            for word in words:
                    result = result.replace(word, '*')
            return result
        return wrapper
    return decorator

@stop_words(["pepsi", "BMW"])
def create_slogan(name: str) -> str:
    return f"{name} drinks pepsi in his brand new BMW!"

print(create_slogan("Steve") == "Steve drinks * in his brand new *!")

# AI log: Попросив допомогти із тим як зрозуміти логіку завдання, код написав сам