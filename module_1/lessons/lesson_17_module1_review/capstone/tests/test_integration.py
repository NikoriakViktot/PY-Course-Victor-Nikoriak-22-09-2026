"""Уся система разом: сесія адміністратора через app.py."""
import contextlib
import io
import os
import shutil
import tempfile

import app

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION = [
    ("import kasa_2024_07.txt", 0, "Імпортовано: 4, пропущено: 5"),
    ("add-delivery 1 Оболонь 230 D-3", 0, "Доставка №1: Оболонь, 230 грн, водій D-3"),
    ("add-delivery 2 Поділ 180 D-1", 0, "Доставка №2: Поділ, 180 грн, водій D-1"),
    ("add-delivery 3 Оболонь 270 D-3", 0, "Доставка №3: Оболонь, 270 грн, водій D-3"),
    ("add-delivery 3 Печерськ 150 D-2", 1, "Помилка: замовлення №3 вже має доставку"),
    ("add-delivery 9 Поділ 100 D-1", 1, "Помилка: замовлення №9 немає"),
    ("find 3", 0, "№3 2024-07-20 20:15, 980.00 грн, гостей: 4, доставка: Оболонь (270 грн)"),
    ("find три", 1, "Помилка: номер замовлення має бути цілим числом, а маємо три"),
    ("report", 0, "Замовлень: 4, з доставкою: 3\n"
                  "Кафе: 3040.00 грн, середній чек 760.00 грн, найкращий день: нд\n"
                  "Таксі: 680 грн за доставки\n"
                  "Райони: Оболонь 2, Поділ 1\n"
                  "Разом: 3720.00 грн"),
    ("voucher 500", 0, "Ваучер 500 грн: доставки замовлень №1 і №3"),
    ("import no_such_file.txt", 1, "Помилка: немає файлу no_such_file.txt"),
]


def test_session():
    with tempfile.TemporaryDirectory() as folder:
        shutil.copy(os.path.join(PROJECT, "kasa_2024_07.txt"), folder)
        old = os.getcwd()
        os.chdir(folder)
        try:
            for command, code, expected in SESSION:
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    result = app.main(["app.py"] + command.split())
                text = out.getvalue().rstrip("\n")
                if command.startswith("import kasa"):
                    text = text.splitlines()[0]
                assert (result, text) == (code, expected), f"\n$ python app.py {command}\n{text}"
        finally:
            os.chdir(old)
