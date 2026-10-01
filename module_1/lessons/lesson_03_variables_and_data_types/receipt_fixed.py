#Task 3

#AI log: None

#Error: raceback (most recent call last):
#   File "/Users/rostyslav/Documents/beetroot/PY-Course-Victor-Nikoriak-22-09-2026/module_1/lessons/lesson_02_first_steps_environment_setup/receipt_fixed.py", line 7, in <module>
#     print("Item: " + item + ", quantity: " + quantity)
#           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~~~
# TypeError: can only concatenate str (not "int") to str

name = "receipt"
item = "coffee"
price = 45.5
quantity = 3

item.upper()
print("Item: " + item + ", quantity: " + str(quantity))


total = price * quantity
print("Total: " + str(total) + " UAH")
print(f"Average: {total / quantity:.2f}")
