# 06. Пакетні менеджери і встановлення ПЗ

!!! info "Довідник бонус-уроку «Linux для розробника»"
    Розділ перевірено: кожну команду виконано в контейнерах Ubuntu, Debian і `python:3.12-slim`. Урок з вправами — [Бонус. Linux](../bonus_linux.md).

## Навіщо це потрібно

На сервері немає App Store і немає `.exe`-файлів. Щоб встановити Nginx, Python, PostgreSQL або будь-яку іншу програму — використовують **пакетний менеджер**. Для Python-бібліотек — `pip`.

Розуміти різницю між системними і Python-пакетами — важливо, щоб не ламати середовище і не плутатися, звідки береться та чи інша версія Python або Django.

---

## Два рівні пакетів

```mermaid
flowchart TD
    classDef step     fill:#eceff1,stroke:#546e7a,stroke-width:1px,color:#1a1a1a;
    classDef decision fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#1a1a1a;
    classDef success  fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1a1a1a;
    classDef error    fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#1a1a1a;
    classDef warning  fill:#fff8e1,stroke:#e65100,stroke-width:2px,color:#1a1a1a;

    OS["Операційна система<br>(Ubuntu)"] --> APT["apt — системні програми:<br>Nginx, Python, Git, PostgreSQL"]
    Python["Python-проєкт"] --> PIP["pip — Python-бібліотеки:<br>Django, requests, celery"]
    APT --> System["Встановлюється в /usr/bin,<br>/usr/lib — для всієї системи"]
    PIP --> Venv["Встановлювати у virtualenv<br>— ізольовано для проєкту"]

    class OS,Python,APT,PIP,System step
    class Venv success
```

> `apt` встановлює програми для операційної системи.
> `pip` встановлює Python-бібліотеки для Python-проєкту.

---

## apt — системний пакетний менеджер

### Оновлення списку пакетів

```bash
sudo apt update
```
Не встановлює нічого — тільки завантажує актуальний список доступних пакетів з репозиторіїв. Завжди виконуй перед `install`.

### Оновлення встановлених пакетів

```bash
sudo apt upgrade
```
Оновлює всі встановлені пакети до нових версій.

### Встановлення пакетів

```bash
sudo apt install nginx
sudo apt install python3
sudo apt install python3-venv
sudo apt install python3-pip
sudo apt install git
sudo apt install postgresql
sudo apt install redis-server
sudo apt install htop curl wget tree
```

### Видалення пакетів

```bash
sudo apt remove nginx            # видалити програму
sudo apt purge nginx             # видалити + конфігураційні файли
sudo apt autoremove              # видалити непотрібні залежності
```

### Пошук пакета

```bash
apt search nginx
apt show nginx                   # детальна інформація про пакет
dpkg -l | grep nginx             # чи встановлений пакет?
```

---

## pip — Python пакетний менеджер

### Встановлення бібліотек

> Команди нижче — всередині активованого virtualenv (див. далі). У системний Python на Ubuntu 23.04+ / Debian 12+ `pip install` не встановить нічого: `error: externally-managed-environment` (PEP 668).

```bash
pip install django
pip install django==4.2.0        # конкретна версія
pip install "django>=4.0,<5.0"  # діапазон версій
pip install django psycopg2-binary celery redis
```

### Робота з requirements.txt

```bash
pip freeze                       # список всіх встановлених пакетів
pip freeze > requirements.txt    # зберегти у файл

pip install -r requirements.txt  # встановити з файлу
```

### Інформація про пакет

```bash
pip show django                  # версія, залежності, розташування
pip list                         # всі встановлені пакети
pip list --outdated              # що можна оновити
```

---

## virtualenv — ізольоване Python-середовище

### Чому virtualenv важливий

Без virtualenv `pip install` ставив би пакети в системний Python (у старих Ubuntu так і було; з Ubuntu 23.04 / Debian 12 pip це блокує — `externally-managed-environment`). Це проблема:

- Проєкт А вимагає `Django==3.2`, Проєкт Б — `Django==4.2`. Конфлікт.
- Ти оновив бібліотеку для одного проєкту — зламав інший.
- На production сервері встановлена не та версія.

