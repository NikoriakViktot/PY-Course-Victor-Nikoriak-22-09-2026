"""Перевірка частин фінального проєкту.

    python check.py 3      — тести частини 3
    python check.py all    — усі частини + сесія адміністратора через app.py
    python check.py        — коротка таблиця: яка частина готова
"""
import importlib
import sys
import traceback

TASKS = {
    1: "rules.py — день тижня і прийом їжі",
    2: "parsing.py — розбір замовлення і доставки",
    3: "storage.py — збереження стану в JSON",
    4: "cafe.py — статистика кафе",
    5: "taxi.py — індекс, райони, ваучер",
    6: "commands.py — команди системи",
}


def run_tests(module_name, verbose=True):
    """Запускає test_*-функції модуля. Повертає (пройдено, усього, чи всі готові)."""
    module = importlib.import_module(f"tests.{module_name}")
    tests = [(name, func) for name, func in vars(module).items() if name.startswith("test_")]
    passed = 0
    ready = True
    for name, func in tests:
        try:
            func()
        except NotImplementedError as error:
            ready = False
            status = f"ще не зроблено — {error}"
        except AssertionError as error:
            status = f"НЕ ПРОЙДЕНО {error}"
        except Exception as error:                       # чужий баг показуємо, а не ховаємо
            frame = traceback.extract_tb(error.__traceback__)[-1]
            status = f"ПОМИЛКА {type(error).__name__}: {error} ({frame.filename.split('/')[-1]}, рядок {frame.lineno})"
        else:
            passed += 1
            status = "OK"
        if verbose:
            print(f"  {name}: {status}")
    return passed, len(tests), ready


def check_task(number):
    print(f"Частина {number}: {TASKS[number]}")
    passed, total, _ = run_tests(f"test_part{number}")
    return passed == total


def main(args):
    if len(args) == 2 and args[1].isdigit() and int(args[1]) in TASKS:
        return 0 if check_task(int(args[1])) else 1
    if len(args) == 2 and args[1] == "all":
        results = [check_task(number) for number in TASKS]
        print("Сесія адміністратора: уся система разом")
        passed, total, _ = run_tests("test_integration")
        ok = all(results) and passed == total
        print("✅ Система працює!" if ok else "❌ Система ще не працює — дивись рядки вище")
        return 0 if ok else 1
    if len(args) == 1:
        for number, title in TASKS.items():
            passed, total, ready = run_tests(f"test_part{number}", verbose=False)
            mark = "✅" if passed == total else ("⏳" if not ready else "❌")
            print(f"{mark} {number}. {title}: {passed}/{total}")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
