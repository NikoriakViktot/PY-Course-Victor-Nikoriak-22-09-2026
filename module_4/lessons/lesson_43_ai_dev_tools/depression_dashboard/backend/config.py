import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    # Paths — data lives one level up from the project root (next to depression_dashboard/)
    DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR.parent / "data")))
    # урок 42: шлях до моделей — зі змінної середовища (у Docker — том), а не лише папка проєкту
    MODELS_DIR = Path(os.getenv("MODELS_DIR", str(BASE_DIR / "models")))

    # Datasets
    STUDENT_DATASET = DATA_DIR / "Student Depression Dataset.csv"
    SLEEP_DATASET = DATA_DIR / "Sleep_health_and_lifestyle_dataset.csv"
    BURNOUT_DATASET = DATA_DIR / "mental_health_burnout_tech_2026.csv"

    # Flask
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    # урок 42: за замовчуванням — лише локально; у Docker FLASK_HOST=0.0.0.0 задає docker-compose.yml
    HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    PORT = int(os.getenv("FLASK_PORT", 5050))
    # урок 42: POST /api/train — лише з цим токеном (заголовок X-Admin-Token); порожній — навчання вимкнено
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

    # ML
    RANDOM_STATE = 42
    TEST_SIZE = 0.2
    N_CLUSTERS = 4
    CONTAMINATION = 0.05          # IsolationForest outlier fraction

    # Streamlit backend URL
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5050")

config = Config()
