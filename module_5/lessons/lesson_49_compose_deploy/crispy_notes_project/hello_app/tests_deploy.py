"""Урок 49: налаштування для сервера — /health/, ключ при DEBUG=0, HTTPS за nginx.

Налаштування читаються один раз, при імпорті, тому варіанти змінних середовища перевіряємо окремим процесом.
"""
import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

from django.test import TestCase

PROJECT = Path(__file__).resolve().parent.parent


def settings_in_subprocess(**env: str) -> subprocess.CompletedProcess[str]:
    code = ("import django; django.setup(); from django.conf import settings as s; "
            "print(s.DEBUG, s.SESSION_COOKIE_SECURE, s.SECURE_PROXY_SSL_HEADER, s.CSRF_TRUSTED_ORIGINS, s.STATIC_ROOT)")
    clean = {k: v for k, v in os.environ.items() if not k.startswith("DJANGO_")}
    return subprocess.run([sys.executable, "-c", code], cwd=PROJECT, capture_output=True, text=True,
                          env={**clean, "DJANGO_SETTINGS_MODULE": "hello_project.settings", **env})


class HealthTests(TestCase):
    def test_health_ok(self) -> None:
        with mock.patch.dict(os.environ, {"REDIS_URL": ""}):
            response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "checks": {"database": "ok"}})

    def test_redis_down_is_503(self) -> None:
        with mock.patch.dict(os.environ, {"REDIS_URL": "redis://127.0.0.1:1/0"}):
            response = self.client.get("/health/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["checks"], {"database": "ok", "redis": "ConnectionError"})


class ServerSettingsTests(TestCase):
    def test_debug_off_without_secret_key_fails_at_start(self) -> None:
        result = settings_in_subprocess(DJANGO_DEBUG="0")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ImproperlyConfigured: DJANGO_DEBUG=0: задай DJANGO_SECRET_KEY", result.stderr)

    def test_debug_off_with_secret_key_starts(self) -> None:
        result = settings_in_subprocess(DJANGO_DEBUG="0", DJANGO_SECRET_KEY="x" * 50)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("False False None []"))
        self.assertTrue(result.stdout.strip().endswith("staticfiles"))

    def test_https_behind_proxy(self) -> None:
        result = settings_in_subprocess(DJANGO_DEBUG="0", DJANGO_SECRET_KEY="x" * 50, DJANGO_HTTPS="1",
                                        DJANGO_CSRF_TRUSTED_ORIGINS="https://notes.example")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("False True ('HTTP_X_FORWARDED_PROTO', 'https') ['https://notes.example']", result.stdout)
