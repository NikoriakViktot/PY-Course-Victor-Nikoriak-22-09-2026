# AI log: використовувала для пояснення методу написання через %
name = "Lena"
day = "Sunday"

print(f"Good day {name}! {day} is a perfect day to learn some python.")

text = "Good day {}! {} is a perfect day to learn some python."
print(text.format(name, day))

print("Good day %s! %s is a perfect day to learn some python." %(name, day))

