"""Навчання й інференс: RandomForest (ризик), KMeans (кластери), IsolationForest (аномалії).

Стартовий код — AI-згенерований проєкт. Урок 42 — що змінено після рецензії тестами:
- витік даних: імпутер і скейлер навчались на ВСІХ рядках до train_test_split → тепер Pipeline,
  навчений лише на навчальній вибірці; скейлер для RandomForest прибрано (деревам він не потрібен);
- модель читалась з диска (pickle, 57 МБ) на КОЖЕН запит → кеш у пам'яті, скидається після навчання;
- файл моделі перезаписувався на місці → запис у тимчасовий файл і атомарна заміна під замком;
- PCA перенавчався на кожен GET /api/clusters → навчається разом з KMeans;
- назви кластерів були вшиті в UI («Sleep Deprived» для кластера, що спить найбільше) →
  назву дає профіль кластера порівняно з середнім (cluster_names);
- /api/predict приймав похідні ознаки від клієнта → StudentProfile + add_features на сервері.
"""
import os
import pickle
import tempfile
import threading
from typing import Any

import numpy as np
import pandas as pd
import sklearn
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from backend.config import config
from backend.schemas import StudentProfile
from backend.services.data_service import add_features, load_student_df
from backend.utils.logger import get_logger

log = get_logger(__name__)

FEATURES = [
    "Age", "Academic Pressure", "Work Pressure",
    "Study Satisfaction", "Job Satisfaction",
    "Sleep_hours", "Work/Study Hours", "Financial Stress",
    "Gender_enc", "Family_History_enc", "Suicidal_enc", "Dietary_enc",
    "Risk_Score", "Pressure_Sum", "Satisfaction_Sum", "Sleep_deficit",
]
TARGET = "Depression"
# Ознаки, якими описуємо кластер (зрозумілі людині, у шкалах датасету)
PROFILE_FEATURES = ["Age", "Risk_Score", "Sleep_hours", "Financial Stress", "Academic Pressure"]
MAX_POINTS = 2000                 # точок на діаграмі розсіювання: 27 901 рядок — це ~3,4 МБ JSON

MODEL_PATH = config.MODELS_DIR / "classifier.pkl"

_lock = threading.Lock()
_cache: dict[str, Any] = {}


def reset_cache() -> None:
    _cache.clear()


# ── Training ─────────────────────────────────────────────────────────────────

def train_all() -> dict:
    df = load_student_df()
    X = df[FEATURES]
    y = df[TARGET]

    # Спершу розділяємо, потім навчаємо все, що «бачить» дані, — лише на навчальній частині
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE,
        random_state=config.RANDOM_STATE, stratify=y,
    )
    clf = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestClassifier(n_estimators=200, max_depth=12,
                                         random_state=config.RANDOM_STATE, n_jobs=-1)),
    ])
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]
    report = classification_report(y_test, y_pred, output_dict=True)
    auc = roc_auc_score(y_test, y_prob)
    log.info("Classifier AUC=%.4f | Acc=%.4f", auc, report["accuracy"])

    # Кластери й аномалії — без мітки (unsupervised): навчаємо на всіх рядках, мітка не використовується
    prep = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
    X_all = prep.fit_transform(X)
    kmeans = KMeans(n_clusters=config.N_CLUSTERS, random_state=config.RANDOM_STATE, n_init=10).fit(X_all)
    iso = IsolationForest(contamination=config.CONTAMINATION, random_state=config.RANDOM_STATE).fit(X_all)
    pca = PCA(n_components=2, random_state=config.RANDOM_STATE).fit(X_all)

    metrics = {
        "auc": round(float(auc), 4),
        "accuracy": round(report["accuracy"], 4),
        "f1_depressed": round(report["1"]["f1-score"], 4),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
    }
    artifacts = {
        "classifier": clf,
        "prep": prep,
        "kmeans": kmeans,
        "isolation_forest": iso,
        "pca": pca,
        "features": FEATURES,
        "metrics": metrics,
        "sklearn_version": sklearn.__version__,     # pickle не переноситься між версіями sklearn
    }
    _save(artifacts)
    log.info("All models saved to %s", MODEL_PATH)
    importance = clf.named_steps["model"].feature_importances_.tolist()
    return {**metrics, "feature_importance": dict(zip(FEATURES, importance))}


def _save(artifacts: dict) -> None:
    """Запис у тимчасовий файл і атомарна заміна: читач ніколи не побачить половину файлу."""
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        fd, tmp = tempfile.mkstemp(dir=MODEL_PATH.parent, suffix=".tmp")
        with os.fdopen(fd, "wb") as f:
            pickle.dump(artifacts, f)
        os.replace(tmp, MODEL_PATH)
        _cache["artifacts"] = artifacts


