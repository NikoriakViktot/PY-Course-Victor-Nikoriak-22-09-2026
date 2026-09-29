# Проєкт нотаток у контейнері. Урок 49 (кроки 8–9 Django-книги).
# Основа — Dockerfile книги notes_chat_app; користувач, HEALTHCHECK і exec-CMD — як у news_hub уроку 48.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \
    DJANGO_SETTINGS_MODULE=hello_project.settings

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin app

COPY . .

# Том для collectstatic: новий іменований том Docker заповнює з образу разом із власником — отже app
RUN mkdir -p /app/staticfiles && chown app /app/staticfiles

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/', timeout=4)"]

# daphne (урок 45) — HTTP і WebSocket; --proxy-headers: IP клієнта з X-Forwarded-For від nginx.
# Без --reload: це для розробки (стежить за файлами, перезапускає процес).
CMD ["daphne", "--bind", "0.0.0.0", "--port", "8000", "--proxy-headers", "hello_project.asgi:application"]
