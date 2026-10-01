#Task 1
from pyexpat.errors import messages

# AI log: None

name= "Rostyslav"

day = "Saturday"


print(f"Good day {name}! {day} is a perfect day to learn some python")

#Сделанно с помощью Format


message = "Good day {}! {} is a perfect day to learn some python".format(name, day)

print(message)

# Сделанно с помощью %

message = "Good day %s! %s is a perfect day to learn some python"% (name,day)

print(message)