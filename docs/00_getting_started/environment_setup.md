# Налаштування середовища Python (venv)

Для кожного проєкту ми використовуємо **віртуальне середовище (venv)** — ізольований Python, який містить тільки бібліотеки курсу. Це потрібно, щоб:

- ✅ бібліотеки не конфліктували між проєктами
- ✅ у всіх студентів було однакове середовище
- ✅ ноутбуки працювали однаково


## 1. Перевір встановлений Python

Відкрий Terminal / PowerShell:

```bash
python --version
```

Якщо команда не працює:

```bash
python3 --version
```

Рекомендована версія: **Python 3.10+**

## 2. Створення віртуального середовища

Перейди у корінь проєкту:

```bash
cd your_project_folder
```

Створи середовище:

```bash
python -m venv .venv
```

(якщо не працює → використай `python3`)

Буде створено папку `.venv/`. ⚠️ Цю папку **не потрібно** додавати в Git.

## 3. Активація середовища

**🪟 Windows (PowerShell)**

```bash
.venv\Scripts\activate
```

Якщо виникла помилка виконання скриптів — виконай **один раз**:

```bash
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

і повтори активацію.

**🍎 macOS / 🐧 Linux**

```bash
source .venv/bin/activate
```

Після успішної активації у терміналі з'явиться `(.venv)` — це означає, що середовище активне.

## 4. Встановлення бібліотек курсу

Коли викладач надасть файл `requirements.txt`:

```bash
pip install -r requirements.txt
```

Перевірка:

```bash
pip list
```

## 5. Підключення venv у PyCharm

Коротко нижче; повний гайд — [PyCharm](pycharm.md) (а для VS Code — [VS Code](vscode.md)).

1. **File → Settings**
2. **Project → Python Interpreter**
3. **Add Interpreter → Existing Environment**
4. Обери:
   - Windows: `project_folder/.venv/Scripts/python.exe`
   - macOS/Linux: `project_folder/.venv/bin/python`
5. **OK**

## 6. Використання venv у Jupyter Notebook

Коротко нижче; докладно про запуск Jupyter, кернели й `%pip` — [Jupyter локально](jupyter.md).

Встанови Jupyter kernel:

```bash
pip install ipykernel
```

Додай середовище як kernel:

```bash
python -m ipykernel install --user --name python-course --display-name "Python Course (.venv)"
```

У Notebook: `Kernel → Change Kernel → Python Course (.venv)`

## 7. Ноутбуки із захищеними клітинками

На заняттях використовуються **protected cells**. Студенти:

- ✅ можуть запускати код
- ✅ можуть редагувати дозволені клітинки
- ❌ не повинні змінювати системні клітинки

Позначення: `🔒 DO NOT EDIT`

## 8. Деактивація середовища

Після завершення роботи:

```bash
deactivate
```

## 9. Чому venv не в Git

Віртуальне середовище **не додається** у Git (`.venv/` вже в `.gitignore` репозиторію), бо воно:

- містить локальні файли Python
- відрізняється на Windows / macOS / Linux
- може займати сотні мегабайт
- відтворюється автоматично через `requirements.txt`

👉 У репозиторій додається тільки код, а не середовище. Детальніше: [офіційна рекомендація GitHub](https://docs.github.com/en/get-started/getting-started-with-git/ignoring-files).
