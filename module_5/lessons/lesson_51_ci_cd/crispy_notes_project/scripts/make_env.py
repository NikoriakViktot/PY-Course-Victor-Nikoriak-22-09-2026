"""Згенерувати .env для CI чи першого запуску: випадкові пароль бази й DJANGO_SECRET_KEY. Урок 50.

    python scripts/make_env.py          # існуючий .env не перезаписує

Лише стандартна бібліотека: ключ — з того самого алфавіту, що get_random_secret_key() Django (є `$` і `#`),
тому в одинарних лапках — так його читає Compose (урок 49).
"""
import os
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"


def main() -> int:
    target = ROOT / ".env"
    if target.exists():
        print(f"{target} уже є — не чіпаю", file=sys.stderr)
        return 1
    values = {
        "POSTGRES_PASSWORD": secrets.token_urlsafe(24),
        "DJANGO_SECRET_KEY": "".join(secrets.choice(ALPHABET) for _ in range(50)),
        "HTTP_PORT": os.environ.get("HTTP_PORT", "80"),
    }
    lines = []
    for line in (ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
        key = line.split("=", 1)[0]
        lines.append(f"{key}='{values.pop(key)}'" if key in values and not line.startswith("#") else line)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    target.chmod(0o600)
    print(f"створено {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
