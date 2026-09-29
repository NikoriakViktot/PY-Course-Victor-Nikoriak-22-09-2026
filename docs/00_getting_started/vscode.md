# VS Code для Python

**Visual Studio Code** — безкоштовний редактор коду від Microsoft. Сам по собі він «знає» лише текст, а Python, дебагер і ноутбуки додаються **розширеннями** (extensions). Легший за PyCharm і популярний у командах, де пишуть кількома мовами.

## Встановлення

1. Завантаж VS Code з [code.visualstudio.com](https://code.visualstudio.com/) і встанови.
2. Переконайся, що встановлено Python 3.10+ (урок 2, [Налаштування середовища](environment_setup.md)).
3. Відкрий папку проєкту: **File → Open Folder…** (наприклад, клон репозиторію курсу).

## Розширення для Python

Панель **Extensions** — **Ctrl+Shift+X** (macOS **⇧⌘X**). Шукай за назвою й перевіряй видавця.

| Розширення | Ідентифікатор | Навіщо |
|---|---|---|
| **Python** (Microsoft) | `ms-python.python` | головне: запуск, venv, тести; **автоматично** встановлює Pylance і Python Debugger |
| **Pylance** (Microsoft) | `ms-python.vscode-pylance` | підказки й автодоповнення, перевірка типів (ставиться разом з Python) |
| **Python Debugger** (Microsoft) | `ms-python.debugpy` | дебагер (ставиться разом з Python) |
| **Jupyter** (Microsoft) | `ms-toolsai.jupyter` | ноутбуки `.ipynb` прямо у VS Code |
| **Ruff** (Astral) | `charliermarsh.ruff` | лінтер і форматувальник: підсвічує помилки стилю й форматує за PEP 8 |

Для курсу досить **Python** і **Jupyter**; **Ruff** — коли захочеш автоформатування.

## Палітра команд

Майже все у VS Code робиться через **палітру команд** (Command Palette): **Ctrl+Shift+P** (macOS **⇧⌘P**) → почни вводити назву команди.

## Віртуальне середовище та інтерпретатор

- **Створити venv**: палітра → **Python: Create Environment** → **Venv** → вибери Python → за наявності `requirements.txt` VS Code запропонує одразу встановити залежності. Папка `.venv` з'явиться в проєкті.
- **Вибрати інтерпретатор** (наприклад, venv, створений у терміналі): палітра → **Python: Select Interpreter** → вибери шлях з `.venv`. Поточний інтерпретатор видно в рядку стану внизу або праворуч унизу.
- **Термінал**: **View → Terminal** (**Ctrl+`**). Новий термінал зазвичай автоматично активує вибране середовище — перевір `(.venv)` на початку рядка.

## Запуск і дебаг

- **Запустити файл**: кнопка ▶ **Run Python File in Terminal** угорі праворуч у редакторі.
- **Запустити виділені рядки**: виділи → **Shift+Enter** (виконаються в інтерактивному Python-терміналі).
- **Дебаг**: клікни зліва від номера рядка — червона крапка (breakpoint). Натисни **F5** → **Python Debugger → Python File**. Коли програма зупиниться, дивись розділи **VARIABLES** і **CALL STACK** зліва, керуй кнопками панелі дебагу (крок через рядок, крок усередину функції, продовжити).

## Ноутбуки Jupyter у VS Code

Потрібне розширення **Jupyter** і пакет `ipykernel` у середовищі:

```bash
pip install ipykernel
```

- Відкрий `.ipynb` з проєкту або створи новий: палітра → **Create: New Jupyter Notebook**.
- Угорі праворуч — **Select Kernel** → вибери Python з `.venv`.
- Клітинки виконуються **Shift+Enter** — як у Jupyter і Colab.

## Автоформатування при збереженні (Ruff)

Після встановлення розширення Ruff відкрий палітру → **Preferences: Open User Settings (JSON)** і додай:

```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```

Тепер при кожному збереженні `.py`-файл форматуватиметься за правилами, сумісними з PEP 8.

## PyCharm чи VS Code

| | PyCharm | VS Code |
|---|---|---|
| Налаштування | Python «з коробки» | Python через розширення |
| Вага | важчий, більше можливостей одразу | легший, розширюється під задачу |
| Для курсу | зручніший на старті: менше налаштувань | зручний, якщо вже користуєшся ним для інших мов |

Обидва підходять для всього курсу — обирай один і вивчи його гарячі клавіші. Детальний гайд по PyCharm — на сторінці [PyCharm](pycharm.md).

## Джерела

- [Python in Visual Studio Code](https://code.visualstudio.com/docs/languages/python), [Getting Started with Python in VS Code](https://code.visualstudio.com/docs/python/python-tutorial), [Quick Start Guide for Python](https://code.visualstudio.com/docs/python/python-quick-start)
- [Python environments in VS Code](https://code.visualstudio.com/docs/python/environments) — Create Environment, Select Interpreter
- [Running Python code](https://code.visualstudio.com/docs/python/run), [Python debugging in VS Code](https://code.visualstudio.com/docs/python/debugging)
- [Jupyter Notebooks in VS Code](https://code.visualstudio.com/docs/datascience/jupyter-notebooks), [Manage Jupyter Kernels in VS Code](https://code.visualstudio.com/docs/datascience/jupyter-kernel-management)
- Marketplace: [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python), [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance), [Python Debugger](https://marketplace.visualstudio.com/items?itemName=ms-python.debugpy); [Ruff для VS Code](https://github.com/astral-sh/ruff-vscode)
