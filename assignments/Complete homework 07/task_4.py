# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні, опрацьовуванні помилок в моєму коді
def stop_words(words: list):
    def decorator(func):
        def wrapper(*args, **kwargs):
            text = func(*args, **kwargs)
            for word in words:
                text = text.replace(word, "*")
            return text
        return wrapper
    return decorator

@stop_words(['pepsi', 'BMW'])
def create_slogan(name: str) -> str:
    return f"{name} drinks pepsi in his brand new BMW!"

assert create_slogan("Steve") == "Steve drinks * in his brand new *!"


print(create_slogan("BMW"))
# * drinks * in his brand new *! бо replace замінює всі входження BMW
print(create_slogan("Pepsi"))
# Pepsi drinks * in his brand new *! бо replace розрізняє регістр