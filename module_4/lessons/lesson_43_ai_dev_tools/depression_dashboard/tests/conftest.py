"""Тестові дані й клієнт Flask. Урок 42.

Справжній датасет (Kaggle, 27 901 рядок) у репозиторій не входить. Тести генерують невеликий
синтетичний CSV з тими самими колонками: детерміновано (seed), з тими ж особливостями, що й
справжні дані, — Work Pressure і Job Satisfaction майже завжди 0 (це студенти).
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

SLEEP = ["Less than 5 hours", "5-6 hours", "7-8 hours", "More than 8 hours"]
SLEEP_HOURS = {"Less than 5 hours": 4.0, "5-6 hours": 5.5, "7-8 hours": 7.5, "More than 8 hours": 9.0}


def make_students(n: int = 400, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    sleep = rng.choice(SLEEP, n)
    academic = rng.integers(1, 6, n).astype(float)
    financial = rng.integers(1, 6, n).astype(float)
    hours = rng.integers(0, 13, n).astype(float)
    suicidal = rng.choice(["Yes", "No"], n, p=[0.4, 0.6])
    logit = (0.8 * academic + 0.6 * financial + 0.15 * hours + 1.5 * (suicidal == "Yes")
             - 0.5 * np.array([SLEEP_HOURS[s] for s in sleep]) - 2.5)
    depression = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(int)
    return pd.DataFrame({
        "id": np.arange(n),
        "Gender": rng.choice(["Male", "Female"], n),
        "Age": rng.integers(18, 35, n).astype(float),
        "City": rng.choice(["Kyiv", "Lviv", "Odesa"], n),
        "Profession": "Student",
        "Academic Pressure": academic,
        "Work Pressure": np.where(rng.random(n) < 0.97, 0.0, rng.integers(1, 6, n)),
        "CGPA": rng.uniform(5, 10, n).round(2),
        "Study Satisfaction": rng.integers(1, 6, n).astype(float),
        "Job Satisfaction": np.where(rng.random(n) < 0.97, 0.0, rng.integers(1, 6, n)),
        "Sleep Duration": sleep,
        "Dietary Habits": rng.choice(["Healthy", "Moderate", "Unhealthy"], n),
        "Degree": rng.choice(["BSc", "MSc"], n),
        "Have you ever had suicidal thoughts ?": suicidal,
        "Work/Study Hours": hours,
        "Financial Stress": financial,
        "Family History of Mental Illness": rng.choice(["Yes", "No"], n),
        "Depression": depression,
    })


def make_burnout(n: int = 100, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "phq9_score": rng.integers(0, 27, n), "gad7_score": rng.integers(0, 21, n),
        "burnout_score": rng.uniform(0, 100, n).round(1),
        "phq9_category": rng.choice(["Minimal", "Mild", "Moderate", "Severe"], n),
        "gad7_category": rng.choice(["Minimal", "Mild", "Moderate", "Severe"], n),
        "burnout_level": rng.choice(["Low", "Medium", "High"], n),
    })


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    make_students().to_csv(tmp_path / "Student Depression Dataset.csv", index=False)
    make_burnout().to_csv(tmp_path / "mental_health_burnout_tech_2026.csv", index=False)
    return tmp_path


@pytest.fixture
def client(data_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Flask test client над синтетичними даними; моделі — у тимчасовій папці, не в проєкті."""
    from backend.config import config
    from backend.services import data_service, ml_service

    monkeypatch.setattr(config, "STUDENT_DATASET", data_dir / "Student Depression Dataset.csv")
    monkeypatch.setattr(config, "BURNOUT_DATASET", data_dir / "mental_health_burnout_tech_2026.csv")
    models = tmp_path / "models"
    monkeypatch.setattr(config, "MODELS_DIR", models)
    monkeypatch.setattr(ml_service, "MODEL_PATH", models / "classifier.pkl")
    for loader in (data_service.load_student_df, data_service.load_burnout_df):
        loader.cache_clear()
    if hasattr(ml_service, "reset_cache"):
        ml_service.reset_cache()

    from backend.app import create_app
    app = create_app()
    app.testing = True
    with app.test_client() as c:
        yield c
    for loader in (data_service.load_student_df, data_service.load_burnout_df):
        loader.cache_clear()
