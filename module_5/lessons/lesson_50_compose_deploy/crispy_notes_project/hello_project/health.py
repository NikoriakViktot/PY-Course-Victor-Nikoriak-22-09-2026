"""GET /health/ — чи готовий застосунок приймати запити: база й Redis (channel layer чату). Урок 49.

Той самий підхід, що /health/ready у news_hub: назовні — лише «ok» чи назва винятку, подробиці — в журнал.
Compose чекає цієї перевірки, перш ніж запустити nginx (depends_on: condition: service_healthy).
"""
import logging
import os

import redis
from django.db import connection
from django.http import HttpRequest, JsonResponse

logger = logging.getLogger(__name__)


def health(request: HttpRequest) -> JsonResponse:
    checks: dict[str, str] = {}
    try:
        connection.ensure_connection()
        checks["database"] = "ok"
    except Exception as error:
        logger.warning("health: база недоступна: %s", error)
        checks["database"] = type(error).__name__
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:                        # без REDIS_URL чат працює на InMemoryChannelLayer (урок 45)
        try:
            redis.Redis.from_url(redis_url, socket_connect_timeout=2).ping()
            checks["redis"] = "ok"
        except Exception as error:
            logger.warning("health: Redis недоступний: %s", error)
            checks["redis"] = type(error).__name__
    ok = all(value == "ok" for value in checks.values())
    return JsonResponse({"status": "ok" if ok else "unavailable", "checks": checks}, status=200 if ok else 503)
