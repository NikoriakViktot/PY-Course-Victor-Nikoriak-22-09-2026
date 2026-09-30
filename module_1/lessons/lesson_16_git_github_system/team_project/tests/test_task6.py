"""Задача 6 — output.py. Працює зі словником звіту, формат якого описано в задачі 5."""
import json
import os
import tempfile

from output import format_report, save_json

REPORT = {
    "orders": 4, "skipped": 5, "revenue": 3040.0, "average": 760.0, "best_day": "нд",
    "by_day": {"пт": 860.0, "сб": 980.0, "нд": 1200.0},
    "by_meal": {"вечеря": 3, "обід": 1},
    "first_order": "2024-07-19T12:10:00",
}
EMPTY = {"orders": 0, "skipped": 2, "revenue": 0, "average": 0.0, "best_day": None,
         "by_day": {}, "by_meal": {}, "first_order": None}


def test_save_json():
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "report.json")
        save_json(REPORT, path)
        with open(path, encoding="utf-8") as file:
            text = file.read()
    assert json.loads(text) == REPORT
    assert "нд" in text, "кирилиця має лишитися кирилицею: ensure_ascii=False"
    assert '\n  "orders": 4' in text, "відступ 2 пробіли: indent=2"


def test_format_report():
    expected = (
        "Чеків: 4, пропущено рядків: 5\n"
        "Виторг: 3040.00 грн, середній чек: 760.00 грн\n"
        "Найкращий день: нд\n"
        "За днями: пт 860.00, сб 980.00, нд 1200.00\n"
        "За прийомом їжі: вечеря 3, обід 1"
    )
    assert format_report(REPORT) == expected, "\n" + format_report(REPORT)


def test_format_empty_report():
    expected = (
        "Чеків: 0, пропущено рядків: 2\n"
        "Виторг: 0.00 грн, середній чек: 0.00 грн\n"
        "Найкращий день: —\n"
        "За днями: —\n"
        "За прийомом їжі: —"
    )
    assert format_report(EMPTY) == expected, "\n" + format_report(EMPTY)
