"""
Таксі: як росте робота програми — демонстрація до уроку 8 (П1. Big O).

Запуск:
    pip install streamlit plotly
    streamlit run app.py

Логіка (дані, алгоритми, підрахунок кроків) — у taxi_core.py.
Тут лише інтерфейс: вибрати задачу → передбачити → запустити → порівняти.
"""
import inspect
import time

import plotly.graph_objects as go
import streamlit as st

from taxi_core import EXPERIMENTS, human_time

SLOW_COLOR = "#eb6834"
FAST_COLOR = "#2a78d6"

WHY = {
    "ids": (
        "Повільне рішення порівнює **кожну пару** номерів: для n поїздок це n·(n−1)/2 порівнянь. "
        "Подвоїли n — пар стало вчетверо більше. Швидке рішення дивиться на кожен номер один раз, "
        "а перевірка «чи бачили вже» в множині (`set`) — один крок."
    ),
    "drivers": (
        "`driver in tuesday` для **списку** виглядає як один крок, але всередині це цикл по всьому "
        "вівторку. Цикл у циклі — n·m кроків. Множина вівторка будується один раз (m кроків), "
        "після чого кожна перевірка — один крок: разом n + m."
    ),
    "clients": (
        "`client not in result` перевіряє список, який **росте**: чим більше клієнтів уже знайдено, "
        "тим довша перевірка. Допоміжна множина `seen` відповідає за один крок, "
        "а список `result` лише зберігає порядок."
    ),
    "repeat": (
        "Повільне рішення перебирає всі пари поїздок, навіть коли повтор уже знайдено: "
        "найкоротший може бути далі. Швидке пам'ятає у словнику, де кожен клієнт їздив "
        "востаннє, — найближчий повтор завжди поруч з останньою поїздкою."
    ),
}

RATIO_OPTIONS = ["×1 — не зміниться", "×2 — удвічі", "×4 — учетверо", "×8 — у 8 разів"]

DIAGNOSIS_OPTIONS = [
    "CPU перевантажений зайвими порівняннями",
    "Серверу не вистачило оперативної пам’яті",
    "База даних відповідала надто повільно",
    "Зникло мережеве з’єднання",
]

ALGORITHM_STORIES = {
    "ids": {
        "data": ["1042", "2087", "3510", "1042"],
        "slow": ["Взяти № 1042", "Порівняти з усіма далі", "Повторити для кожного №"],
        "fast": ["Взяти № 1042", "Перевірити множину seen", "Запам’ятати й іти далі"],
        "slow_note": "Кожна поїздка шукає пару серед решти — утворюється дедалі більше пар.",
        "fast_note": "Множина seen працює як миттєвий журнал: номер або вже є, або його ще не бачили.",
    },
    "drivers": {
        "data": ["D-014", "D-027", "D-031", "D-014"],
        "slow": ["Взяти водія понеділка", "Шукати у всьому вівторку", "Повторити для кожного"],
        "fast": ["Зібрати set вівторка", "Перевірити одного водія", "Додати збіг до результату"],
        "slow_note": "Пошук у списку щоразу починається спочатку — це прихований внутрішній цикл.",
        "fast_note": "Список вівторка перетворюється на множину один раз, далі перевірка швидка.",
    },
    "clients": {
        "data": ["C-12", "C-08", "C-12", "C-31"],
        "slow": ["Взяти клієнта", "Шукати у result", "Якщо нового — додати"],
        "fast": ["Взяти клієнта", "Перевірити seen", "Додати у seen і result"],
        "slow_note": "Список result росте, тому кожна наступна перевірка може ставати довшою.",
        "fast_note": "seen швидко відповідає «вже був?», а result лише зберігає правильний порядок.",
    },
    "repeat": {
        "data": ["C-12", "C-08", "C-31", "C-12"],
        "slow": ["Взяти пару поїздок", "Перевірити клієнтів", "Зберегти найменшу відстань"],
        "fast": ["Взяти клієнта", "Знайти останню поїздку", "Оновити позицію у словнику"],
        "slow_note": "Алгоритм перевіряє всі можливі пари, щоб не пропустити найближче повернення.",
        "fast_note": "Словник пам’ятає лише останню позицію — саме вона дає найближчу можливу пару.",
    },
}

