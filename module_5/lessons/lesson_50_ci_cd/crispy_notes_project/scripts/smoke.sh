#!/usr/bin/env bash
# Smoke-тест стеку нотаток у Compose: так його запускає CI (урок 50), так само можна локально.
#   python scripts/make_env.py && ./scripts/smoke.sh
# Піднімає стек, проходить шлях користувача через nginx і завжди прибирає за собою (docker compose down -v).
set -euo pipefail

cd "$(dirname "$0")/.."
port="$(grep -E '^HTTP_PORT=' .env | cut -d= -f2 | tr -d "'")"
base="http://localhost:${port:-80}"
jar="$(mktemp)"

cleanup() {
    status=$?
    rm -f "$jar"
    if [[ $status -ne 0 ]]; then
        echo "--- smoke впав (код $status): стан і журнали ---" >&2
        docker compose ps -a >&2 || true
        docker compose logs --tail 60 >&2 || true
    fi
    docker compose down -v --remove-orphans > /dev/null 2>&1 || true
}
trap cleanup EXIT

check() {                          # check "назва" очікуване фактичне
    if [[ "$2" != "$3" ]]; then
        echo "✗ $1: очікували $2, отримали $3" >&2
        exit 1
    fi
    echo "✓ $1"
}

docker compose up -d --build --wait --wait-timeout 180

check "готовність через nginx" 200 "$(curl -s -o /dev/null -w '%{http_code}' "$base/health/")"
check "статика з тому nginx" 200 "$(curl -s -o /dev/null -w '%{http_code}' "$base/static/admin/css/base.css")"
check "DEBUG вимкнено (404 без трасування)" 0 "$(curl -s "$base/no-such-page/" | grep -c 'DEBUG = True' || true)"

docker compose exec -T -e DJANGO_SUPERUSER_USERNAME=smoke -e DJANGO_SUPERUSER_PASSWORD=smoke-pass-12345 \
    -e DJANGO_SUPERUSER_EMAIL=smoke@example.com web python manage.py createsuperuser --noinput > /dev/null

# вхід формою: CSRF-токен зі сторінки, cookie — у jar, Origin — як у браузера (урок 49: $http_host)
csrf="$(curl -s -c "$jar" "$base/accounts/login/" | sed -n 's/.*name="csrfmiddlewaretoken" value="\([^"]*\)".*/\1/p' | head -1)"
login="$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' -b "$jar" -c "$jar" -X POST "$base/accounts/login/" \
    -H "Origin: $base" -H "Referer: $base/accounts/login/" \
    --data-urlencode "csrfmiddlewaretoken=$csrf" --data-urlencode "username=smoke" --data-urlencode "password=smoke-pass-12345")"
check "вхід формою через nginx" "302 $base/notes/" "$login"
check "сторінка нотаток після входу" 200 "$(curl -s -o /dev/null -w '%{http_code}' -b "$jar" "$base/notes/")"

check "база й Redis без портів назовні" "" "$(docker compose ps db redis --format '{{.Ports}}' | grep -- '->' || true)"
echo "smoke: усе гаразд"
