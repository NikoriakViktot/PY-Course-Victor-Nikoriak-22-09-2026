def count_lines(lines):
    return len(lines)


def count_chars(lines):

    count = 0

    for line in lines:
        count += len(line)

    return count


def test(lines):

    count = count_lines(lines)
    print(f"Кількість рядків: {count}")

    count = count_chars(lines)
    print(f"Загальна кількість символів: {count}")


if __name__ == '__main__':
    test(["film: Transformers"])
