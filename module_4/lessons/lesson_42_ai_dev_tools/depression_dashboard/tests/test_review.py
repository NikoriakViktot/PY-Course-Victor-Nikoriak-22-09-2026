"""Рецензія AI-згенерованого коду тестами (урок 42).

Кожен тест — одна знахідка рецензії: на стартовому коді він падає, після виправлення — проходить.
Застосунок при цьому «працював»: усі ендпоінти відповідали 200, дашборд малював графіки.
"""
import json
import pickle

import numpy as np
import pytest
from sklearn.model_selection import train_test_split

PROFILE = {
    "age": 22, "gender": "Female", "sleep_duration": "5-6 hours",
    "academic_pressure": 3, "work_pressure": 0, "study_satisfaction": 3, "job_satisfaction": 0,
    "work_study_hours": 6, "financial_stress": 2, "dietary_habits": "Moderate",
    "family_history": False, "suicidal_thoughts": False,
}


def strict_json(response) -> object:
    """NaN / Infinity — не JSON (RFC 8259); браузер і більшість клієнтів їх не приймуть."""
    def reject(token: str) -> None:
        raise ValueError(f"у відповіді {token} — це не JSON")
    return json.loads(response.get_data(as_text=True), parse_constant=reject)


# ── 1. Порядок, який губиться в JSON ─────────────────────────────────────────────

def test_feature_importance_keeps_descending_order(client) -> None:
    """Сервіс сортує важливість за спаданням, але Flask за замовчуванням сортує ключі JSON за алфавітом."""
    values = list(strict_json(client.get("/api/feature-importance")).values())
    assert values == sorted(values, reverse=True)


def test_correlations_keep_order_by_strength(client) -> None:
    corr = strict_json(client.get("/api/correlations"))["with_depression"]
    strengths = [abs(v) for v in corr.values()]
    assert strengths == sorted(strengths, reverse=True)


# ── 2. Вигадані назви кластерів ──────────────────────────────────────────────────

def test_cluster_names_agree_with_profiles(client) -> None:
    """Назву кластера має давати його профіль, а не словник у коді UI: номери KMeans довільні."""
    data = strict_json(client.get("/api/clusters"))
    names = data["cluster_names"]
    profiles = data["cluster_profiles"]
    assert set(names) == set(profiles)
    overall = data["overall"]
    for cid, name in names.items():
        feature, direction = name.split(": ")
        diff = profiles[cid][feature] - overall[feature]
        assert (direction == "вище середнього") == (diff > 0), (cid, name, diff)


# ── 3–4. /api/predict: валідація, похідні ознаки, «мертвий» повзунок ────────────

def test_predict_accepts_raw_profile(client) -> None:
    """Похідні ознаки (Risk_Score, Pressure_Sum…) рахує сервер — клієнт надсилає лише анкету."""
    body = strict_json(client.post("/api/predict", json=PROFILE))
    assert 0 <= body["probability_depressed"] <= 1
    assert body["risk_level"] in {"Low", "Medium", "High"}


@pytest.mark.parametrize(("change", "field"), [
    ({"age": -500}, "age"),
    ({"financial_stress": 999}, "financial_stress"),
    ({"sleep_duration": "Others"}, "sleep_duration"),
    ({"Risk_Score": -100}, "Risk_Score"),              # похідну ознаку не можна підробити
    ({"CGPA": 7.5}, "CGPA"),                            # поле, якого модель не знає, — помилка, а не тиша
])
def test_predict_rejects_bad_input(client, change: dict, field: str) -> None:
    response = client.post("/api/predict", json={**PROFILE, **change})
    assert response.status_code == 422
    assert field in {e["field"] for e in strict_json(response)["errors"]}


def test_predict_missing_field_is_422_without_internals(client) -> None:
    profile = dict(PROFILE)
    profile.pop("age")
    response = client.post("/api/predict", json=profile)
    text = response.get_data(as_text=True)
    assert response.status_code == 422 and "age" in text
    assert "Traceback" not in text and "Index(" not in text and "KeyError" not in text


def test_predict_list_body_is_422(client) -> None:
    assert client.post("/api/predict", json=[1, 2]).status_code == 422


# ── 5. Навчання без захисту ──────────────────────────────────────────────────────

def test_train_requires_admin_token(client, monkeypatch: pytest.MonkeyPatch) -> None:
    """POST /api/train перезаписує модель — лише з токеном адміністратора (ADMIN_TOKEN у середовищі)."""
    from backend.config import config
    monkeypatch.setattr(config, "ADMIN_TOKEN", "test-token-" + "x" * 20, raising=False)
    assert client.post("/api/train").status_code == 403
    assert client.post("/api/train", headers={"X-Admin-Token": "wrong"}).status_code == 403
    ok = client.post("/api/train", headers={"X-Admin-Token": "test-token-" + "x" * 20})
    assert ok.status_code == 200 and 0.5 < ok.get_json()["metrics"]["auc"] <= 1


def test_train_disabled_without_configured_token(client, monkeypatch: pytest.MonkeyPatch) -> None:
    from backend.config import config
    monkeypatch.setattr(config, "ADMIN_TOKEN", "", raising=False)
    assert client.post("/api/train", headers={"X-Admin-Token": ""}).status_code == 403


# ── 6. Витік даних у навчанні ────────────────────────────────────────────────────

def test_imputer_fitted_on_train_split_only(client) -> None:
    """Медіани для пропусків має рахувати лише навчальна вибірка — інакше тестова «підглядає»."""
    from backend.config import config
    from backend.services import ml_service
    from backend.services.data_service import load_student_df

    client.get("/api/feature-importance")                              # модель навчається при першому запиті
    with open(ml_service.MODEL_PATH, "rb") as f:
        artifacts = pickle.load(f)
    imputer = artifacts["classifier"].named_steps["imputer"]
    df = load_student_df()
    X_train, _, _, _ = train_test_split(df[ml_service.FEATURES], df["Depression"], test_size=config.TEST_SIZE,
                                        random_state=config.RANDOM_STATE, stratify=df["Depression"])
    np.testing.assert_allclose(imputer.statistics_, X_train.median().to_numpy())


# ── 7. Модель з диска на кожен запит ─────────────────────────────────────────────

def test_model_loaded_from_disk_once(client, monkeypatch: pytest.MonkeyPatch) -> None:
    client.post("/api/predict", json=PROFILE)                         # навчання + перше завантаження
    loads = []
    real_load = pickle.load
    monkeypatch.setattr(pickle, "load", lambda f: loads.append(1) or real_load(f))
    for _ in range(3):
        client.post("/api/predict", json=PROFILE)
    assert loads == []


# ── 8. Кешований DataFrame змінюють на місці ─────────────────────────────────────

def test_groups_does_not_change_cached_data(client) -> None:
    client.get("/api/groups")
    assert "fin_stress_bucket" not in strict_json(client.get("/api/summary"))["missing_values"]


# ── 9. Невалідний JSON на брудних даних ──────────────────────────────────────────

def test_unknown_sleep_values_give_valid_json(client, data_dir) -> None:
    """Невідоме значення сну (у справжньому датасеті є «Others») → NaN; у відповіді має бути null, а не NaN."""
    import pandas as pd

    from backend.services.data_service import load_student_df
    path = data_dir / "Student Depression Dataset.csv"
    df = pd.read_csv(path)
    df["Sleep Duration"] = "Others"
    df.to_csv(path, index=False)
    load_student_df.cache_clear()
    for url in ("/api/summary", "/api/correlations"):
        strict_json(client.get(url))
