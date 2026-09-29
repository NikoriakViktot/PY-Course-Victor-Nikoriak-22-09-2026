-- Аудит індексів PostgreSQL (урок 51): psql "$DATABASE_URL" -f db_audit.sql
-- Лише читання: pg_catalog і статистика, дані таблиць не змінює.

\echo '== 1. Розмір таблиць та їхніх індексів'
SELECT c.relname                                         AS "таблиця",
       c.reltuples::bigint                               AS "рядків (оцінка)",
       pg_size_pretty(pg_table_size(c.oid))              AS "дані",
       pg_size_pretty(pg_indexes_size(c.oid))            AS "індекси"
FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r' AND n.nspname = 'public'
ORDER BY pg_total_relation_size(c.oid) DESC;

\echo '== 2. Зайві індекси: їхні стовпці — початок іншого індексу тієї ж таблиці'
-- (chat_id) зайвий поруч з UNIQUE (chat_id, keyword): пошук за chat_id іде по складеному.
-- Не чіпаємо індекси первинного ключа.
SELECT a.indrelid::regclass                              AS "таблиця",
       a.indexrelid::regclass                            AS "зайвий індекс",
       b.indexrelid::regclass                            AS "покриває його",
       pg_size_pretty(pg_relation_size(a.indexrelid))    AS "розмір"
FROM pg_index a
JOIN pg_index b ON a.indrelid = b.indrelid AND a.indexrelid <> b.indexrelid
WHERE NOT a.indisprimary
  AND a.indexprs IS NULL AND b.indexprs IS NULL           -- індекси за виразами порівнюємо вручну
  AND a.indpred IS NULL AND b.indpred IS NULL             -- і часткові (WHERE …) теж
  AND a.indnkeyatts <= b.indnkeyatts
  AND (a.indkey::int2[])[0:a.indnkeyatts - 1] = (b.indkey::int2[])[0:a.indnkeyatts - 1]
  -- той самий клас операторів: Django-індекс *_like (varchar_pattern_ops, для LIKE 'abc%') не зайвий
  AND (a.indclass::oid[])[0:a.indnkeyatts - 1] = (b.indclass::oid[])[0:a.indnkeyatts - 1]
  AND NOT (a.indisunique AND a.indnkeyatts = b.indnkeyatts AND NOT b.indisunique)
  AND NOT (a.indnkeyatts = b.indnkeyatts AND a.indexrelid > b.indexrelid AND a.indisunique = b.indisunique)
ORDER BY 1, 2;

\echo '== 3. Індекси, якими ще жодного разу не користувались'
-- Має сенс лише на базі з реальним навантаженням (статистика рахується з останнього скидання).
-- Унікальні індекси не показуємо: вони тримають обмеження, навіть якщо ними не шукають.
SELECT relname AS "таблиця", indexrelname AS "індекс", idx_scan AS "сканувань",
       pg_size_pretty(pg_relation_size(indexrelid)) AS "розмір"
FROM pg_stat_user_indexes JOIN pg_index USING (indexrelid)
WHERE idx_scan = 0 AND NOT indisunique
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 20;

\echo '== 4. Таблиці, які частіше читають повним переглядом, ніж через індекс'
SELECT relname AS "таблиця", seq_scan AS "повних переглядів", idx_scan AS "через індекс",
       n_live_tup AS "рядків"
FROM pg_stat_user_tables
WHERE seq_scan > coalesce(idx_scan, 0) AND n_live_tup > 1000
ORDER BY seq_scan DESC;
