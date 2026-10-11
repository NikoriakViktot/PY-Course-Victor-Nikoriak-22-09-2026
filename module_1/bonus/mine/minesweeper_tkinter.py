"""Навчальний «Сапер»: Tkinter, функції та покрокові повідомлення.

Запуск у терміналі: python minesweeper_tkinter.py
Перевірка Tkinter: python -m tkinter

Вікно показує гру, термінал пояснює виконані дії українською.
Навчальні print() розкривають координати мін — це режим розбору коду!
У main() можна задати size = 3 та bomb_count = 1 для короткого прикладу.

Читати код зручно в такому порядку:
main → create_state → create_interface → start_new_game → open_cell.
Функції визначені раніше, ніж main їх викликає.

Без класів, прапорців, автоматичного відкриття нулів і захисту першого ходу.
"""

# random вибирає випадкові координати мін.
import random
# tk — коротке ім’я модуля для створення вікон і кнопок.
import tkinter as tk
# partial готує функцію до майбутнього виклику з певними аргументами.
from functools import partial


def create_bombs(size, bomb_count):
    """Отримати розмір і кількість мін; повернути множину координат."""
    print("\n[МІНИ] Створюємо мін:", bomb_count, "на полі", size, "×", size)
    # set() створює порожню множину; {} створило б словник.
    bombs = set()
    # Повторені координати не збільшують множину, тому контролюємо її розмір.
    while len(bombs) < bomb_count:
        # Обидві межі randint включено: для size=8 можливі числа 0–7.
        row = random.randint(0, size - 1)
        col = random.randint(0, size - 1)
        position = (row, col)  # Кортеж — адреса однієї клітинки.
        print("[МІНИ] Випадково обрано:", position)
        if position in bombs:
            print("[МІНИ] Тут уже є міна. Кількість не зміниться.")
        # add додає елемент; повторний елемент множина не дублює.
        bombs.add(position)
        print("[МІНИ] Зараз унікальних мін:", len(bombs))
    print("[МІНИ] Готові координати:", sorted(bombs))
    # return передає створену множину коду, який викликав функцію.
    return bombs


def count_nearby_bombs(row, col, bombs):
    """Порахувати міни навколо ОДНІЄЇ клітинки."""
    # dr змінює рядок, dc — стовпець. Центр (0, 0) не перевіряємо.
    # -1 у рядку — вгору; +1 — вниз. У стовпці: ліворуч і праворуч.
    directions = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1),
    ]
    count = 0  # Для кожного виклику починаємо підрахунок заново.
    print("  [СУСІДИ] Перевіряємо оточення клітинки:", (row, col))
    # Розпаковуємо кожну пару зміщень у дві змінні.
    for dr, dc in directions:
        neighbor = (row + dr, col + dc)
        # Це перевірка множини, а не індексування списку.
        # Координат за межами поля у bombs немає: результат буде False.
        if neighbor in bombs:
            count += 1
            print("    Сусід", neighbor, "— МІНА. Лічильник:", count)
        else:
            print("    Сусід", neighbor, "— міни немає або координати поза полем.")
    print("  [СУСІДИ] Результат для", (row, col), ":", count)
    return count


def calculate_counts(size, bombs):
    """Обійти ВСЕ поле; зберегти підказки для безпечних клітинок."""
    print("\n[ПІДКАЗКИ] Готуємо словник: координати → кількість сусідніх мін.")
    counts = {}
    for row in range(size):  # Послідовно вибираємо рядки.
        for col in range(size):  # У кожному рядку перебираємо стовпці.
            if (row, col) in bombs:
                print("[ПІДКАЗКИ]", (row, col), "— міна, пропускаємо.")
                # continue переходить до наступного стовпця цього циклу.
                continue
            # Деталі підрахунку доручаємо окремій функції.
            count = count_nearby_bombs(row, col, bombs)
            counts[(row, col)] = count
            print("[ПІДКАЗКИ] Записано counts[", (row, col), "] =", count)
    print("[ПІДКАЗКИ] Підготовлено безпечних клітинок:", len(counts))
    return counts


def create_state(size, bomb_count):
    """Створити спільний словник даних, який передаватимемо функціям."""
    print("[СТАН] Створюємо словник game.")
    # Поки що це заготовка: міни додасть start_new_game, віджети — create_interface.
    return {
        "size": size,           # Кількість рядків і стовпців.
        "bomb_count": bomb_count,  # Потрібна кількість мін.
        "bombs": set(),         # Координати мін.
        "counts": {},           # Підказки безпечних клітинок.
        "opened": set(),        # Координати вже відкритих клітинок.
        "finished": False,      # Чи завершилася гра?
        "buttons": [],          # Список рядків із кнопками Tkinter.
        "status": None,         # Пізніше тут буде віджет текстового напису.
    }


