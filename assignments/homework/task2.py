# AI log: none
def make_country(name, capital):
    return {"name": name,"capital": capital}


print(make_country("Ukraine", "Kyiv" ))
print(make_country(capital= "Kyiv", name= "Ukraine" ))

# Виведе {'name': 'Kyiv', 'capital': 'Ukraine'}, тому що аргументи вказані позиційно
print(make_country("Kyiv", "Ukraine"))