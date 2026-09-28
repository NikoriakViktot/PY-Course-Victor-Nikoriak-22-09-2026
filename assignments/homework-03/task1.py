# AI log: none

# В фінальній версії я би використовував метод f-strings, бо він найбільш сучасний, простий і зрозуміліший.

name = 'Artem'
day = 'Monday'

# сучасний метод f-string
print(f"Good day {name}! {day} is a perfect day to learn some Python.")

# Extra task

# застарілий метод .format (замінює {} на наші змінні)
print("Good day {}! {} is a perfect day to learn some Python.".format(name, day))

# застарілий метод old style через % (замінює %s на наші змінні)
print("Good day %s! %s is a perfect day to learn some Python." % (name, day))
