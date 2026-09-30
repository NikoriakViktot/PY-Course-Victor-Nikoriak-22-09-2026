import hmac

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from backend.config import config
from backend.schemas import StudentProfile
from backend.services.ml_service import (
    predict_depression,
    get_clusters,
    get_anomalies,
    get_feature_importance,
    train_all,
)
from backend.utils.logger import get_logger

log = get_logger(__name__)
ml_bp = Blueprint("ml", __name__, url_prefix="/api")


@ml_bp.post("/predict")
def predict():
    try:
        profile = StudentProfile.model_validate(request.get_json(silent=True))
    except ValidationError as e:
        # урок 42: 422 з переліком полів; без тексту винятків pandas і без значень, які надіслав клієнт
        errors = [{"field": ".".join(map(str, err["loc"])) or "body", "message": err["msg"]}
                  for err in e.errors()]
        return jsonify({"error": "invalid input", "errors": errors}), 422
    return jsonify(predict_depression(profile))


@ml_bp.get("/clusters")
def clusters():
    return jsonify(get_clusters())


@ml_bp.get("/anomalies")
def anomalies():
    return jsonify(get_anomalies())


@ml_bp.get("/feature-importance")
def feature_importance():
    return jsonify(get_feature_importance())


@ml_bp.post("/train")
def train():
    """Re-train all models. Урок 42: лише з X-Admin-Token == ADMIN_TOKEN; без ADMIN_TOKEN — вимкнено."""
    token = request.headers.get("X-Admin-Token", "")
    if not config.ADMIN_TOKEN or not hmac.compare_digest(token.encode(), config.ADMIN_TOKEN.encode()):
        return jsonify({"error": "forbidden"}), 403
    try:
        metrics = train_all()
        return jsonify({"status": "ok", "metrics": metrics})
    except Exception:
        log.exception("Training failed")
        return jsonify({"error": "training failed"}), 500