def update_status(game):
    """Порахувати залишок безпечних клітинок і змінити напис у вікні."""
    safe_cells = game["size"] * game["size"] - game["bomb_count"]
    remaining = safe_cells - len(game["opened"])
    print("[СТАТУС] Усього безпечних:", safe_cells,
          "| Відкрито:", len(game["opened"]), "| Залишилося:", remaining)
    # config змінює властивості вже створеного віджета.
    game["status"].config(text="Безпечних клітинок залишилося: " + str(remaining))


def show_cell(game, row, col):
    """Замінити крапку на підказку та вимкнути відкриту кнопку."""
    count = game["counts"][(row, col)]  # Беремо готове число зі словника.
    print("[ВІДОБРАЖЕННЯ] Клітинка", (row, col), "покаже число", count)
    # Спочатку вибираємо рядок кнопок, потім кнопку в цьому рядку.
    game["buttons"][row][col].config(
        text=str(count),              # Перетворюємо число на текст кнопки.
        state=tk.DISABLED,            # Забороняємо повторне натискання.
        relief=tk.SUNKEN,             # Вигляд натиснутої кнопки.
        bg="#e2e8f0",                # Колір тла.
        disabledforeground="#0f172a",  # Колір тексту вимкненої кнопки.
    )


def finish_game(game, won):
    """Завершити гру: won=True — перемога, won=False — поразка."""
    game["finished"] = True  # Змінюємо стан, а не лише повідомлення.
    if won:
        message = "Перемога! Усі безпечні клітинки відкрито."
    else:
        message = "Міна! Гру завершено. Спробуйте ще раз."
    print("\n[ЗАВЕРШЕННЯ]", message)
    game["status"].config(text=message)

    # Відкриваємо розташування всіх мін незалежно від результату гри.
    for row, col in game["bombs"]:
        print("[ЗАВЕРШЕННЯ] Показуємо міну:", (row, col))
        game["buttons"][row][col].config(
            text="*", bg="#fecaca", disabledforeground="#991b1b"
        )
    # Два цикли потрібні для проходу по списку рядків із кнопками.
    for button_row in game["buttons"]:
        for button in button_row:
            button.config(state=tk.DISABLED)
    print("[ЗАВЕРШЕННЯ] Усі кнопки поля вимкнено. «Нова гра» доступна.")


def open_cell(game, row, col):
    """Виконати ОДИН хід після натискання кнопки."""
    print("\n[ХІД] Натиснуто клітинку:", (row, col))
    # Додаткова перевірка стану захищає і прямі виклики функції з коду.
    if game["finished"]:
        print("[ХІД] Гра вже завершена. Виходимо через return.")
        return
    if (row, col) in game["opened"]:
        print("[ХІД] Клітинку вже відкрито. Нічого не змінюємо.")
        return

    print("[ХІД] Перевіряємо, чи є тут міна.")
    if (row, col) in game["bombs"]:
        print("[ХІД] Знайдено міну — викликаємо finish_game(game, False).")
        finish_game(game, False)
        return  # Без цього програма спробувала б відкрити міну як безпечну.

    # Множина opened замінює окремий лічильник: його дає len(opened).
    game["opened"].add((row, col))
    print("[ХІД] Безпечно. Додали координати до opened:", sorted(game["opened"]))
    show_cell(game, row, col)
    update_status(game)

    safe_cells = game["size"] * game["size"] - game["bomb_count"]
    print("[ХІД] Перевірка перемоги:", len(game["opened"]), "із", safe_cells)
    if len(game["opened"]) == safe_cells:
        finish_game(game, True)
    else:
        print("[ХІД] Гра триває. Повертаємо керування Tkinter.")


def start_new_game(game):
    """Оновити дані гри та очистити існуючі кнопки без нового вікна."""
    print("\n[НОВА ГРА] Починаємо підготовку.")
    game["bombs"] = create_bombs(game["size"], game["bomb_count"])
    game["counts"] = calculate_counts(game["size"], game["bombs"])
    # Прибираємо відкриті клітинки попередньої гри та скидаємо ознаку завершення.
    game["opened"] = set()
    game["finished"] = False
    print("[НОВА ГРА] opened порожня; finished = False.")

    # Кнопки вже існують: змінюємо їхній вигляд і знову дозволяємо натискання.
    for button_row in game["buttons"]:
        for button in button_row:
            button.config(
                text=".", state=tk.NORMAL, relief=tk.RAISED,
                bg="#f1f5f9", fg="#0f172a", disabledforeground="#0f172a",
            )
    print("[НОВА ГРА] Усі клітинки знову закриті й доступні.")
    update_status(game)
    print("[НОВА ГРА] Готово. Оберіть клітинку у вікні.")


