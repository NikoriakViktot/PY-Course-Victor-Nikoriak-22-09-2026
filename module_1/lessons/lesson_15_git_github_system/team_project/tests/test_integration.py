"""Інтеграційний тест: усі шість задач разом. Проходить лише після злиття всіх PR."""
import contextlib
import io
import json
import os
import shutil
import tempfile

import main

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECTED_TEXT = """Чеків: 4, пропущено рядків: 5
Виторг: 3040.00 грн, середній чек: 760.00 грн
Найкращий день: нд
За днями: пт 860.00, сб 980.00, нд 1200.00
За прийомом їжі: вечеря 3, обід 1
"""
EXPECTED_REPORT = {
    "orders": 4, "skipped": 5, "revenue": 3040.0, "average": 760.0, "best_day": "нд",
    "by_day": {"пт": 860.0, "сб": 980.0, "нд": 1200.0},
    "by_meal": {"вечеря": 3, "обід": 1},
    "first_order": "2024-07-19T12:10:00",
}


def run_main(args, folder):
    out = io.StringIO()
    old = os.getcwd()
    os.chdir(folder)
    try:
        with contextlib.redirect_stdout(out):
            code = main.main(args)
    finally:
        os.chdir(old)
    return code, out.getvalue()


def test_full_report():
    with tempfile.TemporaryDirectory() as folder:
        shutil.copy(os.path.join(PROJECT, "kasa_2024_07.txt"), folder)
        code, text = run_main(["main.py", "kasa_2024_07.txt"], folder)
        assert code == 0 and text == EXPECTED_TEXT, "\n" + text
        with open(os.path.join(folder, "report.json"), encoding="utf-8") as file:
            assert json.load(file) == EXPECTED_REPORT
        with open(os.path.join(folder, "errors.txt"), encoding="utf-8") as file:
            numbers = [line.split(":")[0] for line in file]
        assert numbers == ["рядок 3", "рядок 5", "рядок 6", "рядок 7", "рядок 8"], numbers


def test_missing_file():
    with tempfile.TemporaryDirectory() as folder:
        code, text = run_main(["main.py", "kasa_2024_08.txt"], folder)
    assert code == 1 and text.startswith("Немає файлу каси"), text
