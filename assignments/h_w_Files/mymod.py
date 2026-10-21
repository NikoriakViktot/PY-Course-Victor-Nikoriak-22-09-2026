def count_lines(name):
    with open(name, 'r', encoding="utf-8") as file:
        lines = file.readlines()
        return len(lines)

def count_chars(name):
    with open(name, "r", encoding="utf-8") as file:
        chars = file.read()
        return len(chars)


if __name__ == "__main__":
    print(count_lines("assignments/h_w_Files/mymod.py"))
    print(count_chars("assignments/h_w_Files/mymod.py"))

# wc output: 15     458 assignments/h_w_Files/mymod.py