MISSION_STORIES = {
    "ids": {
        "day": "Понеділок · зміна №1",
        "clock": "08:03",
        "wakeup": "Ти тільки поставив каву, а телефон уже показує 27 пропущених сповіщень. Після нічного імпорту диспетчерська відкриває журнал — і сторінка зависає.",
        "client": "Олена · керівниця диспетчерської",
        "ticket_title": "Перевірка дубльованих номерів після імпорту",
        "context": "Щоночі ми імпортуємо поїздки партнерських автопарків. Іноді партнер повторно надсилає вже створений trip_id. Через це оплата або маршрут можуть прив’язатися не до тієї поїздки.",
        "task": "Реалізувати функцію, яка отримує список номерів поїздок і повертає True, якщо хоча б один номер зустрічається повторно. Якщо всі номери унікальні, повернути False.",
        "example_story": "О 00:14 файл partner_west.csv створив поїздку №781245. О 00:19 партнер повторно надіслав той самий пакет, і №781245 з’явився в журналі вдруге. Перевірка має зупинити пакет до нарахування оплати.",
        "example": "[781245, 781311, 781402, 781245]  →  True",
        "first_thought": "Візьму перший номер і порівняю з усіма наступними. Потім візьму другий і знову порівняю з усіма. Так я точно не пропущу повтор.",
        "first_assumption": "Тести проходять, відповідь правильна, додаткові структури даних не потрібні. Значить, можна віддавати задачу.",
        "why": "Повторний ID може пов’язати оплату, водія й маршрут не з тією поїздкою. Це вже не просто повільний екран, а ризик помилкових грошей і підтримки.",
        "done": ["повертає True або False", "не змінює журнал", "працює на 100 000 поїздок", "відповідає до таймауту API"],
        "hidden": "На тестових 1 000 записах перебір усіх пар здавався нормальним. Після нічного імпорту журнал виріс у 100 разів, а кількість пар — майже у 10 000 разів.",
        "incident": "Нічний імпорт завершився успішно, але ранкова перевірка повторних номерів зайняла всі ядра CPU. Нові API-запити стали в чергу.",
        "impact": "Диспетчери не можуть підтвердити поїздки, водії телефонують у підтримку, клієнти бачать помилки оплати.",
    },
    "drivers": {
        "day": "Вівторок · зміна №2",
        "clock": "07:56",
        "wakeup": "Будильник ніби дзвонить вдруге: учора ти вже рятував сервер. Сьогодні панель знову червона — ранкова зміна не може розподілити водіїв.",
        "client": "Максим · операційний менеджер",
        "ticket_title": "Виявлення водіїв, записаних у дві зміни",
        "context": "Планувальник формує окремі списки водіїв на понеділок і вівторок. Після ручного редагування один водій може випадково залишитися в обох списках і вийти на дві зміни поспіль.",
        "task": "Реалізувати функцію, яка отримує два списки ID водіїв і повертає тих, хто є в обох списках. Порядок результату має відповідати списку понеділка.",
        "example_story": "Водій D-014 є у плані понеділка 08:00–20:00 і через помилку диспетчера також потрапив у план вівторка 06:00–18:00. Система має показати D-014 до публікації розкладу.",
        "example": "['D-014', 'D-027'], ['D-031', 'D-014']  →  ['D-014']",
        "first_thought": "Пройду список понеділка й для кожного водія напишу driver in tuesday. Це читається просто, а Python сам знайде збіг.",
        "first_assumption": "У коді лише один видимий цикл, на тестових списках результат з’являється миттєво. Схоже на готове рішення.",
        "why": "Якщо водій випадково потрапив у дві зміни поспіль, зростає ризик втоми, помилок у графіку й нестачі машин в іншому районі.",
        "done": ["повертає список збігів", "кожен водій лише один раз", "порядок понеділка збережено", "дві великі зміни не блокують API"],
        "hidden": "Вираз driver in tuesday виглядає як одна дія, але для списку це прихований прохід. Для кожного водія понеділка сервер знову переглядає вівторок.",
        "incident": "Після підключення партнерського автопарку обидва списки виросли. Вкладений пошук виконує мільйони порівнянь, CPU забитий, формування графіка не завершується.",
        "impact": "Частина районів залишається без машин, а перевтомлені водії можуть отримати повторну зміну.",
    },
    "clients": {
        "day": "Середа · зміна №3",
        "clock": "08:11",
        "wakeup": "Ти заходиш до офісу й уже знаєш цей звук: сирена моніторингу. Маркетинг запустив ранкову кампанію, а разом із нею ліг сервіс журналу.",
        "client": "Ірина · CRM та маркетинг",
        "ticket_title": "Список отримувачів для CRM-кампанії",
        "context": "У журналі кожна поїздка містить ID клієнта, тому один клієнт зустрічається багато разів. CRM має надіслати повідомлення один раз і зберегти порядок першої появи клієнтів.",
        "task": "Реалізувати функцію, яка отримує послідовність ID клієнтів і повертає список без повторів. Перша поява визначає позицію клієнта в результаті.",
        "example_story": "Клієнт C-1207 здійснив три поїздки за місяць. У вибірці для SMS він трапляється тричі, але промокод потрібно надіслати лише один раз — у позиції його першої поїздки.",
        "example": "['C-1207', 'C-0844', 'C-1207', 'C-3102']  →  ['C-1207', 'C-0844', 'C-3102']",
        "first_thought": "Створю порожній result. Для кожного клієнта перевірю client not in result і додам лише нового. Порядок збережеться автоматично.",
        "first_assumption": "Рішення коротке, зрозуміле й повертає саме той список, який попросив замовник. Інших проблем я поки не бачу.",
        "why": "Дублікати означають кілька однакових SMS одному клієнту, зайві витрати й скарги. Але сортувати список не можна — бізнесу важливий порядок першої появи.",
        "done": ["кожен клієнт один раз", "порядок першої появи", "вхідні дані не змінюються", "велика кампанія завершується швидко"],
        "hidden": "Перевірка client not in result щоразу проходить список результатів, який постійно росте. Чим успішніше кампанія збирає клієнтів, тим повільнішою стає наступна перевірка.",
        "incident": "Маркетинг завантажив історію за рік. Список унікальних клієнтів виріс, кожна нова перевірка стала довшою, CPU досяг 100%, а черга API продовжила рости.",
        "impact": "Кампанія зупинена, диспетчерська не бачить журнал, а повторний запуск ризикує надіслати дублікати.",
    },
    "repeat": {
        "day": "Четвер · зміна №4",
        "clock": "08:47",
        "wakeup": "Четвертий ранок поспіль починається однаково: кава, червоний алерт, 503. Аналітика лояльності запустила важкий звіт саме в годину пік.",
        "client": "Данило · продуктова аналітика",
        "ticket_title": "Найменша відстань між повторними поїздками клієнта",
        "context": "Аналітика хоче зрозуміти, як швидко клієнти повертаються. Журнал упорядкований за часом, а позиція елемента означає номер поїздки в загальній послідовності.",
        "task": "Для кожного повторного ID знайти різницю між позиціями двох його поїздок і повернути найменшу різницю. Якщо жоден клієнт не повторився, повернути -1.",
        "example_story": "C-1207 стоїть у журналі на позиціях 1 і 3, тому відстань між його замовленнями дорівнює 2. Це менше, ніж у C-0844, який повторився через 4 позиції.",
        "example": "['C-1207', 'C-0844', 'C-1207', 'C-3102', 'C-0844']  →  2",
        "first_thought": "Переберу всі пари поїздок. Якщо клієнти однакові, порахую відстань і залишу найменшу. Повний перебір гарантує правильну відповідь.",
        "first_assumption": "Алгоритм перевіряє всі варіанти, тому помилитися не може. На маленькому журналі він завершується швидко.",
        "why": "Команда хоче виміряти повернення клієнтів без календарних дат. Менша відстань між поїздками означає швидше повторне використання сервісу.",
        "done": ["повертає найменшу відстань", "-1, якщо повторів немає", "перевіряє весь журнал", "звіт не заважає живим поїздкам"],
        "hidden": "V1 порівнює кожну поїздку з усіма наступними. Навіть після знайденого повтору робота триває, бо десь далі може бути ще коротша пара.",
        "incident": "Плановий аналітичний звіт перебирає всі пари клієнтів на тому самому сервері, що обслуговує диспетчерів. Фонове завдання забрало весь CPU.",
        "impact": "Живі поїздки конкурують зі звітом за ресурси: диспетчери чекають, запити завершуються таймаутом.",
    },
}


