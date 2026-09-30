import math
from typing import Any

from flask import Flask, jsonify
from flask.json.provider import DefaultJSONProvider
from backend.config import config
from backend.routes.analytics import analytics_bp
from backend.routes.ml import ml_bp
from backend.utils.logger import get_logger

log = get_logger(__name__)


def _finite(value: Any) -> Any:
    """NaN / inf → None (null): інакше json.dumps пише NaN, а це не JSON."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: _finite(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_finite(v) for v in value]
    return value


class StrictJSONProvider(DefaultJSONProvider):
    """Урок 42: порядок ключів — як у словнику (сервіси сортують за важливістю), і лише валідний JSON."""
    sort_keys = False                     # Flask за замовчуванням сортує ключі за алфавітом

    def dumps(self, obj: Any, **kwargs: Any) -> str:
        kwargs.setdefault("allow_nan", False)
        return super().dumps(_finite(obj), **kwargs)


def create_app() -> Flask:
    app = Flask(__name__)
    app.json = StrictJSONProvider(app)

    # register blueprints
    app.register_blueprint(analytics_bp)
    app.register_blueprint(ml_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "internal server error"}), 500

    log.info("Flask app created — routes registered")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
