# М4. Web (+ Web Advanced)

Програми говорять мережею: спершу — як клієнт до чужих API, далі — власні сервери на Django і FastAPI.

Уроки модуля:

- [Урок 31. HTTP: requests, httpx, aiohttp](m4/lesson_31.md) — шлях запиту: URL, IP і DNS, порти, TCP-рукостискання, TLS; HTTP як текст (запит сокетом), методи й статус-коди; `requests`: `params`, `json`, заголовки й токен, `raise_for_status`, тайм-аути й ієрархія винятків, повторні спроби з backoff і чому не для `POST`, `Session`; справжній API PyPI; `httpx` і `AsyncClient` + `gather`, `aiohttp`, потоки; архітектура: свій клієнт до API з доменними винятками, вибір бібліотеки. Практика — на навчальному API диспетчерської `smachno_api.py`.

Решта уроків — 🚧 у розробці.

17 уроків (лекції #31–47 у навігаційній таблиці v5.0): HTTP/REST → Django intro → DRF/FastAPI → повний CRUD → middlewares/кешування → auth/security basics → тестування API (лекції #31–41, «Web»), потім AI-інструменти розробника, інтеграція LLM API, архітектура застосунків, WebSockets, security advanced, Telegram Bot API (лекції #42–47, «Web Advanced»).

«Web Advanced» — це продовження М4, не окремий модуль: обидва блоки йдуть під одним наскрізним номером уроку, а модулі М5/М6 зберігають свої номери одразу після «Web Advanced» без зсуву.
