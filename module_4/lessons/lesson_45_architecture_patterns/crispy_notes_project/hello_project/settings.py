"""
Django settings — уроки 40 (автентифікація й безпека) і 44 (PostgreSQL).

Зі стартового коду (автентифікація й безпека):
  + password reset/change flows   → EMAIL_BACKEND (console), /accounts/password_*/
  + security settings block       → SESSION_COOKIE_HTTPONLY, X_FRAME_OPTIONS, ...
  + Group-based sharing           → Django built-in Group model used in Note/ShoppingList
Урок 40 курсу додає:
  + JWT для API (djangorestframework-simplejwt) → /api/token/, /api/token/refresh/
  + throttle на видачу токена (перебір паролів) → 5 спроб за хвилину
  + SECRET_KEY і DEBUG зі змінних середовища    → ключ підпису JWT не лежить у git для production
Урок 44 (крок 3 Django-книги):
  + DATABASES з DATABASE_URL (hello_project/database.py) → PostgreSQL 16 у docker-compose.yml; без змінної — SQLite
"""

import os
from datetime import timedelta
from pathlib import Path

from .database import database_from_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Цим ключем підписуються сесії, токени скидання пароля і JWT. Хто його знає — підробить будь-який токен.
# Для навчання — значення за замовчуванням; на сервері — лише змінна середовища (урок 49).
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-crispy-notes-dev-key-change-in-production")

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = [host for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if host]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # ── Crispy Forms ────────────────────────────────────────────────────────────
    "crispy_forms",       # core: FormHelper, Layout objects
    "crispy_bootstrap5",  # Bootstrap5 template pack
    # ── REST API (урок 35) ─────────────────────────────────────────────────────────
    "rest_framework",     # Django REST Framework: серіалізатори, ViewSet, роутер
    "drf_spectacular",    # OpenAPI-схема з ViewSet і серіалізаторів
    # ── Debug ────────────────────────────────────────────────────────────────────
    "debug_toolbar",
    # ── Our app ──────────────────────────────────────────────────────────────────
    "hello_app",
]

# ── Crispy Forms Config ──────────────────────────────────────────────────────────
# Tells crispy-forms which HTML/CSS to generate
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ── Django REST Framework (урок 35) ──────────────────────────────────────────────
# Вхід — ті самі сесії, що й у HTML-частини (+ Basic для curl/скриптів).
# Без входу API не віддає нічого: нотатки приватні.
REST_FRAMEWORK = {
    # Порядок важливий: без облікових даних DRF відповідає за ПЕРШИМ класом. JWT першим → 401 з
    # WWW-Authenticate: Bearer; сесія першою → 403 (у неї немає заголовка WWW-Authenticate).
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",     # урок 40: інші клієнти, Bearer
        "rest_framework.authentication.SessionAuthentication",           # браузер (cookie + CSRF)
    ],                                                                   # BasicAuthentication прибрано: пароль у кожному запиті
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_RATES": {"login": "5/min"},                        # урок 40: перебір паролів на /api/token/
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),     # короткий: викрадений access-токен швидко «згорає»
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),       # ним отримують новий access, не вводячи пароль
    "ROTATE_REFRESH_TOKENS": True,                     # з кожним refresh — новий refresh-токен
    "AUTH_HEADER_TYPES": ("Bearer",),
}
SPECTACULAR_SETTINGS = {"TITLE": "CrispyNotes API", "VERSION": "1.0.0"}

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

INTERNAL_IPS = ["127.0.0.1"]

ROOT_URLCONF = "hello_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # ── DIRS: project-level templates (base.html, layouts/, components/) ──
        # Without this, {% extends 'layouts/dashboard.html' %} would fail!
        # APP_DIRS only searches <app>/templates/, not project root templates/
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,   # also searches hello_app/templates/hello_app/
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Sidebar: notebooks + tags available in every template
                "hello_app.context_processors.sidebar_context",
            ],
        },
    },
]

WSGI_APPLICATION = "hello_project.wsgi.application"

# ── Messages → Bootstrap alert variants ─────────────────────────────────────────
from django.contrib.messages import constants as messages_constants
MESSAGE_TAGS = {
    messages_constants.DEBUG:   'secondary',
    messages_constants.INFO:    'info',
    messages_constants.SUCCESS: 'success',
    messages_constants.WARNING: 'warning',
    messages_constants.ERROR:   'danger',
}

# Урок 44: база — з DATABASE_URL (PostgreSQL у docker compose); без змінної — SQLite, як і раніше
DATABASES = {"default": database_from_url(os.environ.get("DATABASE_URL"), base_dir=BASE_DIR)}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "uk"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ── Static files ─────────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
# STATICFILES_DIRS: project-level static/ (custom CSS overrides)
# hello_app/static/ is found automatically via APP_DIRS
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth redirects
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/notes/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# ── Email (password reset) ────────────────────────────────────────────────────
# console → лист виводиться в термінал, не надсилається реально.
# В production: django.core.mail.backends.smtp.EmailBackend + SMTP config.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ── Web Security ──────────────────────────────────────────────────────────────
# AuthenticationMiddleware: JS не може прочитати session cookie через document.cookie
SESSION_COOKIE_HTTPONLY = True

# CSRF cookie читається JS (потрібно для fetch/axios з CSRF header).
# Якщо не використовуєш JS fetch — постав True для строгого захисту.
CSRF_COOKIE_HTTPONLY = False

# SameSite=Lax: cookie надсилається тільки з того самого сайту.
# Захищає від CSRF-атак через cross-site форми.
SESSION_COOKIE_SAMESITE = "Lax"

# X-Frame-Options: браузер блокує вставку сторінки в <iframe>.
# Захищає від clickjacking-атак.
X_FRAME_OPTIONS = "DENY"

# Content-Type sniffing: браузер не вгадує тип файлу, якщо сервер не вказав.
# Захищає від XSS через завантажені файли.
SECURE_CONTENT_TYPE_NOSNIFF = True

# ── Production HTTPS (розкоментувати на сервері з SSL) ───────────────────────
# SESSION_COOKIE_SECURE = True    # cookie тільки через HTTPS
# CSRF_COOKIE_SECURE = True       # CSRF cookie тільки через HTTPS
# SECURE_SSL_REDIRECT = True      # HTTP → 301 → HTTPS
# SECURE_HSTS_SECONDS = 31536000  # браузер запам'ятовує HTTPS на 1 рік
