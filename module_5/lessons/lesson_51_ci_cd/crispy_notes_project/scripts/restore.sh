#!/usr/bin/env bash
# Відновити базу нотаток з бекапу. Урок 49.   ./scripts/restore.sh backups/crispy_notes-….sql.gz
# Поточні дані в базі буде ЗАМІНЕНО даними з бекапу.
set -euo pipefail

cd "$(dirname "$0")/.."
if [[ $# -ne 1 || ! -f "$1" ]]; then
    echo "usage: scripts/restore.sh BACKUP.sql.gz" >&2
    exit 2
fi

gunzip -c "$1" | docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -q -o /dev/null'
echo "відновлено з $1"
