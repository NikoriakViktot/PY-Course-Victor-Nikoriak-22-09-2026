def make_country(country_name, capital):
    my_dict = {}
    my_dict['name'] = country_name
    my_dict['capital'] = capital
    return my_dict


# Функція застосує до параметрів такі аргументи
# counntry_name = 'Kyiv'
# capital = 'Ukraine'
print(make_country('Kyiv', 'Ukraine'))

print(make_country('Ukraine', 'Kyiv'))

print(make_country(capital='Kyiv', country_name='Ukraine'))

# AI log: самостійно реалізував створення словника та виклики функції.
# За підказкою ментора(AI) виправив ключ на 'name' згідно з умовою,
# прибрав побічний ефект у вигляді print() з тіла функції та повертув сформований словник через return.
