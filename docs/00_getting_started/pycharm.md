# PyCharm: повний гайд для курсу

**PyCharm** — середовище розробки (IDE) для Python від компанії JetBrains. В одному вікні — редактор з підказками й перевіркою коду, запуск програм, дебагер, термінал, керування пакетами, Git і ноутбуки Jupyter. IDE — це інструмент, а не мова: той самий код працює і в PyCharm, і у VS Code, і в терміналі.

## Яку версію брати

З версії **2025.1** PyCharm Community і PyCharm Professional об'єднано в **один продукт — PyCharm**:

- **основні можливості безкоштовні**: редактор, запуск, дебагер, venv, пакети, Git, **ноутбуки Jupyter**. Для всього курсу цього досить;
- **Pro-підписка** додає веб-фреймворки (Django, Flask, FastAPI), роботу з базами даних, віддалені інтерпретатори (SSH, Docker, WSL), розширені можливості ноутбуків;
- після встановлення діє **безкоштовний місячний пробний період Pro**; після нього PyCharm лишається працювати в безкоштовному режимі;
- окремої Community Edition більше немає: 2025.2 — останній окремий реліз, далі — лише об'єднаний PyCharm.

!!! tip "Pro безкоштовно для студентів"
    JetBrains дає безкоштовні освітні ліцензії студентам і викладачам акредитованих навчальних програм тривалістю понад рік: підтвердження через університетську пошту, картку ISIC або GitHub Student Developer Pack. Подати заявку — на сторінці [Free JetBrains Student Pack](https://www.jetbrains.com/academy/student-pack/). Для нашого курсу Pro не обов'язковий: до модуля 4 (веб) вистачає безкоштовних можливостей.

## Встановлення

**Спосіб 1 — JetBrains Toolbox App** (рекомендований JetBrains). Це невелика програма, яка встановлює й оновлює IDE JetBrains:

- Windows — завантаж `.exe` зі сторінки [Toolbox App](https://www.jetbrains.com/toolbox-app/) і пройди майстер встановлення;
- macOS — завантаж `.dmg` (окремо для Intel і Apple Silicon) і перетягни Toolbox у **Applications**;
- Linux — завантаж архів `.tar.gz` і розпакуй.

У Toolbox знайди **PyCharm** → **Install**.

**Спосіб 2 — окремий інсталятор** зі сторінки [завантаження PyCharm](https://www.jetbrains.com/pycharm/download/).

Сам Python PyCharm не встановлює за тебе автоматично — встанови Python 3.10+ заздалегідь (див. урок 2 і [Налаштування середовища](environment_setup.md)).

## Перший проєкт із віртуальним середовищем

1. Запусти PyCharm → **New Project**.
2. Вкажи **Location** — папку проєкту (наприклад, `lesson_03`).
3. У блоці інтерпретатора вибери створення нового **virtualenv (venv)** і базовий Python 3.10+. PyCharm створить папку `.venv` усередині проєкту.
4. **Create**.

Щоб працювати з **клонованим репозиторієм курсу**: **Open** → вибери папку `PY-Course-Victor-Nikoriak-22-09-2026` → далі налаштуй інтерпретатор (наступний розділ).

## Інтерпретатор: який Python виконує код

Інтерпретатор проєкту — це Python (зазвичай з venv), яким PyCharm запускає код і в який ставить пакети. Поточний інтерпретатор видно в **правому нижньому куті** вікна; клік по ньому — швидка зміна.

Налаштувати через меню: **Settings** (Windows/Linux: **File → Settings**; macOS: **PyCharm → Settings**) → пункт **Python Interpreter** (розташування в дереві налаштувань залежить від версії, тому найпростіше ввести «interpreter» у пошук угорі вікна Settings) → **Add Interpreter → Add Local Interpreter**:

- **новий venv**: тип **Virtualenv** → нове середовище; галочку «Inherit packages from base interpreter» **не** став — тоді venv чистий, як і має бути;
- **наявний venv** (наприклад, створений у терміналі командою `python -m venv .venv`): вибери наявне середовище й вкажи шлях до Python:
    - Windows: `.venv\Scripts\python.exe`
    - macOS / Linux: `.venv/bin/python`

## Запуск коду

| Дія | Як |
|---|---|
| запустити поточний файл | правий клік у редакторі → **Run '<файл>'**, або зелений трикутник ▶ біля `if __name__ == "__main__":` |
| повторити останній запуск | **Shift+F10** (кнопка ▶ угорі праворуч) |
| запустити з дебагером | **Shift+F9** (кнопка з жуком) |
| інтерактивний Python | **Tools → Python Console** або кнопка **Python Console** внизу |

Кожен запуск створює **конфігурацію запуску** (Run/Debug Configuration) — її видно у списку біля кнопки ▶ угорі. Там можна задати аргументи командного рядка, робочу папку, змінні оточення: **Edit Configurations…**.

Результат з'являється у вікні **Run** внизу. Помилки (traceback) там клікабельні: клік по `File "...", line 12` переносить у потрібний рядок.

## Дебагер крок за кроком

Дебагер (debugger) дозволяє **зупинити програму** на потрібному рядку й подивитися значення всіх змінних. Це найкращий спосіб зрозуміти, чому код робить не те, що ти очікуєш.

1. **Точка зупинки (breakpoint)**: клікни на сірому полі зліва від номера рядка — з'явиться червона крапка. Або курсор у рядок і **Ctrl+F8** (macOS **⌘F8**).
2. Запусти з дебагером: **Shift+F9** або правий клік → **Debug '<файл>'**.
3. Програма зупиниться **перед** виконанням рядка з крапкою. Внизу відкриється вікно **Debug**: зліва — стек викликів (які функції зараз виконуються), справа — **Variables**, усі змінні та їхні значення.
4. Далі керуй виконанням:

| Клавіша | Команда | Що робить |
|---|---|---|
| **F8** | Step Over | виконати поточний рядок і перейти до наступного, **не заходячи** всередину функцій |
| **F7** | Step Into | зайти **всередину** функції, що викликається в рядку |
| **Shift+F7** | Smart Step Into | якщо в рядку кілька викликів — вибрати, в який зайти |
| **Alt+Shift+F7** | Step Into My Code | заходити лише у **свій** код, не в бібліотеки |
| **F9** | Resume | виконувати далі до наступної точки зупинки |

Порада: крок за кроком (F8) пройди цикл з уроку 6 і стеж у **Variables**, як змінюються лічильник і список — це дає інтуїцію, якої не дасть жоден `print`.

## Вбудований термінал

**Alt+F12** (або кнопка **Terminal** внизу) відкриває термінал у папці проєкту. Якщо інтерпретатор проєкту — venv і в **Settings → Tools → Terminal** увімкнено **Activate virtualenv**, venv у терміналі активується автоматично: на початку рядка буде `(.venv)`. Тут зручно запускати `git`, `pip`, `pytest`, `jupyter lab`.

## Встановлення пакетів

**Вікно Python Packages**: кнопка **Python Packages** зліва або меню **View → Tool Windows → Python Packages**.

1. Почни вводити назву пакета в пошук.
2. Вибери пакет → **Install** (остання версія) або вибери версію зі списку.

Пакет ставиться в **поточний інтерпретатор проєкту**. Альтернатива — вбудований термінал з активованим venv: `pip install назва` або `pip install -r requirements.txt`.

## Git у PyCharm

PyCharm уміє все, що потрібно для [здачі домашніх робіт](homework_workflow.md), без командного рядка:

| Дія | Як |
|---|---|
| створити / перемкнути гілку | клік по назві гілки у верхній панелі (віджет Git) → **New Branch…**, назва `homework-03`, галочка **Checkout branch** |
| коміт | **Ctrl+K** (macOS **⌘K**) → відміть файли → повідомлення коміту → **Commit** |
| push | **Ctrl+Shift+K** (macOS **⌘⇧K**) |
| коміт і одразу push | **Ctrl+Alt+K** / кнопка **Commit and Push…** у вікні коміту |
| історія, гілки | вікно **Git** (**Alt+9**) → вкладка **Log** |
| усі Git-дії | **Alt+`** (VCS Operations Popup) або меню **Git** |

Pull Request на GitHub створюй як завжди — на сайті GitHub після push.

## Ноутбуки Jupyter у PyCharm

Підтримка Jupyter — у безкоштовній частині PyCharm: відкрий `.ipynb` у проєкті, і PyCharm покаже клітинки з кнопками запуску, результати й підказки коду. Ноутбук виконується на **інтерпретаторі проєкту**, тому бібліотеки для ноутбука ставляться туди ж (вікно Python Packages або `%pip install` у клітинці). Розширені можливості (віддалені ноутбуки, SQL-клітинки, інтерактивні таблиці) — у Pro.

## Корисні налаштування

- **Шрифт і розмір**: Settings → Editor → Font.
- **PEP 8**: PyCharm перевіряє стиль «з коробки» — жовте підкреслення й підказки справа. Наведи курсор на підкреслене, щоб прочитати пояснення, і натисни **Alt+Enter** (macOS **⌥↩**) — PyCharm запропонує виправлення.
- **Автоформатування**: **Ctrl+Alt+L** (macOS **⌘⌥L**) — **Reformat Code**, розставляє відступи й пробіли за PEP 8.
- **Мова інтерфейсу, тема** — Settings → Appearance & Behavior.

## Гарячі клавіші, які варто вивчити першими

| Дія | Windows / Linux | macOS |
|---|---|---|
| знайти будь-що (файл, клас, налаштування) | **Shift** двічі | **Shift** двічі |
| знайти дію / команду меню | **Ctrl+Shift+A** | **⌘⇧A** |
| переформатувати код | **Ctrl+Alt+L** | **⌘⌥L** |
| закоментувати рядок | **Ctrl+/** | **⌘/** |
| дублювати рядок | **Ctrl+D** | **⌘D** |
| запуск / дебаг | **Shift+F10** / **Shift+F9** | див. Keymap |
| термінал | **Alt+F12** | див. Keymap |
| точка зупинки | **Ctrl+F8** | **⌘F8** |

Якщо сумніваєшся — **Find Action** (Ctrl+Shift+A) і введи назву дії англійською: PyCharm покаже і команду, і її гарячу клавішу. Повна шпаргалка для твоєї ОС — **Help → Keyboard Shortcuts PDF**.

## Плагіни

**Settings → Plugins → Marketplace** — пошук і встановлення, вкладка **Installed** — керування встановленими. Основне для курсу (Python, Git, Markdown, Jupyter) уже вбудоване. Став плагіни свідомо: кожен плагін уповільнює запуск IDE, а плагіни від невідомих авторів отримують доступ до твого коду.

## Джерела

- JetBrains: [Unified PyCharm overview](https://www.jetbrains.com/help/pycharm/unified-pycharm.html), [PyCharm 2025.1: Unified PyCharm…](https://blog.jetbrains.com/pycharm/2025/04/pycharm-2025-1/), [PyCharm Community Edition is discontinued](https://youtrack.jetbrains.com/articles/SUPPORT-A-4358/PyCharm-Community-Edition-is-discontinued-download-the-unified-PyCharm-instead)
- [Install PyCharm](https://www.jetbrains.com/help/pycharm/installation-guide.html), [Toolbox App: Installation](https://www.jetbrains.com/help/toolbox-app/installation.html)
- [Configure a virtualenv environment](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html), [Configure a Python interpreter](https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html)
- [Debug your first Python application](https://www.jetbrains.com/help/pycharm/debugging-your-first-python-application.html), [Step through the program](https://www.jetbrains.com/help/pycharm/stepping-through-the-program.html)
- [Install, uninstall, and upgrade packages](https://www.jetbrains.com/help/pycharm/installing-uninstalling-and-upgrading-packages.html), [Terminal settings](https://www.jetbrains.com/help/pycharm/settings-tools-terminal.html)
- [Commit and push changes to Git repository](https://www.jetbrains.com/help/pycharm/commit-and-push-changes.html), [Main version control shortcuts](https://www.jetbrains.com/help/pycharm/main-version-control-shortcuts.html)
- [PyCharm keyboard shortcuts](https://www.jetbrains.com/help/pycharm/mastering-keyboard-shortcuts.html)
- [Free educational licenses](https://sales.jetbrains.com/hc/en-gb/articles/207241195-Do-you-offer-free-educational-licenses-for-students-and-teachers)
