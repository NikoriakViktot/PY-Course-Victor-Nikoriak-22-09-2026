"""DATABASES з однієї змінної середовища DATABASE_URL (урок 44, крок 3 Django-книги: PostgreSQL).

    DATABASE_URL=postgres://notes_user:notes_pass@localhost:5432/notes_db   → PostgreSQL (docker compose up -d)
    без DATABASE_URL                                                        → SQLite db.sqlite3 поруч з manage.py

Та сама ідея, що в news_hub (урок 38): застосунок не знає, яка база, — знає змінна середовища.
Пакет dj-database-url робить те саме; тут — 20 рядків стандартної бібліотеки, щоб було видно, що всередині.
"""
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, unquote, urlsplit

ENGINES = {
    "postgres": "django.db.backends.postgresql",
    "postgresql": "django.db.backends.postgresql",
    "sqlite": "django.db.backends.sqlite3",
}


def database_from_url(url: str | None, *, base_dir: Path) -> dict[str, Any]:
    """postgres://user:pass@host:port/name?sslmode=require → словник для DATABASES["default"]."""
    if not url:
        return {"ENGINE": ENGINES["sqlite"], "NAME": base_dir / "db.sqlite3"}
    parts = urlsplit(url)
    if parts.scheme not in ENGINES:
        raise ValueError(f"DATABASE_URL: невідома схема {parts.scheme!r} (postgres:// або sqlite://)")
    if parts.scheme == "sqlite":                  # sqlite:///абсолютний/шлях.db
        return {"ENGINE": ENGINES["sqlite"], "NAME": unquote(parts.path) or base_dir / "db.sqlite3"}
    return {
        "ENGINE": ENGINES[parts.scheme],
        "NAME": unquote(parts.path.lstrip("/")),
        "USER": unquote(parts.username or ""),
        "PASSWORD": unquote(parts.password or ""),   # пароль із @ чи : — закодований (%40, %3A)
        "HOST": parts.hostname or "",
        "PORT": str(parts.port or ""),
        "CONN_MAX_AGE": 60,                       # тримати з'єднання між запитами (сторінка книги postgresql)
        "OPTIONS": dict(parse_qsl(parts.query)),  # напр. ?sslmode=require
    }
