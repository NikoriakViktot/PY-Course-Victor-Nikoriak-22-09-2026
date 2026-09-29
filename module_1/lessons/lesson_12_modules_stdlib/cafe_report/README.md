# Звіт кафе з модулів — проєкт до уроку 12

Проєкт до [уроку 12 «Модулі та стандартна бібліотека»](../../../../docs/modules/m1/lesson_12.md). Звіт кафе з уроку 7, розкладений на чотири модулі й запущений з термінала. Той самий проєкт студенти створюють з клітинок ноутбука [`note_lesson_12_modules_stdlib.ipynb`](../note_lesson_12_modules_stdlib.ipynb) через `%%writefile`.

## Запуск

```bash
cd module_1/lessons/lesson_12_modules_stdlib/cafe_report
python main.py 2024 7        # звіт за липень 2024
python report.py             # перевірка модуля звіту на трьох тестових чеках
python test_cafe_report.py   # усі перевірки
```

Потрібна лише стандартна бібліотека. Чеки генеруються з фіксованим зерном (`seed=42`), тож звіт щоразу однаковий.

## Файли

| Файл | Що всередині | Імпортує |
|---|---|---|
| `rules.py` | `DAYS`, `MONTHS`, `day_from_timestamp`, `meal_type_from_hour` | нічого |
| `orders.py` | `RawOrder`, `Order`, `generate_raw_orders`, `in_month`, `to_order` | `random`, `datetime`, `typing`, `rules` |
| `report.py` | `count_by_day`, `revenue_by_day`, `best_day`, `print_report` | `collections`, `rules` |
| `main.py` | `main(args)`: аргументи командного рядка → звіт за місяць | `sys`, `calendar`, `orders`, `report`, `rules` |
| `test_cafe_report.py` | перевірки `assert`-ами | усі модулі проєкту |

## Що показати на занятті

1. `python main.py 2024 7` і `python main.py` без аргументів — підказка з `main()`.
2. Перенести тестовий `print_report(...)` у `report.py` з-під `if __name__ == "__main__":` на верхній рівень і знову запустити `main.py`: звіт з трьох тестових чеків надрукується перед справжнім.
3. Створити поруч `calendar.py` з одним рядком і запустити `main.py`: `AttributeError: module 'calendar' has no attribute 'monthrange'`. Видалити файл і теку `__pycache__`.
4. `python main.py 2024 липень` — `ValueError`: місток до уроку 13.