def create_interface(window, game):
    """Створити віджети й пов’язати кнопки з функціями-обробниками."""
    print("\n[ІНТЕРФЕЙС] Задаємо заголовок і фіксуємо розмір вікна.")
    window.title("Сапер — Tkinter і функції")
    window.resizable(False, False)

    # Label показує текст. pack розміщує віджет у батьківському контейнері.
    # Створення віджета та його розміщення — окремі дії.
    title = tk.Label(window, text="Сапер", font=("Arial", 20, "bold"))
    title.pack(padx=16, pady=(14, 4))  # Зовнішні відступи по горизонталі та вертикалі.
    instruction = tk.Label(window, text="Відкрийте всі клітинки без мін.")
    instruction.pack(padx=16, pady=(0, 8))

    # Посилання на напис зберігаємо, щоб інші функції могли змінювати його текст.
    game["status"] = tk.Label(window, text="", font=("Arial", 11))
    game["status"].pack(padx=16, pady=(0, 8))
    print("[ІНТЕРФЕЙС] Створено заголовок, інструкцію та напис статусу.")

    # Frame — контейнер для таблиці кнопок.
    board_frame = tk.Frame(window)
    board_frame.pack(padx=16, pady=4)
    # Усередині window використовуємо pack, усередині board_frame — grid.
    # Не змішуємо ці способи для дочірніх віджетів одного контейнера.
    for col in range(game["size"]):
        tk.Label(board_frame, text=str(col)).grid(row=0, column=col + 1)

    for row in range(game["size"]):
        tk.Label(board_frame, text=str(row), width=2).grid(row=row + 1, column=0)
        button_row = []  # Кожен рядок має власний новий список.
        for col in range(game["size"]):
            # partial НЕ відкриває клітинку зараз.
            # Він створює виклик «на потім» із координатами саме цієї кнопки.
            # command=open_cell(game, row, col) було б помилкою:
            # функція виконалася б одразу під час створення кнопки.
            handler = partial(open_cell, game, row, col)
            button = tk.Button(
                board_frame, text=".", width=3, height=1,
                font=("Arial", 16, "bold"), command=handler,
            )
            # +1 залишає нульовий рядок і стовпець для підписів координат.
            button.grid(row=row + 1, column=col + 1, padx=1, pady=1)
            button_row.append(button)
            print("[ІНТЕРФЕЙС] Створено кнопку", (row, col),
                  "→ натискання викличе open_cell з цими координатами.")
        game["buttons"].append(button_row)

    # Ця кнопка отримує той самий словник game й перезапускає гру.
    restart = tk.Button(
        window, text="Нова гра", font=("Arial", 12),
        command=partial(start_new_game, game),
    )
    restart.pack(pady=(10, 14))
    print("[ІНТЕРФЕЙС] Кнопку «Нова гра» створено.")


def main():
    """Організувати запуск: налаштування → дані → вікно → події."""
    print("[ЗАПУСК] Починаємо виконання main().")
    # Для короткого покрокового розбору поставте 3 і 1.
    size = 10
    bomb_count = 10
    # У цьому навчальному прикладі задаємо цілі числа безпосередньо в коді.
    if size <= 0 or bomb_count < 0 or bomb_count >= size * size:
        print("[ПОМИЛКА] Потрібно: size > 0 та 0 <= bomb_count < size * size.")
        return

    game = create_state(size, bomb_count)
    # Створюємо головне вікно. Потрібне середовище з графічним робочим столом.
    window = tk.Tk()
    print("[ЗАПУСК] Головне вікно створено.")
    create_interface(window, game)
    start_new_game(game)
    print("\n[ПОДІЇ] Запускаємо mainloop. Чекаємо натискань у вікні.")
    # Tkinter сам чекає події й викликає обробники. input() не потрібен.
    window.mainloop()
    # Цей рядок виконається після завершення циклу подій — закриття вікна.
    print("[ВИХІД] Вікно закрито. Програму завершено.")


# При прямому запуску файла __name__ дорівнює "__main__".
# При імпорті визначаться функції, але main автоматично не запуститься.
if __name__ == "__main__":
    main()
