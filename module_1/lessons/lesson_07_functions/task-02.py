# Task 2

# AI log: not used

country = {}


def make_country(name, capital):
    country[name] = capital
    return country


make_country("Ukraine", "Kyiv")

print(country)

make_country(capital="New York", name="USA")

print(country)
