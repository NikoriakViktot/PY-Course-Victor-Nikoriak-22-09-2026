from orders import RawOrder, generate_raw_orders, to_order

raw = RawOrder(540.0, 50.0, 2, datetime(2024, 7, 19, 18, 30))
print(to_order(raw))

raw_orders = generate_raw_orders(2000, seed=42)
print(len(raw_orders))
print(raw_orders[0])