def inject_styles():
    st.markdown(
        """
        <style>
        .block-container {padding-top: 2rem; padding-bottom: 4rem; max-width: 1180px;}
        .taxi-hero {
            display:grid; grid-template-columns:1.05fr .95fr; gap:28px; align-items:center;
            padding:30px; border-radius:28px; overflow:hidden; color:#16202a;
            background:linear-gradient(135deg,#fff9d9 0%,#fff1a8 52%,#ffd84d 100%);
            box-shadow:0 18px 50px rgba(92,72,0,.13); margin-bottom:22px;
        }
        .taxi-kicker {font-size:.78rem; letter-spacing:.13em; font-weight:800; text-transform:uppercase; color:#806500;}
        .taxi-hero h1 {font-size:clamp(2rem,4vw,3.7rem); line-height:1.02; margin:.45rem 0 .8rem; letter-spacing:-.04em;}
        .taxi-hero p {font-size:1.06rem; line-height:1.55; max-width:600px; margin:0;}
        .city-map {position:relative; min-height:275px; border-radius:22px; overflow:hidden; background:#dff2ef; border:1px solid rgba(25,47,45,.12);}
        .road-h,.road-v {position:absolute; background:#47535d; box-shadow:inset 0 0 0 7px #5d6871;}
        .road-h {left:-5%; right:-5%; height:58px; top:108px; transform:rotate(-7deg);}
        .road-v {top:-8%; bottom:-8%; width:58px; left:52%; transform:rotate(11deg);}
        .road-h:after {content:"";position:absolute;left:0;right:0;top:27px;border-top:3px dashed #f8d84b;}
        .road-v:after {content:"";position:absolute;top:0;bottom:0;left:27px;border-left:3px dashed #f8d84b;}
        .zone {position:absolute;padding:9px 12px;border-radius:12px;background:rgba(255,255,255,.88);font-size:.76rem;font-weight:750;box-shadow:0 5px 15px rgba(30,65,60,.12);}
        .z1{left:7%;top:12%}.z2{right:7%;top:12%}.z3{left:8%;bottom:11%}.z4{right:6%;bottom:10%}
        .taxi {position:absolute;font-size:2rem;filter:drop-shadow(0 5px 5px rgba(0,0,0,.22));z-index:3;animation:drive 4.5s ease-in-out infinite alternate;}
        .t1{left:12%;top:109px}.t2{right:15%;top:132px;animation-delay:-2.2s}.t3{left:51%;top:38px;animation-name:drive-vertical;animation-delay:-1s}
        @keyframes drive {from{transform:translateX(-10px)}to{transform:translateX(34px)}}
        @keyframes drive-vertical {from{transform:translateY(-10px) rotate(90deg)}to{transform:translateY(34px) rotate(90deg)}}
        .city-counter {position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:4;background:#17212b;color:white;border-radius:14px;padding:10px 14px;text-align:center;box-shadow:0 8px 22px rgba(0,0,0,.2);}
        .city-counter strong{display:block;color:#ffd84d;font-size:1.25rem}.city-counter span{font-size:.68rem;white-space:nowrap}
        .why-grid {display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:6px 0 28px;}
        .why-card {border:1px solid #e8e4d4;border-radius:17px;padding:16px;background:#fffefa;}
        .why-card b {display:block;margin:3px 0 5px;color:#17212b}.why-card span {color:#5d6470;font-size:.88rem;line-height:1.45}
        .section-eyebrow {font-size:.75rem;font-weight:850;letter-spacing:.12em;text-transform:uppercase;color:#8a6e00;margin-top:10px;}
        .algorithm-stage {display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:10px 0 20px;}
        .algo-card {position:relative;border-radius:20px;padding:20px 20px 20px 24px;border:1px solid;background:#fff;min-height:245px;color:#17212b;box-shadow:0 10px 30px rgba(0,0,0,.08);overflow:hidden;}
        .algo-card:before {content:"";position:absolute;left:0;top:0;bottom:0;width:6px;}
        .algo-slow {border-color:#ffc8b3;background:linear-gradient(145deg,#fff7f3 0%,#fff 72%);}
        .algo-slow:before {background:#eb6834;}
        .algo-fast {border-color:#b6d8ff;background:linear-gradient(145deg,#f1f8ff 0%,#fff 72%);}
        .algo-fast:before {background:#2a78d6;}
        .algo-title {display:flex;align-items:center;justify-content:space-between;margin-bottom:15px;font-weight:850;font-size:1.05rem;color:#17212b;}
        .badge {font-size:.75rem;padding:5px 9px;border-radius:999px}.algo-slow .badge{background:#ffe1d5;color:#9d3510}.algo-fast .badge{background:#dcecff;color:#165ea8}
        .flow {display:flex;align-items:stretch;gap:7px;margin:8px 0 15px;}
        .flow-step {flex:1;display:flex;align-items:center;justify-content:center;text-align:center;border-radius:12px;padding:14px 9px;background:#fff;border:1px solid #d9dee4;font-size:.8rem;font-weight:800;line-height:1.3;color:#26313c;box-shadow:0 4px 12px rgba(28,40,52,.06);}
        .arrow {align-self:center;color:#687481;font-weight:900;font-size:1.1rem}.algo-note{font-size:.9rem;line-height:1.5;color:#505c68;margin:0;font-weight:500}
        .trip-strip {display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:8px 0 17px;padding:13px 15px;border-radius:14px;background:#f3f5f7;}
        .trip-strip span {font-size:.78rem;color:#68707b}.trip-chip {background:white;border:1px solid #dfe3e7;border-radius:9px;padding:6px 9px;font-weight:750;color:#26313c!important;}
        .growth-legend {display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:26px;}
        .growth-box {border-radius:14px;padding:13px 15px;font-size:.88rem;line-height:1.4}.growth-box strong{font-size:1.1rem}
        .growth-slow{background:#fff0ea;color:#8f3212}.growth-fast{background:#eaf4ff;color:#175f9f}
        .mission-bar {display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:4px 0 18px;}
        .mission-pill {padding:7px 11px;border-radius:999px;background:#2a78d6;color:#fff;font-size:.78rem;font-weight:800;letter-spacing:.02em;}
        .mission-muted {padding:7px 11px;border-radius:999px;background:#252b35;color:#c9d0da;font-size:.78rem;font-weight:700;border:1px solid #3c4450;}
        .client-brief {display:grid;grid-template-columns:auto 1fr;gap:14px;align-items:start;padding:20px;border-radius:18px;background:#17212b;color:#f7f9fb;border:1px solid #333e49;margin:8px 0 20px;box-shadow:0 12px 30px rgba(0,0,0,.18);}
        .client-avatar {width:48px;height:48px;border-radius:14px;display:grid;place-items:center;background:#ffd84d;font-size:1.45rem;}
        .ticket-meta{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}.client-brief small{display:block;color:#9eabb8;font-size:.72rem;text-transform:uppercase;letter-spacing:.09em;font-weight:800}.brief-status{color:#ffd84d;font-size:.7rem;font-weight:850;white-space:nowrap}.ticket-title{color:#fff;font-size:1.18rem;font-weight:850;margin:7px 0 14px}.ticket-section{padding:11px 0;border-top:1px solid #34404c}.ticket-label{display:block;color:#7fb8f4;font-size:.68rem;text-transform:uppercase;letter-spacing:.1em;font-weight:850;margin-bottom:4px}.ticket-section p{margin:0;color:#d5dce3;line-height:1.5;font-size:.86rem}.ticket-example{display:inline-block;margin-top:9px;padding:8px 10px;border-radius:9px;background:#0e141a;color:#a7e4bd;font-family:monospace;font-size:.8rem;border:1px solid #303a44}.example-note{margin-top:7px!important;color:#84919e!important;font-size:.65rem!important;text-transform:none!important;letter-spacing:.02em!important}
        .morning-scene {display:grid;grid-template-columns:165px 1fr;gap:0;border-radius:20px;overflow:hidden;border:1px solid #3a424c;background:#171d25;margin:8px 0 16px;box-shadow:0 14px 35px rgba(0,0,0,.18);}
        .morning-clock {padding:22px;display:flex;flex-direction:column;justify-content:center;background:linear-gradient(150deg,#ff6548,#b62d26);color:#fff}.morning-clock small{font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;color:#ffd2c9;font-weight:800}.morning-clock strong{font-size:2rem;line-height:1;margin:7px 0}.morning-clock span{font-size:.72rem;color:#ffe0da}.morning-copy{padding:22px;color:#eef2f6}.morning-copy small{color:#ff8b78;font-size:.7rem;letter-spacing:.1em;font-weight:850;text-transform:uppercase}.morning-copy h3{color:#fff;margin:5px 0 7px;font-size:1.2rem}.morning-copy p{color:#bbc4ce;margin:0;line-height:1.55;font-size:.9rem}
        .story-context {display:grid;grid-template-columns:1.1fr .9fr;gap:12px;margin:0 0 16px}.context-card{padding:16px;border-radius:16px;border:1px solid #dfe3e8;background:#fff;color:#202a34}.context-card b{display:block;margin-bottom:6px;color:#202a34}.context-card p{margin:0;color:#5b6672;font-size:.84rem;line-height:1.5}.context-card.impact{background:#fff6f2;border-color:#ffd0c5}.context-card.impact b{color:#a13a24}
        .acceptance {padding:18px;border-radius:18px;background:#f4f6f8;border:1px solid #dce1e6;margin:0 0 18px;color:#222c36}.acceptance-head{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;margin-bottom:12px}.acceptance-head b{display:block;color:#222c36}.acceptance-head small{display:block;color:#687481;font-size:.75rem;margin-top:3px;line-height:1.35}.ticket-id{font-family:monospace;font-size:.7rem;background:#e2e7ec;color:#52606d;padding:4px 7px;border-radius:7px;white-space:nowrap}.acceptance-list{display:grid;grid-template-columns:1fr 1fr;gap:8px}.acceptance-item{padding:9px 11px;border-radius:10px;background:#fff;border:1px solid #e1e5e9;color:#36414c;font-size:.78rem}.acceptance-item:before{content:"✓";color:#19a267;font-weight:900;margin-right:7px}
        .hidden-constraint {display:flex;gap:12px;align-items:flex-start;padding:15px 17px;border-radius:15px;background:#fff8d9;border:1px solid #f1d46b;color:#604e08;margin-bottom:22px}.hidden-constraint strong{display:block;margin-bottom:3px}.hidden-constraint p{margin:0;font-size:.83rem;line-height:1.45;color:#6e5c18}.hidden-icon{font-size:1.25rem}
        .first-v1 {display:grid;grid-template-columns:72px 1fr;gap:16px;padding:20px;border-radius:20px;background:linear-gradient(145deg,#eef6ff,#fff);border:1px solid #b8d8fa;margin:8px 0 14px;color:#1e2a36}.first-avatar{width:60px;height:60px;border-radius:18px;display:grid;place-items:center;background:#2a78d6;color:#fff;font-size:1.8rem;box-shadow:0 8px 20px rgba(42,120,214,.22)}.first-copy small{display:block;color:#2a78d6;font-size:.7rem;letter-spacing:.1em;font-weight:850;text-transform:uppercase}.first-copy h3{margin:4px 0 7px;color:#17212b;font-size:1.15rem}.first-copy p{margin:0;color:#52606d;font-size:.88rem;line-height:1.5}.first-assumption{margin-top:10px!important;padding:10px 12px;border-radius:10px;background:#fff;color:#34414d!important;border-left:4px solid #2a78d6}.v1-verdict{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0 20px}.verdict-good,.verdict-bad{padding:12px 14px;border-radius:13px;font-size:.82rem;line-height:1.4}.verdict-good{background:#eaf8f0;color:#176b43;border:1px solid #bde5cf}.verdict-bad{background:#fff0eb;color:#94361e;border:1px solid #ffc9ba}.review-divider{padding:16px 18px;border-radius:15px;background:#242c36;color:#eef3f7;margin:8px 0 18px;border-left:5px solid #ffd84d}.review-divider b{display:block;color:#ffd84d;margin-bottom:4px}.review-divider span{font-size:.84rem;color:#c5cdd5;line-height:1.45}
        .system-shell {padding:23px;border-radius:22px;background:linear-gradient(145deg,#151b23,#202a34);border:1px solid #34404c;margin:8px 0 24px;color:#fff;}
        .system-heading {display:flex;justify-content:space-between;align-items:start;gap:20px;margin-bottom:18px}.system-heading h3{margin:0;color:#fff;font-size:1.2rem}.system-heading p{margin:5px 0 0;color:#aeb8c3;font-size:.85rem}.system-rule{padding:7px 10px;border-radius:10px;background:#2b3540;color:#ffd84d;font-size:.75rem;font-weight:800;white-space:nowrap}
        .system-flow {display:grid;grid-template-columns:repeat(5,1fr);gap:22px;align-items:stretch;}
        .system-node {position:relative;padding:15px 10px;border-radius:15px;background:#fff;color:#19232d;text-align:center;min-height:96px;display:flex;flex-direction:column;align-items:center;justify-content:center;border:2px solid transparent;}
        .system-node:not(:last-child):after {content:"→";position:absolute;right:-22px;top:34px;width:22px;color:#ffd84d;font-size:1.25rem;font-weight:900;}
        .system-node .node-icon{font-size:1.55rem}.system-node b{font-size:.82rem;margin-top:5px}.system-node span{font-size:.68rem;color:#65717c;margin-top:3px}.system-node.hot{border-color:#ff6b4a;box-shadow:0 0 0 4px rgba(255,107,74,.12)}.system-node.hot:before{content:"ВУЗЬКЕ МІСЦЕ";position:absolute;top:-10px;background:#ff5a3c;color:#fff;border-radius:999px;padding:3px 7px;font-size:.58rem;font-weight:900;letter-spacing:.07em}
        .system-lesson {margin-top:16px;padding:12px 14px;border-radius:12px;background:#11171d;color:#d7dee5;font-size:.83rem;line-height:1.45;border-left:4px solid #ffd84d}.system-lesson strong{color:#ffd84d}
        .incident {border-radius:22px;padding:22px;background:linear-gradient(135deg,#2b1718,#1d2229);border:1px solid #74363a;margin:10px 0 16px;color:#fff;}
        .incident-top {display:flex;align-items:center;justify-content:space-between;gap:15px;margin-bottom:16px}.incident-title{display:flex;align-items:center;gap:11px}.alarm{width:42px;height:42px;border-radius:50%;display:grid;place-items:center;background:#ff5b45;box-shadow:0 0 0 7px rgba(255,91,69,.12);font-size:1.2rem}.incident h3{margin:0;color:#fff}.incident p{margin:4px 0 0;color:#d0b7b7;font-size:.84rem}.incident-time{font-family:monospace;color:#ffb1a5;font-size:.78rem}
        .telemetry {display:grid;grid-template-columns:repeat(4,1fr);gap:9px}.telemetry-card{padding:12px;border-radius:13px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1)}.telemetry-card span{display:block;color:#b9bfc8;font-size:.68rem;text-transform:uppercase;letter-spacing:.08em}.telemetry-card strong{display:block;color:#fff;font-size:1.15rem;margin-top:3px}.telemetry-card.danger strong{color:#ff735d}.telemetry-card.ok strong{color:#6de0a5}
        .cause-grid {display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:10px 0 24px}.cause-card{padding:13px;border-radius:14px;background:#f4f6f8;color:#26313c;border:1px solid #dce1e6;font-size:.77rem;line-height:1.35}.cause-card b{display:block;font-size:.85rem;margin-bottom:4px}.cause-card span{color:#65717c}.cause-card.active{background:#fff1ed;border-color:#ff9b82}.cause-card.active b{color:#a43a20}
        @media(max-width:800px){.taxi-hero,.algorithm-stage{grid-template-columns:1fr}.why-grid{grid-template-columns:1fr}.growth-legend{grid-template-columns:1fr}.city-map{min-height:230px}.flow{flex-direction:column}.arrow{transform:rotate(90deg)}.client-brief{grid-template-columns:auto 1fr}.brief-status{grid-column:2}.system-flow{grid-template-columns:1fr}.system-node:not(:last-child):after{content:"↓";right:auto;left:50%;top:auto;bottom:-23px}.system-heading{flex-direction:column}.telemetry,.cause-grid{grid-template-columns:1fr 1fr}.morning-scene,.story-context{grid-template-columns:1fr}.morning-clock{min-height:130px}.acceptance-list,.v1-verdict{grid-template-columns:1fr}.first-v1{grid-template-columns:1fr}.first-avatar{width:52px;height:52px}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_city_intro():
    st.markdown(
        """
        <div class="mission-bar">
          <span class="mission-pill">SYSTEM QUEST</span>
          <span class="mission-muted">Рівень 1 · Побудуй</span>
          <span class="mission-muted">Рівень 2 · Знайди збій</span>
          <span class="mission-muted">Рівень 3 · Масштабуй</span>
        </div>
        <section class="taxi-hero">
          <div>
            <div class="taxi-kicker">Нова задача від замовника</div>
            <h1>Побудуй систему.<br>Переживи навантаження.</h1>
            <p>Ти — інженер сервісу таксі. Спочатку створи рішення, яке працює. Потім місто виросте, сервер почне падати, а тобі треба буде знайти вузьке місце й покращити систему.</p>
          </div>
          <div class="city-map" aria-label="Схема міста з таксі">
            <div class="road-h"></div><div class="road-v"></div>
            <div class="zone z1">Поділ</div><div class="zone z2">Оболонь</div>
            <div class="zone z3">Теремки</div><div class="zone z4">Позняки</div>
            <div class="taxi t1">🚕</div><div class="taxi t2">🚕</div><div class="taxi t3">🚕</div>
            <div class="city-counter"><strong>1 000 → 100 000</strong><span>поїздок на день</span></div>
          </div>
        </section>
        <div class="why-grid">
          <div class="why-card"><div>🧩</div><b>Бач систему</b><span>Визнач компоненти, потік даних і місце, де робота накопичується швидше, ніж виконується.</span></div>
          <div class="why-card"><div>🔎</div><b>Діагностуй фактами</b><span>CPU, RAM, база й мережа залишають різні сигнали. Не оптимізуй навмання.</span></div>
          <div class="why-card"><div>🚀</div><b>Будуй на зростання</b><span>Правильна відповідь — лише перша умова. Система має встигати і на великих даних.</span></div>
        </div>
        <div class="section-eyebrow">Карта системи · простеж потік одного запиту</div>
        <section class="system-shell">
          <div class="system-heading">
            <div><h3>З чого складається сервіс таксі?</h3><p>Система — це не тільки код. Це компоненти, зв’язки, ресурси й обмеження.</p></div>
            <div class="system-rule">Вхідний потік &gt; швидкість обробки = черга росте</div>
          </div>
          <div class="system-flow">
            <div class="system-node"><div class="node-icon">🚕</div><b>Місто</b><span>створює поїздки</span></div>
            <div class="system-node"><div class="node-icon">🌐</div><b>API</b><span>приймає запити</span></div>
            <div class="system-node hot"><div class="node-icon">⚙️</div><b>Алгоритм</b><span>обробляє журнал</span></div>
            <div class="system-node"><div class="node-icon">🗄️</div><b>Дані</b><span>зберігають поїздки</span></div>
            <div class="system-node"><div class="node-icon">🖥️</div><b>Диспетчер</b><span>чекає відповідь</span></div>
          </div>
          <div class="system-lesson"><strong>Інженерне питання:</strong> якщо місто надсилає 100 запитів за секунду, а алгоритм обробляє лише 40, куди подінуться ще 60? Вони стануть чергою, займуть пам’ять і зрештою дадуть таймаут.</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def show_client_brief(key):
    story = MISSION_STORIES[key]
    checklist = "".join(f'<div class="acceptance-item">{item}</div>' for item in story["done"])
    st.markdown(
        f"""
        <div class="section-eyebrow">Нова задача від замовника · {story['day']}</div>
        <div class="client-brief">
          <div class="client-avatar">👤</div>
          <div>
            <div class="ticket-meta"><small>{story['client']} · Taxi Control</small><span class="brief-status">● ДО РОБОТИ · HIGH</span></div>
            <div class="ticket-title">{story['ticket_title']}</div>
            <div class="ticket-section"><span class="ticket-label">Контекст</span><p>{story['context']}</p></div>
            <div class="ticket-section"><span class="ticket-label">Що потрібно зробити</span><p>{story['task']}</p></div>
            <div class="ticket-section"><span class="ticket-label">Приклад із робочої ситуації</span><p>{story['example_story']}</p><span class="ticket-example">{story['example']}</span><small class="example-note">Умовні дані для навчальної лабораторії</small></div>
          </div>
        </div>
        <div class="story-context">
          <div class="context-card"><b>🎯 Навіщо це бізнесу?</b><p>{story['why']}</p></div>
          <div class="context-card impact"><b>💥 Що станеться, якщо рішення не витримає?</b><p>{story['impact']}</p></div>
        </div>
        <div class="acceptance">
          <div class="acceptance-head"><div><b>Як зрозуміти, що задача виконана?</b><small>Замовник прийме роботу, якщо виконано всі умови нижче.</small></div><span class="ticket-id">TAXI-{1042 + list(MISSION_STORIES).index(key)}</span></div>
          <div class="acceptance-list">{checklist}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_first_v1(key, exp):
    story = MISSION_STORIES[key]
    st.markdown(
        f"""
        <div class="section-eyebrow">Сцена 1 · Перша версія рішення</div>
        <div class="first-v1">
          <div class="first-avatar">🧑‍💻</div>
          <div class="first-copy">
            <small>Моя перша думка</small>
            <h3>Зроблю найпростіше рішення, яке дає правильну відповідь</h3>
            <p>{story['first_thought']}</p>
            <p class="first-assumption">💭 «{story['first_assumption']}»</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.code(inspect.getsource(exp["slow"]), language="python")
    st.markdown(
        """
        <div class="v1-verdict">
          <div class="verdict-good"><b>✅ Функціонально правильно</b><br>На малих тестах відповідь збігається з вимогами замовника.</div>
          <div class="verdict-bad"><b>⚠️ Інженерно не готово</b><br>Ми ще не перевірили кількість кроків, великі дані та поведінку під навантаженням.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_review_intro():
    st.markdown(
        """
        <div class="section-eyebrow">Сцена 3 · Код-рев’ю після інциденту</div>
        <div class="review-divider"><b>Тепер порівнюємо дві версії</b><span>Перша версія дає правильну відповідь, але погано масштабується. Виправлена версія виконує ту саму задачу й витримує зростання міста.</span></div>
        """,
        unsafe_allow_html=True,
    )


def show_incident(key):
    story = MISSION_STORIES[key]
    st.markdown(
        f"""
        <div class="section-eyebrow">Сцена 2 · Наступного ранку сервер упав</div>
        <div class="morning-scene">
          <div class="morning-clock"><small>Моніторинг розбудив</small><strong>{story['clock']}</strong><span>● production недоступний</span></div>
          <div class="morning-copy"><small>Після релізу V1</small><h3>Ти приходиш на зміну — сервер уже лежить</h3><p>{story['wakeup']}</p></div>
        </div>
        <section class="incident">
          <div class="incident-top">
            <div class="incident-title"><div class="alarm">🚨</div><div><h3>Сервер не відповідає</h3><p>{story['incident']}</p></div></div>
            <div class="incident-time">INCIDENT #1042 · 08:47</div>
          </div>
          <div class="telemetry">
            <div class="telemetry-card danger"><span>CPU</span><strong>100%</strong></div>
            <div class="telemetry-card ok"><span>RAM</span><strong>38%</strong></div>
            <div class="telemetry-card ok"><span>База даних</span><strong>12 ms</strong></div>
            <div class="telemetry-card danger"><span>Черга запитів</span><strong>+840/с</strong></div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def show_diagnosis_explanation(key):
    story = MISSION_STORIES[key]
    st.markdown(
        f"""
        <div class="section-eyebrow">Розбір після вашої відповіді</div>
        <div class="cause-grid">
          <div class="cause-card active"><b>🔥 CPU / алгоритм — причина цього інциденту</b><span>CPU = 100% і черга росте. Сервер витрачає час на зайві порівняння та не встигає приймати нові запити.</span></div>
          <div class="cause-card"><b>🧠 Пам’ять — не цього разу</b><span>RAM = 38%. Немає ознак, що процес завершився через нестачу пам’яті.</span></div>
          <div class="cause-card"><b>🗄️ База даних — не цього разу</b><span>12 ms — нормальна відповідь. API не чекає на повільний запит або блокування.</span></div>
          <div class="cause-card"><b>🔌 Мережа — не цього разу</b><span>Запити доходять до сервера і стають у чергу, отже мережевий шлях працює.</span></div>
        </div>
        <div class="hidden-constraint"><div class="hidden-icon">⚠️</div><div><strong>Проблема, якої не було видно в початковому ТЗ</strong><p>{story['hidden']}</p></div></div>
        """,
        unsafe_allow_html=True,
    )


def show_algorithm_story(key):
    story = ALGORITHM_STORIES[key]
    chips = "".join(f'<span class="trip-chip">{item}</span>' for item in story["data"])

    def flow(items):
        return '<span class="arrow">→</span>'.join(
            f'<div class="flow-step">{index}. {item}</div>' for index, item in enumerate(items, 1)
        )

    st.markdown(
        f"""
        <div class="section-eyebrow">Як працюють алгоритми</div>
        <div class="trip-strip"><span>Фрагмент журналу:</span>{chips}</div>
        <div class="algorithm-stage">
          <div class="algo-card algo-slow">
            <div class="algo-title"><span>🐢 Повільне рішення</span><span class="badge">багато пар</span></div>
            <div class="flow">{flow(story['slow'])}</div>
            <p class="algo-note">{story['slow_note']}</p>
          </div>
          <div class="algo-card algo-fast">
            <div class="algo-title"><span>⚡ Швидке рішення</span><span class="badge">один прохід</span></div>
            <div class="flow">{flow(story['fast'])}</div>
            <p class="algo-note">{story['fast_note']}</p>
          </div>
        </div>
        <div class="growth-legend">
          <div class="growth-box growth-slow"><strong>O(n²): 2× даних → приблизно 4× кроків</strong><br>Кожен елемент порівнюється з багатьма іншими.</div>
          <div class="growth-box growth-fast"><strong>O(n): 2× даних → приблизно 2× кроків</strong><br>Алгоритм проходить журнал лише один раз.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def ratio_label(ratio):
    """Виміряне відношення → найближчий варіант відповіді."""
    return min(RATIO_OPTIONS, key=lambda option: abs(int(option[1]) - ratio))


def run_experiment(exp, sizes, on_progress=None):
    rows = []
    for index, n in enumerate(sizes):
        if on_progress:
            on_progress(index, len(sizes), n, "slow")
        args = exp["make_input"](n)
        start = time.perf_counter()
        cpu_start = time.process_time()
        slow_answer, slow_steps = exp["slow"](*args)
        slow_cpu_seconds = time.process_time() - cpu_start
        slow_seconds = time.perf_counter() - start
        if on_progress:
            on_progress(index, len(sizes), n, "fast")
        start = time.perf_counter()
        cpu_start = time.process_time()
        fast_answer, fast_steps = exp["fast"](*args)
        fast_cpu_seconds = time.process_time() - cpu_start
        fast_seconds = time.perf_counter() - start
        rows.append({
            "n": n,
            "slow_steps": slow_steps, "fast_steps": fast_steps,
            "slow_seconds": slow_seconds, "fast_seconds": fast_seconds,
            "slow_cpu_seconds": slow_cpu_seconds, "fast_cpu_seconds": fast_cpu_seconds,
            "same_answer": slow_answer == fast_answer,
        })
        if on_progress:
            on_progress(index + 1, len(sizes), n, "done")
    for previous, row in zip(rows, rows[1:]):
        row["slow_ratio"] = row["slow_steps"] / previous["slow_steps"]
        row["fast_ratio"] = row["fast_steps"] / previous["fast_steps"]
    return rows


def resource_chart(last):
    """Реальна частка процесорного часу під час останнього запуску; GPU цей код не використовує."""
    slow_cpu = min(100, 100 * last["slow_cpu_seconds"] / max(last["slow_seconds"], 1e-9))
    fig = go.Figure()
    for value, title, color, domain in (
        (slow_cpu, "CPU · повільний алгоритм", SLOW_COLOR, {"x": [0, 0.47], "y": [0, 1]}),
        (0, "GPU · алгоритм", "#7d8792", {"x": [0.53, 1], "y": [0, 1]}),
    ):
        fig.add_trace(go.Indicator(
            mode="gauge+number", value=value,
            number={"suffix": "%", "font": {"size": 30, "color": "#26313c"}},
            title={"text": title, "font": {"size": 14, "color": "#26313c"}}, domain=domain,
            gauge={
                "axis": {"range": [0, 100], "tickfont": {"color": "#52606d"}}, "bar": {"color": color},
                "steps": [
                    {"range": [0, 60], "color": "#eaf5ef"},
                    {"range": [60, 85], "color": "#fff2c6"},
                    {"range": [85, 100], "color": "#ffe2da"},
                ],
                "threshold": {"line": {"color": "#c73520", "width": 4}, "value": 90},
            },
        ))
    fig.update_layout(
        template="none", height=260, margin={"l": 25, "r": 25, "t": 45, "b": 15},
        paper_bgcolor="#fcfcfb", font={"color": "#26313c"},
    )
    return fig, slow_cpu


def queue_chart(last, incoming_rps):
    """Черга моделюється з реальної пропускної здатності виміряних алгоритмів."""
    slow_capacity = 1 / max(last["slow_seconds"], 1e-9)
    fast_capacity = 1 / max(last["fast_seconds"], 1e-9)
    seconds = list(range(31))
    slow_queue = [max(0, (incoming_rps - slow_capacity) * second) for second in seconds]
    fast_queue = [max(0, (incoming_rps - fast_capacity) * second) for second in seconds]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=seconds, y=slow_queue, name="повільне", mode="lines", fill="tozeroy",
        line={"color": SLOW_COLOR, "width": 3}, fillcolor="rgba(235,104,52,.18)",
    ))
    fig.add_trace(go.Scatter(
        x=seconds, y=fast_queue, name="швидке", mode="lines",
        line={"color": FAST_COLOR, "width": 3},
    ))
    fig.add_hline(
        y=100, line_dash="dash", line_color="#c73520", annotation_text="зона таймаутів",
        annotation_font_color="#9f2f1d", annotation_bgcolor="#fff4f0",
    )
    fig.update_layout(
        template="none", height=320, margin={"l": 10, "r": 15, "t": 45, "b": 10},
        title={"text": "Як росте черга запитів за 30 секунд", "font": {"color": "#26313c"}},
        xaxis={"title": "секунди", "tickfont": {"color": "#52606d"}, "title_font": {"color": "#52606d"}, "gridcolor": "#dfe4e8"},
        yaxis={"title": "запитів у черзі", "tickfont": {"color": "#52606d"}, "title_font": {"color": "#52606d"}, "gridcolor": "#dfe4e8"},
        plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb", font={"color": "#26313c"},
        legend={"orientation": "h", "y": 1.12, "font": {"color": "#26313c"}}, hovermode="x unified",
    )
    return fig, slow_capacity, fast_capacity, slow_queue[-1], fast_queue[-1]


def growth_chart(rows):
    ns = [r["n"] for r in rows]
    fig = go.Figure()
    for key, name, color in (("slow_steps", "повільне", SLOW_COLOR), ("fast_steps", "швидке", FAST_COLOR)):
        fig.add_trace(go.Scatter(
            x=ns, y=[r[key] for r in rows], name=name, mode="lines+markers+text",
            line={"color": color, "width": 2}, marker={"size": 9, "color": color},
            text=[""] * (len(ns) - 1) + [name], textposition="middle right",
            textfont={"color": "#52514e"},
            hovertemplate="n = %{x:,}<br>кроків: %{y:,}<extra>" + name + "</extra>",
        ))
    fig.update_layout(
        template="none", height=380, margin={"l": 10, "r": 90, "t": 10, "b": 10},
        xaxis={"title": "кількість поїздок n", "gridcolor": "#ecebe8", "tickfont": {"color": "#52606d"}, "title_font": {"color": "#52606d"}},
        yaxis={"title": "кроків", "gridcolor": "#ecebe8", "tickfont": {"color": "#52606d"}, "title_font": {"color": "#52606d"}},
        plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb", font={"color": "#26313c"}, hovermode="x unified",
        legend={"orientation": "h", "y": 1.08, "font": {"color": "#26313c"}},
    )
    return fig


st.set_page_config(page_title="Таксі: Big O", page_icon="🚕", layout="wide")
inject_styles()
show_city_intro()

key = st.selectbox(
    "Оберіть місію від замовника", list(EXPERIMENTS),
    format_func=lambda k: f"{EXPERIMENTS[k]['title']}",
)
exp = EXPERIMENTS[key]
show_client_brief(key)
show_first_v1(key, exp)

show_incident(key)
diagnosis = st.radio(
    "Яка причина найкраще пояснює ці показники?",
    DIAGNOSIS_OPTIONS,
    index=None,
    key=f"diagnosis-{key}",
)
if diagnosis == DIAGNOSIS_OPTIONS[0]:
    st.success("Діагноз підтверджено: CPU зайнятий обчисленнями, черга росте, а інші компоненти системи здорові.")
elif diagnosis is not None:
    st.warning("Ця причина можлива в інших інцидентах, але не збігається з телеметрією: RAM, база й мережа тут у нормі. Подивіться на CPU та чергу.")
if diagnosis is not None:
    show_diagnosis_explanation(key)

show_review_intro()
show_algorithm_story(key)

code_slow, code_fast = st.columns(2)
with code_slow:
    with st.expander("Перша версія — повільний код"):
        st.code(inspect.getsource(exp["slow"]), language="python")
with code_fast:
    with st.expander("Виправлення — швидкий код"):
        st.code(inspect.getsource(exp["fast"]), language="python")

st.subheader("Сцена 4 · Передбач навантаження")
st.write("Поїздок стало **вдвічі більше**. У скільки разів зросте кількість кроків?")
guess_slow_col, guess_fast_col = st.columns(2)
guess_slow = guess_slow_col.radio("Повільне рішення", RATIO_OPTIONS, index=None, key=f"gs-{key}")
guess_fast = guess_fast_col.radio("Швидке рішення", RATIO_OPTIONS, index=None, key=f"gf-{key}")

st.subheader("Сцена 5 · Запусти навантажувальний тест")
max_n = st.select_slider(
    "Найбільша кількість поїздок у досліді",
    options=[800, 1600, 3200, 6400], value=3200,
    help="Дослід запускає обидва рішення для n/8, n/4, n/2 і n — щоразу вдвічі більше.",
)
sizes = [max_n // 8, max_n // 4, max_n // 2, max_n]
ready = diagnosis is not None and guess_slow is not None and guess_fast is not None
if not ready:
    st.caption("Щоб відкрити тест, постав діагноз інциденту й обери обидва прогнози.")
if st.button("Запустити дослід", type="primary", disabled=not ready):
    load_progress = st.progress(0, text="Готуємо журнал поїздок…")
    phase_text = st.empty()

    def update_load_progress(completed, total, n, phase):
        percent = min(100, int(100 * completed / total))
        labels = {
            "slow": f"🐢 Повільний алгоритм обробляє n = {n:,}… CPU зайнятий порівняннями",
            "fast": f"⚡ Швидкий алгоритм обробляє n = {n:,}… один прохід журналу",
            "done": f"✅ Завершено вимірювання для n = {n:,}",
        }
        load_progress.progress(percent, text=labels[phase])
        phase_text.caption("Це справжній запуск Python-коду. Час і використаний процесорний час вимірюються, а не вигадуються.")

    st.session_state["result"] = (key, max_n, run_experiment(exp, sizes, update_load_progress))
    load_progress.progress(100, text="Навантажувальний тест завершено")

result = st.session_state.get("result")
if result and result[0] == key and result[1] == max_n and ready:
    rows = result[2]
    last = rows[-1]

    if all(r["same_answer"] for r in rows):
        st.success("Обидва рішення дали однакову відповідь для кожного n — вони однаково правильні.")
    else:
        st.error("Відповіді різні — в одному з рішень помилка.")

    st.subheader("Живий монітор сервера")
    incoming_rps = st.slider(
        "Скільки запитів надходить щосекунди?",
        min_value=1, max_value=100, value=25, step=1,
        help="Змініть трафік і подивіться, чи встигає сервер обробляти запити.",
        key=f"rps-{key}-{max_n}",
    )
    resource_fig, measured_cpu = resource_chart(last)
    queue_fig, slow_capacity, fast_capacity, slow_queue, fast_queue = queue_chart(last, incoming_rps)
    monitor_left, monitor_right = st.columns([0.9, 1.1])
    with monitor_left:
        st.plotly_chart(resource_fig, width="stretch")
        st.caption(
            f"CPU — реально виміряна частка процесорного часу Python під час запуску: {measured_cpu:.0f}% одного ядра. "
            "GPU = 0%, бо цей код не використовує CUDA/OpenCL і працює на процесорі."
        )
    with monitor_right:
        st.plotly_chart(queue_fig, width="stretch")

    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Вхідний трафік", f"{incoming_rps} зап./с")
    q2.metric("Повільне обробляє", f"{slow_capacity:.1f} зап./с")
    q3.metric("Черга через 30 с", f"{slow_queue:,.0f}")
    q4.metric("Швидке обробляє", f"{fast_capacity:,.0f} зап./с")
    if slow_queue >= 100:
        st.error("🔴 СЕРВЕР «ЗАВИСАЄ»: запити приходять швидше, ніж обробляються. Черга перетнула зону таймаутів, користувачі отримують 503.")
    elif slow_queue > 0:
        st.warning("🟠 Сервер ще відповідає, але черга вже росте. Наступний сплеск трафіку спричинить таймаути.")
    else:
        st.success("🟢 Сервер встигає: пропускна здатність більша за вхідний трафік, черга не росте.")
    st.caption(
        "Час алгоритмів і CPU виміряні під час цього запуску. Черга — модель сервера на основі виміряної "
        "пропускної здатності: вхідні запити мінус оброблені запити."
    )

    m1, m2, m3 = st.columns(3)
    m1.metric(f"Кроків при n = {last['n']:,}: повільне", f"{last['slow_steps']:,}")
    m2.metric("швидке", f"{last['fast_steps']:,}")
    m3.metric("Повільне робить більше в", f"{last['slow_steps'] / last['fast_steps']:,.0f} раз")

    st.info(
        "🛠️ **Рішення інциденту:** замінити алгоритм, який створює квадратичне навантаження на CPU, "
        "на один прохід із множиною або словником. Сервер обробляє більше запитів за той самий час, "
        "черга скорочується, а диспетчер отримує відповідь без таймауту."
    )

    st.plotly_chart(growth_chart(rows), width="stretch")

    st.dataframe(
        [
            {
                "n": r["n"],
                "повільне: кроки": r["slow_steps"],
                "повільне: × до попер.": round(r["slow_ratio"], 2) if "slow_ratio" in r else None,
                "швидке: кроки": r["fast_steps"],
                "швидке: × до попер.": round(r["fast_ratio"], 2) if "fast_ratio" in r else None,
                "час, мс (повільне / швидке)": f"{r['slow_seconds'] * 1000:.1f} / {r['fast_seconds'] * 1000:.2f}",
            }
            for r in rows
        ],
        width="stretch", hide_index=True,
    )

    measured_slow = ratio_label(last["slow_ratio"])
    measured_fast = ratio_label(last["fast_ratio"])
    for label, guess, measured in (("Повільне", guess_slow, measured_slow), ("Швидке", guess_fast, measured_fast)):
        if guess == measured:
            st.write(f"✅ {label}: прогноз «{guess}» підтвердився.")
        else:
            st.write(f"❌ {label}: ти передбачив «{guess}», а дослід показав «{measured}».")
    st.caption(
        "Кроки однакові на будь-якому комп'ютері. Мілісекунди — ні: запусти дослід ще раз, "
        "і час трохи зміниться, а кроки — ні. Тому Big O рахує кроки."
    )

    with st.expander("Чому так?", expanded=True):
        st.markdown(WHY[key])
        st.markdown(
            "- відношення **≈2** при подвоєнні n → робота росте як n → **O(n)**;\n"
            "- відношення **≈4** при подвоєнні n → робота росте як n² → **O(n²)**."
        )

    st.subheader("Фінал · Масштабуй систему")
    target = st.select_slider(
        "Скільки поїздок буде в журналі?",
        options=[10_000, 100_000, 1_000_000, 10_000_000], value=1_000_000,
        format_func=lambda v: f"{v:,}".replace(",", " "),
    )
    scale = target / last["n"]
    slow_estimate = last["slow_seconds"] * scale ** 2
    fast_estimate = last["fast_seconds"] * scale
    e1, e2 = st.columns(2)
    e1.metric("Повільне рішення чекатиме приблизно", human_time(slow_estimate))
    e2.metric("Швидке рішення чекатиме приблизно", human_time(fast_estimate))
    st.caption(
        f"Оцінка з досліду при n = {last['n']:,}: час O(n²) множимо на ({target:,} / {last['n']:,})², "
        "а час O(n) — на відношення без квадрата. На іншому комп'ютері секунди будуть інші, "
        "але різниця в тисячі разів лишиться."
    )
