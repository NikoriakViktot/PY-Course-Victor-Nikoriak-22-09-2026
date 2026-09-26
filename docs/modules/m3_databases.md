# М3. Бази даних

Стан програми виходить за межі Python-процесу: дані живуть у базі, переживають перезапуск і спільні для багатьох програм.

Уроки модуля:

- [Урок 29. Основи SQL (PostgreSQL)](m3/lesson_29.md) — база диспетчерської «Смачно + Таксі»: клієнт і сервер PostgreSQL, встановлення (Docker, інсталятор, Linux, Colab), таблиці з первинними й зовнішніми ключами та обмеженнями, `INSERT … RETURNING` / `UPDATE` / `DELETE`, `SELECT` і порядок його виконання, `NULL`, агрегати з `GROUP BY` / `HAVING`, `JOIN` і `LEFT JOIN`, підзапити й `WITH`, транзакції й ACID; з Python — `psycopg`, SQL-ін'єкція й параметри, репозиторій; архітектура: де живуть правила, індекси й `EXPLAIN`.
- [Урок 30. Redis overview](m3/lesson_30.md) — Redis поруч із PostgreSQL: що класти в пам'ять, а що на диск; `SET` / `GET`, атомарний `INCR` проти гонитви, `EXPIRE` / `TTL`; структури list, hash, set, sorted set (відповідники з уроку 28); `redis-py` і `pipeline`; кеш cache-aside, черга задач producer / consumer (`BLPOP`), Pub/Sub; архітектура: персистентність RDB / AOF, `maxmemory-policy allkeys-lru`, коли Redis не потрібен; протокол RESP. Практика — rate limit.
