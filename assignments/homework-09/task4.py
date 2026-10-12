# create_slogan('BMW') # поверне (* п’є * у своєму новенькому *!)
# create_slogan('Pepsi') # поверне (Pepsi п’є * у своєму новенькому *!)

def stop_words(words: list):

    def decorator(func):

        def wrapper(*args, **kwargs):

            result_text = func(*args, **kwargs)

            for word in words:
                result_text = result_text.replace(word, '*')

            return result_text

        return wrapper

    return decorator


@stop_words(['pepsi', 'BMW'])
def create_slogan(name: str) -> str:
    return f"{name} п’є pepsi у своєму новенькому BMW!"


assert create_slogan("Стів") == "Стів п’є * у своєму новенькому *!"

# AI log: Самостійно написав каркас декоратора з аргументами (3 рівні вкладеності).
# З ментором(AI) розібрав логіку незмінності рядків та використання методу .replace().
# Виправив помилку з відступами в циклі та проаналізував, як replace замінює абсолютно всі збіги в тексті, не зважаючи на контекст.
