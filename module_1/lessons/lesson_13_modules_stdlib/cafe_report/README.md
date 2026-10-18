# Звіт кафе з модулів — проєкт до уроку 13

Проєкт до [уроку 13 «Модулі та стандартна бібліотека»](../../../../docs/modules/m1/lesson_13.md). Звіт кафе з уроку 8, розкладений на чотири модулі й запущений з термінала. У ноутбуці [`note_lesson_13_modules_stdlib.ipynb`](../note_lesson_13_modules_stdlib.ipynb) студенти створюють ті самі модулі через `%%writefile` поруч, у одній теці. Тут кожен модуль уже лежить у своєму пакеті — так виглядає проєкт, що росте (розділи уроку [«Практика»](../../../../docs/modules/m1/lesson_13.md#practice) і [«Поглиблення: пакети»](../../../../docs/modules/m1/lesson_13.md#packages)).

## Запуск

```bash
cd module_1/lessons/lesson_13_modules_stdlib/cafe_report
python main.py 2024 7                # звіт за липень 2024
python -m reports.report             # перевірка модуля звіту на трьох тестових чеках
python -m tests.test_cafe_report     # усі перевірки (або: python -m pytest)
```

Усі команди — з теки `cafe_report/`. Модулі всередині пакетів запускають через `-m` і ім'я модуля: `python reports/report.py` впаде з `ModuleNotFoundError: No module named 'rules'`, бо тоді першою текою в `sys.path` стане `reports/`, а не `cafe_report/`.

Потрібна лише стандартна бібліотека. Чеки генеруються з фіксованим зерном (`seed=42`), тож звіт щоразу однаковий.

## Файли

```text
cafe_report/
├── main.py                  ← точка входу: python main.py 2024 7
├── rules/
│   ├── __init__.py
│   └── rules.py             ← модуль rules.rules
├── orders/
│   ├── __init__.py
│   └── orders.py            ← модуль orders.orders
├── reports/
│   ├── __init__.py
│   └── report.py            ← модуль reports.report
└── tests/
    ├── __init__.py
    └── test_cafe_report.py  ← модуль tests.test_cafe_report
```

| Модуль | Що всередині | Імпортує |
|---|---|---|
| `rules.rules` | `DAYS`, `MONTHS`, `day_from_timestamp`, `meal_type_from_hour` | нічого |
| `orders.orders` | `RawOrder`, `Order`, `generate_raw_orders`, `in_month`, `to_order` | `random`, `datetime`, `typing`, `rules.rules` |
| `reports.report` | `count_by_day`, `revenue_by_day`, `best_day`, `print_report` | `collections`, `rules.rules` |
| `main` | `main(args)`: аргументи командного рядка → звіт за місяць | `sys`, `calendar`, `orders.orders`, `reports.report`, `rules.rules` |
| `tests.test_cafe_report` | перевірки `assert`-ами | усі модулі проєкту |

Тека тестів — `tests/`, а не `test/`: `test` — пакет стандартної бібліотеки, і своя тека з таким ім'ям його затінила б (розділ уроку «Затінення»).

## Що показати на занятті

1. `python main.py 2024 7` і `python main.py` без аргументів — підказка з `main()`.
2. Перенести тестовий `print_report(...)` у `reports/report.py` з-під `if __name__ == "__main__":` на верхній рівень і знову запустити `main.py`: звіт з трьох тестових чеків надрукується перед справжнім.
3. Створити поруч `calendar.py` з одним рядком і запустити `main.py`: `AttributeError: module 'calendar' has no attribute 'monthrange'`. Видалити файл і теку `__pycache__`.
4. `python main.py 2024 липень` — `ValueError`: місток до уроку 14.
