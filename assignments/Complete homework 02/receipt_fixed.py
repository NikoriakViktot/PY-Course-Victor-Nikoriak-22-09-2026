#1. не вірно вказана змінна (str)
#2. не вірний виклик методу upper(), поза викликом print (або не присвоєно для нього нову змінну)
#3. int замість float
#4. str для total пропущено
#5. не знайшла
# AI log: не використовувала

x = "receipt"
item = "coffee"
price = "45.5"
quantity = 3
print("Item: " + item.upper() + ", quantity: " + str(quantity))
total = float(price) * quantity
print("Total: " + str(total) + " UAH")
print(f"Average: {total / quantity:.2f}")