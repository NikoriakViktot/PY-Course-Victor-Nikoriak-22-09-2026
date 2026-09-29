"""Перевірка задач команди.

    python check.py 3      — тести задачі 3 (чужі задачі замінено заглушками)
    python check.py all    — усі задачі + інтеграційний тест: чи працює проєкт після злиття
    python check.py        — коротка таблиця: яка задача готова
"""
import importlib
import sys
import traceback

TASKS = {
    1: "rules.py — день тижня і прийом їжі",
    2: "parsing.py — розбір рядка каси",
    3: "loading.py — читання файлу і всіх рядків",
    4: "stats.py — підрахунки за днями і прийомами їжі",
    5: "report.py — словник звіту",
    6: "output.py — JSON і текст звіту",
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
    print(f"Задача {number}: {TASKS[number]}")
    passed, total, _ = run_tests(f"test_task{number}")
    return passed == total


def main(args):
    if len(args) == 2 and args[1].isdigit() and int(args[1]) in TASKS:
        return 0 if check_task(int(args[1])) else 1
    if len(args) == 2 and args[1] == "all":
        results = [check_task(number) for number in TASKS]
        print("Інтеграційний тест: увесь проєкт разом")
        passed, total, _ = run_tests("test_integration")
        ok = all(results) and passed == total
        print("✅ Проєкт працює!" if ok else "❌ Проєкт ще не працює — дивись рядки вище")
        return 0 if ok else 1
    if len(args) == 1:
        for number, title in TASKS.items():
            passed, total, ready = run_tests(f"test_task{number}", verbose=False)
            mark = "✅" if passed == total else ("⏳" if not ready else "❌")
            print(f"{mark} {number}. {title}: {passed}/{total}")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