Virtualenv ізолює бібліотеки для кожного проєкту:

```mermaid
flowchart TD
    classDef step     fill:#eceff1,stroke:#546e7a,stroke-width:1px,color:#1a1a1a;
    classDef decision fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#1a1a1a;
    classDef success  fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1a1a1a;
    classDef error    fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#1a1a1a;
    classDef warning  fill:#fff8e1,stroke:#e65100,stroke-width:2px,color:#1a1a1a;

    System["Системний Python 3.11"] --> P1["project_A/.venv/<br>Django 3.2, pillow 9.0"]
    System --> P2["project_B/.venv/<br>Django 4.2, pillow 10.0"]
    System --> P3["project_C/.venv/<br>FastAPI, sqlalchemy"]

    class System step
    class P1,P2,P3 success
```

### Команди virtualenv

```bash
# Створити virtualenv
python3 -m venv .venv

# Активувати (Linux/Mac)
source .venv/bin/activate

# Деактивувати
deactivate

# Після активації — встановити залежності
pip install -r requirements.txt
```

Після активації ти побачиш `(.venv)` перед prompt:
```text
(.venv) student@ubuntu:~/myproject$
```

### Де зберігати virtualenv

- Завжди в директорії проєкту: `.venv/`
- Додай у `.gitignore` — не комітити

```bash
# .gitignore
.venv/
__pycache__/
*.pyc
.env
```

---

## Типова послідовність на новому сервері

```bash
# 1. Оновити систему
sudo apt update && sudo apt upgrade -y

# 2. Встановити системні залежності
sudo apt install python3 python3-venv python3-pip git nginx -y

# 3. Клонувати проєкт
git clone https://github.com/you/myproject.git
cd myproject

# 4. Створити virtualenv
python3 -m venv .venv
source .venv/bin/activate

# 5. Встановити Python-залежності
pip install -r requirements.txt
```

---

## Типові помилки початківців

**Помилка 1:** Запускати `pip install` без активованого virtualenv
> На Ubuntu 23.04+ / Debian 12+ отримаєш `error: externally-managed-environment` (PEP 668); на старіших системах бібліотека встановиться в системний Python. Не обходь це через `--break-system-packages` — створи й активуй `.venv`. Перевіряй: `which pip` — має вказувати на `.venv/bin/pip`.

**Помилка 2:** `pip: command not found`
> Використовуй `pip3` або `python3 -m pip`, або встанови через `sudo apt install python3-pip`.

**Помилка 3:** Не додати `.venv` у `.gitignore`
> Virtualenv містить тисячі файлів і важить десятки–сотні МБ. Не потрібно в Git.

**Помилка 4:** Забути `sudo apt update` перед `install`
> Без оновлення можеш встановити стару версію або отримати помилку "package not found".

---

## Практичне завдання

### Завдання 1
```bash
sudo apt update
sudo apt install tree htop -y
tree --version
htop --version
```
Переконайся, що обидві програми встановились.

### Завдання 2
```bash
mkdir ~/test_project && cd ~/test_project
python3 -m venv .venv
source .venv/bin/activate
pip install django
python -c "import django; print(django.__version__)"
pip freeze > requirements.txt
cat requirements.txt
deactivate
```
Прослідкуй кожен крок. Поясни, що відбувається.

### Завдання 3
Відкрий два термінали. В одному активуй virtualenv і введи `which python`. В іншому — без virtualenv (там `python` може не бути — тоді `which python3`). Порівняй результати.

---

## Самоперевірка

- [ ] Я розумію різницю між `apt` і `pip`
- [ ] Я можу встановити системну програму через `apt install`
- [ ] Я можу створити і активувати virtualenv
- [ ] Я розумію, навіщо virtualenv потрібен для кожного проєкту
- [ ] Я вмію зберегти і відновити залежності через `pip freeze` і `requirements.txt`

---

## Короткий підсумок

`apt` — для системних програм (Nginx, PostgreSQL, Git). `pip` — для Python-бібліотек (Django, requests). Virtualenv ізолює бібліотеки кожного проєкту. Завжди активуй `.venv` перед роботою з проєктом. Наступний крок — SSH і підключення до сервера.
