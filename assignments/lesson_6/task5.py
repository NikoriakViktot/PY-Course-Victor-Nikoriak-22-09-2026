# card - словарь,потому что он хранит товар и его количество в формате ключ: значение.
cart = {}
stock = {
    "apple": 10,
    "break": 5,
    "milk": 8,
    "chesse": 4,
    "coffee": 6,
    "tea": 7,
}
prices = {
    "apple": 2.0,
    "break": 3.0,
    "milk": 2.5,
    "chesse": 5.0,
    "coffee": 8.0,
    "tea": 4.0,
}
while True:
    product =input("Enter product (or 'done'): ").lower()
    if product == "done":
        break
    if product not in stock:
        print("Product is not available.")
        continue
    quantity = int(input("Enter quantity: "))
    if quantity > stock[product]:
        print(f"Only {stock[produck]} available.")
        continue
    stock[product] -= quantity
    cart[product] = cart.get(product, 0) + quantity
print("\nReceipt")
total = 0
for product, quantity in cart.items():
    price = prices[product]
    cost = price * quantity
    total += cost
    print(f"{product}: {quantity} x ${price:.2f} = ${cost:.2f}")
print(f"Total: ${total:.2f}")
out_of_stock = [product for product, quantity in stock.items() if quantity ==0]
print("Out of stock:", out_of_stock)
# Al log :Ai помог со структурой программы,код написал и протестировал сам