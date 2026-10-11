# AI log: використано для перекладу завдання та пояснення що саме потрібно зробити в завданні

def make_country(name, capital):
    return {'name': name, 'capital': capital}

print(make_country('Poland', 'Warsaw'))
print(make_country('Warsaw', 'Poland'))
#переплутані значення, не вірний порядок аргументів
print(make_country(name='France', capital='Paris'))
print(make_country(capital='Paris', name='France'))
#друкує правильно - тому що в іменних параметрах порядок аргументів не важливий
print(make_country("Kyiv", "Ukraine"))
# поверне {'name': 'Kyiv', 'capital': 'Ukraine'} бо порядок аргументів (не іменних) - важливий