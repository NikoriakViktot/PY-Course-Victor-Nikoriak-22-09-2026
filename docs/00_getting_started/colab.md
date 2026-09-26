# Ноутбуки в Google Colab

Google Colab запускає Jupyter-ноутбуки просто в браузері: нічого встановлювати не треба, потрібен лише Google-акаунт.

## Як відкрити ноутбук уроку

**Спосіб 1 — кнопка.** У першій клітинці кожного ноутбука (і поруч із посиланнями на ноутбуки в книзі) є кнопка [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](#). Натисни її, і ноутбук відкриється в Colab.

**Спосіб 2 — адреса вручну.** Відкрий ноутбук на GitHub і в адресі заміни `https://github.com/` на `https://colab.research.google.com/github/`:

```text
https://github.com/NikoriakViktot/PY-Course-Victor-Nikoriak-22-09-2026/blob/main/module_1/lessons/lesson_03_variables_and_data_types/note_lesson_variables.ipynb
https://colab.research.google.com/github/NikoriakViktot/PY-Course-Victor-Nikoriak-22-09-2026/blob/main/module_1/lessons/lesson_03_variables_and_data_types/note_lesson_variables.ipynb
```

**Спосіб 3 — із самого Colab.** File → Open notebook → вкладка **GitHub** → введи `NikoriakViktot/PY-Course-Victor-Nikoriak-22-09-2026` → обери файл.

Уроки лежать у `module_N/lessons/lesson_NN_<тема>/`, де `NN` — номер уроку за програмою курсу.

## Збережи свою копію

Ноутбук, відкритий із репозиторію курсу, **не зберігає твоїх змін**. Щоб працювати з ним:

- **File → Save a copy in Drive** — копія з'явиться на твоєму Google Drive (папка «Colab Notebooks»). Далі працюй у ній.
- Якщо викладач оновив урок, твоя копія на Drive сама не оновиться. Відкрий ноутбук заново кнопкою Colab.

## Робота в Colab

### Інтерфейс і клітинки

Ноутбук складається з **клітинок** двох видів: **код** (Python) і **текст** (Markdown). Кнопки **+ Code** і **+ Text** зверху додають нову клітинку під поточною. Щоб виконати клітинку — кнопка ▶ зліва від неї або клавіші:

| Клавіші | Дія |
|---|---|
| **Shift+Enter** | виконати й перейти до наступної клітинки |
| **Ctrl+Enter** | виконати й лишитися на клітинці |
| **Ctrl+M B** / **Ctrl+M A** | нова клітинка нижче / вище |
| **Ctrl+M D** | видалити клітинку |
| **Ctrl+M M** / **Ctrl+M Y** | зробити клітинку текстом / кодом |
| **Ctrl+M H** | показати всі гарячі клавіші |

У Colab гарячі клавіші Jupyter працюють через префікс **Ctrl+M** (на macOS — **⌘M** або **Ctrl+M**; точний варіант покаже **Ctrl+M H**): спершу натисни Ctrl+M, відпусти, потім літеру. Зліва на панелі: зміст ноутбука, пошук, **Files** (файли сесії) і **Secrets** (ключ 🔑).

### Середовище виконання (runtime)

Коли ти запускаєш першу клітинку, Colab виділяє тобі **віртуальну машину** в хмарі Google — середовище виконання. У ній працює кернел Python, тобто всі змінні, встановлені бібліотеки й завантажені файли.

- У безкоштовному Colab ноутбук працює **не довше 12 годин** поспіль, а при бездіяльності середовище від'єднується раніше. Ліміти не гарантовані й змінюються з часом.
- Після від'єднання **усе в пам'яті зникає**: змінні, встановлені через `%pip` пакети, файли в `/content`. Сам ноутбук (код і тексти) лишається.
- Меню **Runtime** (Середовище виконання):
    - **Restart session** (у старих інструкціях — Restart runtime) — перезапустити кернел: пам'ять очищається, файли лишаються;
    - **Run all** — виконати всі клітинки згори донизу;
    - **Disconnect and delete runtime** — повністю віддати віртуальну машину; наступний запуск почнеться «з нуля»;
    - **Change runtime type** — вибрати прискорювач (GPU T4 у безкоштовному плані — за наявності). Для задач курсу GPU не потрібен.

Після перезапуску виконай клітинки знову — найпростіше **Runtime → Run all**.

### Встановлення бібліотек

Популярні бібліотеки для даних у Colab уже встановлені. Перевірити:

```python
%pip show pandas
!python --version
```

Встановити бібліотеку, якої немає:

```python
%pip install назва-пакета
```

- `%pip` ставить пакет у Python, на якому працює ноутбук. `!pip install` зазвичай теж працює в Colab, але `%pip` — надійніший звичай, який однаково працює і в Colab, і в локальному Jupyter.
- Якщо бібліотеку **вже імпортували** в цьому сеансі, а тепер оновили — **Runtime → Restart session**: інакше Python використовуватиме стару версію з пам'яті.
- Встановлення живе лише до кінця сесії. Тримай клітинку з `%pip install …` **на початку** ноутбука, щоб наступного разу виконати її першою.

### Файли: завантаження, Google Drive

Робоча папка сесії — `/content`. Усе, що там лежить, **зникає** разом із середовищем виконання.

**Завантажити файл зі свого комп'ютера** — перетягни його на панель **Files** або з коду:

```python
from google.colab import files

uploaded = files.upload()      # відкриє вікно вибору файлу
print(list(uploaded))           # імена завантажених файлів
```

**Скачати файл із Colab** на комп'ютер: правий клік по файлу на панелі **Files → Download**, або `files.download("result.csv")`.

**Google Drive** — щоб файли не зникали між сесіями:

```python
from google.colab import drive

drive.mount("/content/drive")
```

Colab попросить дозволити доступ до Drive. Після цього твій Drive видно як папку `/content/drive/MyDrive/`: звідти можна читати дані й туди зберігати результати.

### Секрети: API-ключі без ключа в коді

Ключі й паролі **ніколи** не пишуть прямо в ноутбук: його можуть побачити інші. У Colab для цього є панель **Secrets** (іконка 🔑 зліва): додай секрет (ім'я + значення) і ввімкни для ноутбука доступ перемикачем. У коді:

```python
from google.colab import userdata

api_key = userdata.get("MY_API_KEY")
```

Секрети не потрапляють у ноутбук, коли ти ним ділишся.

### Термінал і команди оболонки

- Одна команда: `!` на початку рядка — `!ls`, `!pwd`, `!git clone …`.
- Повноцінний **термінал**: кнопка **Terminal** внизу ліворуч. З червня 2025 року термінал безкоштовний для всіх користувачів Colab.

### Colab чи Jupyter на своєму комп'ютері

| | Colab | Jupyter локально |
|---|---|---|
| Встановлення | нічого, лише браузер і Google-акаунт | Python + venv + `pip install jupyterlab` |
| Час роботи | обмежений, змінні зникають після від'єднання | скільки завгодно |
| Файли | тимчасові в `/content`, постійні — на Drive | твій диск |
| Бібліотеки | багато вже є, решта — `%pip` кожну сесію | ставиш один раз у venv |

Інструкція для свого комп'ютера — [Jupyter локально: Notebook і JupyterLab](jupyter.md).

## Здача домашки з Colab

Домашні роботи здаються через Pull Request із гілки твого fork (див. [Здача домашніх робіт](homework_workflow.md)). Щоб зберегти ноутбук із Colab одразу у свій fork:

1. File → **Save a copy in GitHub**.
2. Repository: **твій fork** (`<твій-логін>/PY-Course-Victor-Nikoriak-22-09-2026`), а не репозиторій викладача.
3. Branch: гілка домашки (наприклад, `homework-03`). Спершу створи її на GitHub або локально.
4. File path: **повний шлях** до файлу, який вказано в завданні, а не лише ім'я файлу.
5. Далі на GitHub відкрий Pull Request `homework-03 → main`.

## Ноутбуки, яким потрібні сусідні файли

Деякі уроки імпортують `.py`-файли або читають дані з тієї ж папки. Наприклад, ноутбук `file_json_example.ipynb` з уроку 14 читає `restaurant_info.txt` та `orders.csv`. У Colab є лише сам ноутбук, тому додай на його початок клітинку:

```python
!git clone --depth 1 https://github.com/NikoriakViktot/PY-Course-Victor-Nikoriak-22-09-2026.git course
%cd course/module_1/lessons/lesson_14_file_io_json
```

Шлях після `%cd` — це папка уроку, який ти відкрив.

## Помилка «Could not find … .ipynb»

Кнопка Colab зберігає повний шлях до файлу в репозиторії. Ця помилка означає, що за цим шляхом файлу немає: ноутбук перенесли, або кнопка веде на старий репозиторій курсу. Відкрий ноутбук через книгу курсу або вручну (спосіб 2) і повідом викладача.

## Для викладача: як не зламати посилання

- **Джерело правди — репозиторій на GitHub.** Кнопку Colab (перша клітинка з `id: view-in-github`) і `metadata.lms` генерує скрипт. Вручну їх не редагуй.
- **Зберігаєш зміни з Colab:** File → Save a copy in GitHub → репозиторій `NikoriakViktot/PY-Course-Victor-Nikoriak-22-09-2026`, гілка `main`. У полі **File path** вкажи повний шлях, наприклад `module_1/lessons/lesson_07_functions/note_lesson_07_functions.ipynb`. За замовчуванням Colab підставляє лише ім'я файлу, і тоді ноутбук потрапляє в корінь репозиторію: саме так посилання зламалися після переїзду зі старого курсу. Галочку «Include a link to Colaboratory» не знімай.
- **Додав, переніс або перейменував ноутбук** — запусти:

    ```bash
    python tools/sync_notebook_metadata.py
    ```

    Скрипт оновить кнопку Colab, `metadata.lms` (потік, модуль, номер і назву уроку, шлях), перетворить відносні посилання на абсолютні (у Colab відносні не працюють) і розставить кнопки Colab у книзі поруч із посиланнями на ноутбуки. GitHub Actions на кожен push і PR запускає `python tools/sync_notebook_metadata.py --check` і падає, якщо щось розсинхронізовано.
- **Номери й назви уроків** беруться з `tools/lessons_v5.json` (програма v5.0), модулі — з `course.json`.

## Джерела

- [Colab FAQ](https://research.google.com/colaboratory/faq.html) — ліміти безкоштовного Colab, від'єднання при бездіяльності
- [Overview of Colaboratory Features](https://colab.research.google.com/notebooks/basic_features_overview.ipynb) — клітинки, гарячі клавіші
- [External data: Local Files, Drive, Sheets, and Cloud Storage](https://colab.research.google.com/notebooks/io.ipynb) — `files.upload`, `drive.mount`
- Google Colab, [Colab Terminal Is Now Free For All Users](https://medium.com/google-colab/colab-terminal-is-now-free-for-all-users-9a10eaef2ca8) (червень 2025)