def _load_artifacts() -> dict:
    """Модель — один раз у пам'ять. pickle виконує код під час читання: лише власні, довірені файли."""
    if "artifacts" in _cache:
        return _cache["artifacts"]
    if not MODEL_PATH.exists():
        log.info("No saved models found — training now …")
        train_all()
        return _cache["artifacts"]
    with _lock, open(MODEL_PATH, "rb") as f:
        artifacts = pickle.load(f)
    if artifacts.get("sklearn_version") != sklearn.__version__:
        log.warning("Модель збережено з scikit-learn %s, а встановлено %s — перенавчіть її",
                    artifacts.get("sklearn_version", "?"), sklearn.__version__)
    _cache["artifacts"] = artifacts
    return artifacts


# ── Inference ─────────────────────────────────────────────────────────────────

def predict_depression(profile: StudentProfile) -> dict:
    arts = _load_artifacts()
    row = add_features(pd.DataFrame([profile.to_row()]))[arts["features"]]
    prob = arts["classifier"].predict_proba(row)[0]
    return {
        "prediction": int(prob[1] >= 0.5),
        "probability_depressed": round(float(prob[1]), 4),
        "probability_not_depressed": round(float(prob[0]), 4),
        "risk_level": _risk_label(prob[1]),
    }


def _risk_label(prob: float) -> str:
    if prob >= 0.75:
        return "High"
    if prob >= 0.5:
        return "Medium"
    return "Low"


# ── Clustering ────────────────────────────────────────────────────────────────

def _cluster_names(profiles: pd.DataFrame, overall: pd.Series, spread: pd.Series) -> dict[str, str]:
    """Кластер називаємо за ознакою, де він найдалі від середнього (у стандартних відхиленнях)."""
    names = {}
    for cid, row in profiles.iterrows():
        z = (row[PROFILE_FEATURES] - overall[PROFILE_FEATURES]) / spread[PROFILE_FEATURES].replace(0, np.nan)
        feature = z.abs().idxmax()
        names[str(cid)] = f"{feature}: {'вище' if z[feature] > 0 else 'нижче'} середнього"
    return names


def get_clusters() -> dict:
    arts = _load_artifacts()
    df = load_student_df()
    X_all = arts["prep"].transform(df[arts["features"]])
    labels = arts["kmeans"].predict(X_all)
    coords = arts["pca"].transform(X_all)

    result_df = df[PROFILE_FEATURES + ["Depression"]].copy()
    result_df["cluster"] = labels
    result_df["pca_x"] = coords[:, 0]
    result_df["pca_y"] = coords[:, 1]

    profiles = result_df.groupby("cluster")[PROFILE_FEATURES + ["Depression"]].mean()
    overall = result_df[PROFILE_FEATURES].mean()
    points = result_df.sample(min(MAX_POINTS, len(result_df)), random_state=config.RANDOM_STATE)

    return {
        "points": points[["pca_x", "pca_y", "cluster", "Depression", "Risk_Score", "Age"]]
        .to_dict(orient="records"),
        "cluster_profiles": {str(k): v for k, v in profiles.round(3).to_dict(orient="index").items()},
        "cluster_sizes": {str(k): int(v) for k, v in result_df["cluster"].value_counts().sort_index().items()},
        "cluster_names": _cluster_names(profiles, overall, result_df[PROFILE_FEATURES].std()),
        "overall": overall.round(3).to_dict(),
        "n_clusters": config.N_CLUSTERS,
        "explained_variance": round(float(arts["pca"].explained_variance_ratio_.sum()), 4),
    }


# ── Anomaly Detection ─────────────────────────────────────────────────────────

def get_anomalies() -> dict:
    arts = _load_artifacts()
    df = load_student_df()
    X_all = arts["prep"].transform(df[arts["features"]])

    scores = arts["isolation_forest"].decision_function(X_all)
    preds = arts["isolation_forest"].predict(X_all)   # -1 = anomaly

    result_df = df[["Age", "Depression", "Risk_Score", "Sleep_hours",
                     "Financial Stress", "Academic Pressure", "Gender"]].copy()
    result_df["anomaly_score"] = scores
    result_df["is_anomaly"] = (preds == -1).astype(int)

    anomalies = result_df[result_df["is_anomaly"] == 1].copy()
    return {
        "total_anomalies": int(anomalies["is_anomaly"].sum()),
        "anomaly_rate": round(float((preds == -1).mean()) * 100, 2),
        "anomalies": anomalies.head(200).to_dict(orient="records"),
        "depression_in_anomalies": round(float(anomalies["Depression"].mean()), 4),
        "depression_overall": round(float(df["Depression"].mean()), 4),
    }


# ── Feature importance ────────────────────────────────────────────────────────

def get_feature_importance() -> dict:
    arts = _load_artifacts()
    model = arts["classifier"].named_steps["model"]
    importance = dict(zip(arts["features"], model.feature_importances_.tolist()))
    return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
