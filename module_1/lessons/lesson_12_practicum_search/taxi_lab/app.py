"""
Таксі: чи треба перебирати все? — демонстрація до уроку 12 (П2. Пошук).

Запуск:
    pip install streamlit plotly numpy pandas sortedcontainers
    streamlit run app.py

Логіка (дані, алгоритми, готові інструменти, заміри) — у taxi_core.py.
Тут лише інтерфейс: дві вкладки — місії диспетчера і гонка пошуків.
"""
import inspect
import time

import plotly.graph_objects as go
import streamlit as st

from taxi_core import (
    EXPERIMENTS, GROWTH, POSITIONS, RACERS, READY_TOOLS, batch_race, human_time,
    measure_tools, race, race_data, sort_payoff, unsorted_trap,
)

SLOW_COLOR = "#eb6834"
FAST_COLOR = "#2a78d6"
LIB_COLORS = {
    "наш код": "#7d8792", "Python": "#2a78d6", "numpy": "#3d9970",
    "pandas": "#8e6cc8", "sortedcontainers": "#d4a017",
}
RACER_COLORS = {
    "Свій лінійний пошук": "#eb6834", "x in list": "#f2a541",
    "Свій бінарний пошук": "#2a78d6", "bisect.bisect_left": "#5aa9e6",
    "numpy.searchsorted": "#3d9970", "SortedList: x in": "#d4a017",
}

PROPERTY_OPTIONS = [
    "Нічого: записи в довільному порядку",
    "Відсортовані — шукаємо одне значення чи позицію",
    "Відсортовані — шукаємо пару",
    "Суцільні відрізки однакової довжини",
]
STRATEGIES = ["лінійний пошук", "бінарний пошук", "два вказівники", "ковзне вікно"]

RATIO_OPTIONS = ["+1 крок — майже не зміниться", "×2 — удвічі", "×4 — учетверо"]

GROWTH_TEXT = {
    "O(n)": "2× даних → приблизно ×2 кроків",
    "O(n²)": "2× даних → приблизно ×4 кроків",
    "O(n·k)": "2× даних і 2× довше вікно → приблизно ×4 кроків",
    "O(log n)": "2× даних → лише +1 крок",
    "O(n log n)": "2× даних → трохи більше ніж ×2",
}

WHY = {
    "time": (
        "Лінійний пошук не знає, що час відсортований, і перевіряє кожен запис: подвоїли журнал — "
        "подвоїлась робота. Бінарний пошук одним порівнянням із серединою відкидає **половину** журналу. "
        "Подвоїли дані — знадобився лише ще один поділ навпіл: **+1 крок**."
    ),
    "voucher": (
        "Перебір перевіряє кожну пару поїздок: n·(n−1)/2 пар, подвоїли n — пар учетверо більше. "
        "Два вказівники користуються порядком: якщо сума завелика навіть з найдешевшою поїздкою, "
        "найдорожчу можна відкинути назавжди. Кожен крок відкидає одну поїздку — щонайбільше n − 1 кроків."
    ),
    "peak": (
        "Наївна версія для кожного вікна заново додає k чисел. Тут вікно — чверть доби, тож коли журнал "
        "детальнішає вдвічі, удвічі більше і вікон, і чисел у кожному: ×4. Ковзне вікно отримує нову суму "
        "зі старої: одне значення випадає зліва, одне додається справа."
    ),
    "suggest": (
        "Перевірка всіх адрес зі `startswith` проходить увесь довідник, хоч підказок треба лише три. "
        "Але довідник відсортований: усі адреси на «Хр» стоять **підряд**. Бінарний пошук знаходить "
        "початок блоку за log n кроків, далі беремо трьох сусідів праворуч."
    ),
}

MISSION_STORIES = {
    "time": {
        "day": "Понеділок · зміна №1",
        "client": "Олена · служба підтримки",
        "ticket_title": "Перевірка скарги: «я їхав, а поїздки немає»",
        "context": "Клієнт пише, що поїздку з картки списано, а в застосунку її немає. Підтримка знає точну секунду списання й має перевірити журнал поїздок за місяць. Система дописує поїздки в журнал по черзі, тому моменти початку йдуть за зростанням.",
        "task": "Реалізувати функцію, яка отримує відсортований список моментів початку поїздок (секунди від початку місяця) і момент зі скарги. Повернути індекс поїздки або -1, якщо такої немає.",
        "example_story": "Списання о 18:40:00 першого дня — це 67 200 секунд від початку місяця. Якщо такого запису в журналі немає, скаргу передають у банк.",
        "example": "[25500, 30600, 67200, 75600], 67200  →  2",
        "first_thought": "Пройду журнал з початку і порівняю кожен запис із моментом зі скарги. Знайшов — повертаю індекс.",
        "first_assumption": "Пошук правильний, код на п'ять рядків. На тестовому журналі відповідь миттєва.",
        "why": "Підтримка обробляє сотні скарг на годину. Кожна перевірка, що проходить мільйон записів, — це хвилини очікування для клієнта.",
        "impact": "Черга скарг росте, клієнти чекають, а гроші повертаються із запізненням.",
        "done": ["індекс або -1", "журнал не змінюється", "мільйон записів за мить", "працює для будь-якого моменту"],
    },
    "voucher": {
        "day": "Вівторок · зміна №2",
        "client": "Максим · програма лояльності",
        "ticket_title": "Ваучер покриває рівно дві поїздки",
        "context": "Клієнтам видають ваучер на фіксовану суму. Його можна використати на дві поїздки, якщо їхня сума дорівнює номіналу. Суми поїздок за тиждень у звіті вже відсортовані.",
        "task": "Знайти дві поїздки, сума яких дорівнює номіналу ваучера. Повернути пару сум або None, якщо такої пари немає.",
        "example_story": "Ваучер на 500 грн: поїздки 180 і 320 грн дають рівно 500. Якщо пари немає, клієнт отримує пропозицію на іншу суму.",
        "example": "[120, 150, 180, 230, 270, 320, 410], 500  →  (180, 320)",
        "first_thought": "Переберу всі пари поїздок: першу з кожною наступною. Як тільки сума збіглася — повертаю пару.",
        "first_assumption": "Повний перебір нічого не пропустить. На семи поїздках це 21 пара — дрібниця.",
        "why": "Акцію запускають для всіх корпоративних клієнтів одночасно. У великих компаній тисячі поїздок за тиждень.",
        "impact": "Розсилка ваучерів не встигає до ранку, а клієнти отримують пропозиції із запізненням на добу.",
        "done": ["пара або None", "сума рівно номінал", "суми не сортуються заново", "тисячі поїздок за мить"],
    },
    "peak": {
        "day": "Середа · зміна №3",
        "client": "Ірина · планування змін",
        "ticket_title": "Коли виводити підсилення водіїв",
        "context": "Підсилення водіїв виходить на шість годин поспіль — чверть доби. Треба знайти, з якого моменту почати, щоб ці шість годин були найзавантаженішими. Дані бувають погодинні, поминутні або посекундні.",
        "task": "Отримати список кількості поїздок за проміжками доби і довжину вікна k. Повернути (початок вікна, сума поїздок у ньому) для найзавантаженішого вікна.",
        "example_story": "Погодинно найзавантаженіші три години — з 17:00 до 20:00: 45 + 52 + 38 = 135 поїздок.",
        "example": "per_hour, k = 3  →  (17, 135)",
        "first_thought": "Для кожного можливого початку порахую sum() вікна й залишу найбільшу суму.",
        "first_assumption": "sum() — вбудована функція, вона швидка. Код короткий і точно правильний.",
        "why": "Що детальніші дані (хвилини замість годин), то точніше вибирається початок зміни — і то більше роботи.",
        "impact": "Розрахунок на посекундних даних не завершується до початку зміни — водіїв виводять навмання.",
        "done": ["початок і сума вікна", "при рівних сумах — найраніше", "поминутні дані за мить", "будь-яке k"],
    },
    "suggest": {
        "day": "Четвер · зміна №4",
        "client": "Данило · мобільний застосунок",
        "ticket_title": "Підказки адреси під час набору",
        "context": "Після кожної літери, яку набирає пасажир, застосунок показує три підказки адреси. Довідник адрес відсортований за абеткою і містить сотні тисяч записів.",
        "task": "Отримати відсортований довідник адрес і префікс, який набрав пасажир. Повернути перші три адреси, що починаються з цього префікса.",
        "example_story": "Пасажир набрав «Хр» — застосунок має одразу показати «Хрещатик, 1», «Хрещатик, 12», «Хрещатик, 15».",
        "example": "streets, 'Хр'  →  ['Хрещатик, 1', 'Хрещатик, 12', ...]",
        "first_thought": "Пройду довідник і для кожної адреси перевірю startswith. Збіги складу в список і поверну перші три.",
        "first_assumption": "startswith вбудований і швидкий. Код читається як речення.",
        "why": "Підказка має з'явитися раніше, ніж пасажир набере наступну літеру. Кожна літера — новий пошук.",
        "impact": "Підказки запізнюються, пасажир набирає адресу вручну з помилками, водій їде не туди.",
        "done": ["не більше трьох підказок", "порядок за абеткою", "кожна літера — без затримки", "порожній список, якщо збігів немає"],
    },
}

ALGORITHM_STORIES = {
    "time": {
        "data": ["25500", "30600", "41200", "67200", "75600"],
        "slow": ["Взяти перший запис", "Порівняти з моментом", "Іти до наступного"],
        "fast": ["Взяти середину", "Менше? Відкинути ліву половину", "Повторити на половині"],
        "slow_note": "Не користується порядком: момент може бути де завгодно — перевіряємо все.",
        "fast_note": "Кожне порівняння відкидає половину журналу, що лишився.",
        "slow_badge": "кожен запис", "fast_badge": "половина за крок",
    },
    "voucher": {
        "data": ["120", "150", "180", "230", "270", "320", "410"],
        "slow": ["Взяти поїздку", "Скласти з кожною наступною", "Повторити для всіх"],
        "fast": ["Лівий — найдешевша, правий — найдорожча", "Замало → лівий праворуч", "Забагато → правий ліворуч"],
        "slow_note": "Кількість пар росте як квадрат кількості поїздок.",
        "fast_note": "Кожен крок назавжди відкидає одну поїздку.",
        "slow_badge": "усі пари", "fast_badge": "назустріч",
    },
    "peak": {
        "data": ["…", "33", "45", "52", "38", "24", "…"],
        "slow": ["Взяти початок вікна", "sum() k чисел", "Зсунутися на 1 і знову sum()"],
        "fast": ["Порахувати перше вікно", "Додати нове справа", "Відняти старе зліва"],
        "slow_note": "Сусідні вікна майже однакові, але сума щоразу рахується з нуля.",
        "fast_note": "Нова сума = стара + одне значення − одне значення.",
        "slow_badge": "k додавань на вікно", "fast_badge": "2 дії на зсув",
    },
    "suggest": {
        "data": ["Жилянська, 7", "Хорива, 3", "Хрещатик, 1", "Хрещатик, 12", "Шота Руставелі, 9"],
        "slow": ["Взяти адресу", "startswith('Хр')?", "Іти до кінця довідника"],
        "fast": ["bisect: де почалися б «Хр»", "Взяти сусіда праворуч", "Стоп після трьох"],
        "slow_note": "Перевіряє весь довідник, хоч потрібні лише три адреси.",
        "fast_note": "Адреси з однаковим початком стоять підряд — достатньо знайти перший.",
        "slow_badge": "увесь довідник", "fast_badge": "log n + 3",
    },
}


def inject_styles():
    st.markdown(
        """
        <style>
        .block-container {padding-top: 2rem; padding-bottom: 4rem; max-width: 1180px;}
        .taxi-hero {display:grid; grid-template-columns:1.05fr .95fr; gap:28px; align-items:center; padding:30px; border-radius:28px; overflow:hidden; color:#16202a; background:linear-gradient(135deg,#fff9d9 0%,#fff1a8 52%,#ffd84d 100%); box-shadow:0 18px 50px rgba(92,72,0,.13); margin-bottom:22px;}
        .taxi-kicker {font-size:.78rem; letter-spacing:.13em; font-weight:800; text-transform:uppercase; color:#806500;}
        .taxi-hero h1 {font-size:clamp(2rem,4vw,3.4rem); line-height:1.04; margin:.45rem 0 .8rem; letter-spacing:-.04em; color:#16202a;}
        .taxi-hero p {font-size:1.04rem; line-height:1.55; max-width:600px; margin:0;}
        .q-table {display:grid; gap:8px;}
        .q-row {display:grid; grid-template-columns:1.2fr 1fr .9fr; gap:8px; align-items:center; padding:10px 12px; border-radius:13px; background:rgba(255,255,255,.82); font-size:.8rem; color:#26313c; box-shadow:0 4px 12px rgba(92,72,0,.08);}
        .q-row b {color:#17212b}.q-row span {color:#5d6470}.q-row i {font-style:normal; font-weight:800; color:#165ea8; text-align:right}
        .section-eyebrow {font-size:.75rem;font-weight:850;letter-spacing:.12em;text-transform:uppercase;color:#8a6e00;margin-top:10px;}
        .client-brief {display:grid;grid-template-columns:auto 1fr;gap:14px;align-items:start;padding:20px;border-radius:18px;background:#17212b;color:#f7f9fb;border:1px solid #333e49;margin:8px 0 20px;box-shadow:0 12px 30px rgba(0,0,0,.18);}
        .client-avatar {width:48px;height:48px;border-radius:14px;display:grid;place-items:center;background:#ffd84d;font-size:1.45rem;}
        .ticket-meta{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}.client-brief small{display:block;color:#9eabb8;font-size:.72rem;text-transform:uppercase;letter-spacing:.09em;font-weight:800}.brief-status{color:#ffd84d;font-size:.7rem;font-weight:850;white-space:nowrap}.ticket-title{color:#fff;font-size:1.18rem;font-weight:850;margin:7px 0 14px}.ticket-section{padding:11px 0;border-top:1px solid #34404c}.ticket-label{display:block;color:#7fb8f4;font-size:.68rem;text-transform:uppercase;letter-spacing:.1em;font-weight:850;margin-bottom:4px}.ticket-section p{margin:0;color:#d5dce3;line-height:1.5;font-size:.86rem}.ticket-example{display:inline-block;margin-top:9px;padding:8px 10px;border-radius:9px;background:#0e141a;color:#a7e4bd;font-family:monospace;font-size:.8rem;border:1px solid #303a44}
        .story-context {display:grid;grid-template-columns:1.1fr .9fr;gap:12px;margin:0 0 16px}.context-card{padding:16px;border-radius:16px;border:1px solid #dfe3e8;background:#fff;color:#202a34}.context-card b{display:block;margin-bottom:6px;color:#202a34}.context-card p{margin:0;color:#5b6672;font-size:.84rem;line-height:1.5}.context-card.impact{background:#fff6f2;border-color:#ffd0c5}.context-card.impact b{color:#a13a24}
        .acceptance {padding:18px;border-radius:18px;background:#f4f6f8;border:1px solid #dce1e6;margin:0 0 18px;color:#222c36}.acceptance-head{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;margin-bottom:12px}.acceptance-head b{display:block;color:#222c36}.acceptance-head small{display:block;color:#687481;font-size:.75rem;margin-top:3px}.ticket-id{font-family:monospace;font-size:.7rem;background:#e2e7ec;color:#52606d;padding:4px 7px;border-radius:7px;white-space:nowrap}.acceptance-list{display:grid;grid-template-columns:1fr 1fr;gap:8px}.acceptance-item{padding:9px 11px;border-radius:10px;background:#fff;border:1px solid #e1e5e9;color:#36414c;font-size:.78rem}.acceptance-item:before{content:"✓";color:#19a267;font-weight:900;margin-right:7px}
        .first-v1 {display:grid;grid-template-columns:72px 1fr;gap:16px;padding:20px;border-radius:20px;background:linear-gradient(145deg,#eef6ff,#fff);border:1px solid #b8d8fa;margin:8px 0 14px;color:#1e2a36}.first-avatar{width:60px;height:60px;border-radius:18px;display:grid;place-items:center;background:#2a78d6;color:#fff;font-size:1.8rem}.first-copy small{display:block;color:#2a78d6;font-size:.7rem;letter-spacing:.1em;font-weight:850;text-transform:uppercase}.first-copy h3{margin:4px 0 7px;color:#17212b;font-size:1.15rem}.first-copy p{margin:0;color:#52606d;font-size:.88rem;line-height:1.5}.first-assumption{margin-top:10px!important;padding:10px 12px;border-radius:10px;background:#fff;color:#34414d!important;border-left:4px solid #2a78d6}
        .v1-verdict{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0 20px}.verdict-good,.verdict-bad{padding:12px 14px;border-radius:13px;font-size:.82rem;line-height:1.4}.verdict-good{background:#eaf8f0;color:#176b43;border:1px solid #bde5cf}.verdict-bad{background:#fff0eb;color:#94361e;border:1px solid #ffc9ba}
        .review-divider{padding:16px 18px;border-radius:15px;background:#242c36;color:#eef3f7;margin:8px 0 18px;border-left:5px solid #ffd84d}.review-divider b{display:block;color:#ffd84d;margin-bottom:4px}.review-divider span{font-size:.84rem;color:#c5cdd5;line-height:1.45}
        .algorithm-stage {display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:10px 0 20px;}
        .algo-card {position:relative;border-radius:20px;padding:20px 20px 20px 24px;border:1px solid;background:#fff;min-height:230px;color:#17212b;box-shadow:0 10px 30px rgba(0,0,0,.08);overflow:hidden;}
        .algo-card:before {content:"";position:absolute;left:0;top:0;bottom:0;width:6px;}
        .algo-slow {border-color:#ffc8b3;background:linear-gradient(145deg,#fff7f3 0%,#fff 72%);}.algo-slow:before {background:#eb6834;}
        .algo-fast {border-color:#b6d8ff;background:linear-gradient(145deg,#f1f8ff 0%,#fff 72%);}.algo-fast:before {background:#2a78d6;}
        .algo-title {display:flex;align-items:center;justify-content:space-between;margin-bottom:15px;font-weight:850;font-size:1.05rem;color:#17212b;}
        .badge {font-size:.75rem;padding:5px 9px;border-radius:999px}.algo-slow .badge{background:#ffe1d5;color:#9d3510}.algo-fast .badge{background:#dcecff;color:#165ea8}
        .flow {display:flex;align-items:stretch;gap:7px;margin:8px 0 15px;}
        .flow-step {flex:1;display:flex;align-items:center;justify-content:center;text-align:center;border-radius:12px;padding:14px 9px;background:#fff;border:1px solid #d9dee4;font-size:.8rem;font-weight:800;line-height:1.3;color:#26313c;}
        .arrow {align-self:center;color:#687481;font-weight:900;font-size:1.1rem}.algo-note{font-size:.9rem;line-height:1.5;color:#505c68;margin:0;font-weight:500}
        .trip-strip {display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:8px 0 17px;padding:13px 15px;border-radius:14px;background:#f3f5f7;}
        .trip-strip span {font-size:.78rem;color:#68707b}.trip-chip {background:white;border:1px solid #dfe3e7;border-radius:9px;padding:6px 9px;font-weight:750;color:#26313c!important;font-family:monospace}
        .trip-chip.hit {background:#ffe1d5;border-color:#eb6834}
        .growth-legend {display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:26px;}
        .growth-box {border-radius:14px;padding:13px 15px;font-size:.88rem;line-height:1.4}.growth-box strong{font-size:1.05rem}
        .growth-slow{background:#fff0ea;color:#8f3212}.growth-fast{background:#eaf4ff;color:#175f9f}
        .property-grid {display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:10px 0 24px}.property-card{padding:13px;border-radius:14px;background:#f4f6f8;color:#26313c;border:1px solid #dce1e6;font-size:.77rem;line-height:1.35}.property-card b{display:block;font-size:.85rem;margin-bottom:4px}.property-card span{color:#65717c}.property-card.active{background:#eaf8f0;border-color:#7fd1a4}.property-card.active b{color:#176b43}
        .tools-note {padding:15px 17px;border-radius:15px;background:#f1f8f4;border:1px solid #bde5cf;color:#1f4d36;margin:6px 0 18px;font-size:.86rem;line-height:1.5}
        @media(max-width:800px){.taxi-hero,.algorithm-stage,.growth-legend,.story-context,.first-v1{grid-template-columns:1fr}.flow{flex-direction:column}.arrow{transform:rotate(90deg)}.property-grid{grid-template-columns:1fr 1fr}.acceptance-list,.v1-verdict{grid-template-columns:1fr}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_intro():
    rows = [
        ("Чи була поїздка о 18:40?", "час відсортований", "бінарний пошук"),
        ("Дві поїздки на суму ваучера", "суми відсортовані", "два вказівники"),
        ("Найзавантаженіші 6 годин", "відрізки підряд", "ковзне вікно"),
        ("Підказка адреси «Хр…»", "адреси за абеткою", "bisect + сусіди"),
    ]
    table = "".join(f'<div class="q-row"><b>{q}</b><span>{p}</span><i>{s}</i></div>' for q, p, s in rows)
    st.markdown(
        f"""
        <section class="taxi-hero">
          <div>
            <div class="taxi-kicker">Урок 12 · Практикум П2 · Пошук</div>
            <h1>Чи треба<br>перебирати все?</h1>
            <p>У П1 диспетчерська навчилася рахувати ціну рішення. Тепер у кожній задачі про дані щось <b>відомо</b> — порядок або суцільні відрізки. Саме це перетворює мільйон перевірок на двадцять.</p>
          </div>
          <div class="q-table">{table}</div>
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
            <div class="ticket-meta"><small>{story['client']} · Taxi Control</small><span class="brief-status">● ДО РОБОТИ</span></div>
            <div class="ticket-title">{story['ticket_title']}</div>
            <div class="ticket-section"><span class="ticket-label">Контекст</span><p>{story['context']}</p></div>
            <div class="ticket-section"><span class="ticket-label">Що потрібно зробити</span><p>{story['task']}</p></div>
            <div class="ticket-section"><span class="ticket-label">Приклад</span><p>{story['example_story']}</p><span class="ticket-example">{story['example']}</span></div>
          </div>
        </div>
        <div class="story-context">
          <div class="context-card"><b>🎯 Навіщо це бізнесу?</b><p>{story['why']}</p></div>
          <div class="context-card impact"><b>💥 Що буде, якщо рішення не встигатиме?</b><p>{story['impact']}</p></div>
        </div>
        <div class="acceptance">
          <div class="acceptance-head"><div><b>Як зрозуміти, що задача виконана?</b><small>Замовник прийме роботу, якщо виконано всі умови.</small></div><span class="ticket-id">TAXI-{1201 + list(MISSION_STORIES).index(key)}</span></div>
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
          <div class="verdict-good"><b>✅ Функціонально правильно</b><br>На малих прикладах відповідь збігається з вимогами.</div>
          <div class="verdict-bad"><b>⚠️ Не користується тим, що відомо про дані</b><br>Рішення перебирає все, ніби дані — випадкова купа.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_property_explanation(exp):
    cards = [
        ("Нічого не відомо", "Лишається перевірити кожен запис: лінійний пошук, O(n)."),
        ("Відсортовані, одне значення", "Порівняння з серединою відкидає половину: бінарний пошук, O(log n)."),
        ("Відсортовані, пара", "Вказівники з обох кінців назустріч: O(n) замість O(n²)."),
        ("Суцільні відрізки", "Нове вікно = старе + одне − одне: ковзне вікно, O(n)."),
    ]
    html = "".join(
        f'<div class="property-card{" active" if i == exp["property"] else ""}"><b>{title}</b><span>{text}</span></div>'
        for i, (title, text) in enumerate(cards)
    )
    st.markdown(f'<div class="property-grid">{html}</div>', unsafe_allow_html=True)


def show_algorithm_story(key, exp):
    story = ALGORITHM_STORIES[key]
    chips = "".join(f'<span class="trip-chip">{item}</span>' for item in story["data"])

    def flow(items):
        return '<span class="arrow">→</span>'.join(
            f'<div class="flow-step">{index}. {item}</div>' for index, item in enumerate(items, 1)
        )

    st.markdown(
        f"""
        <div class="section-eyebrow">Сцена 3 · Як працюють обидві версії</div>
        <div class="trip-strip"><span>Фрагмент даних:</span>{chips}</div>
        <div class="algorithm-stage">
          <div class="algo-card algo-slow">
            <div class="algo-title"><span>🐢 Перша версія · {exp['slow_o']}</span><span class="badge">{story['slow_badge']}</span></div>
            <div class="flow">{flow(story['slow'])}</div>
            <p class="algo-note">{story['slow_note']}</p>
          </div>
          <div class="algo-card algo-fast">
            <div class="algo-title"><span>⚡ Пошук з розумом · {exp['fast_o']}</span><span class="badge">{story['fast_badge']}</span></div>
            <div class="flow">{flow(story['fast'])}</div>
            <p class="algo-note">{story['fast_note']}</p>
          </div>
        </div>
        <div class="growth-legend">
          <div class="growth-box growth-slow"><strong>{exp['slow_o']}: {GROWTH_TEXT[exp['slow_o']]}</strong></div>
          <div class="growth-box growth-fast"><strong>{exp['fast_o']}: {GROWTH_TEXT[exp['fast_o']]}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def ratio_label(ratio):
    """Виміряне відношення кроків при подвоєнні n → варіант відповіді."""
    if ratio < 1.5:
        return RATIO_OPTIONS[0]
    if ratio < 3:
        return RATIO_OPTIONS[1]
    return RATIO_OPTIONS[2]


def run_experiment(exp, key, sizes, on_progress=None):
    rows = []
    args = None
    for index, n in enumerate(sizes):
        if on_progress:
            on_progress(index, len(sizes), n, "data")
        args = exp["make_input"](n)
        if on_progress:
            on_progress(index, len(sizes), n, "slow")
        start = time.perf_counter()
        slow_answer, slow_steps = exp["slow"](*args)
        slow_seconds = time.perf_counter() - start
        if on_progress:
            on_progress(index, len(sizes), n, "fast")
        start = time.perf_counter()
        fast_answer, fast_steps = exp["fast"](*args)
        fast_seconds = time.perf_counter() - start
        rows.append({
            "n": n, "slow_steps": slow_steps, "fast_steps": fast_steps,
            "slow_seconds": slow_seconds, "fast_seconds": fast_seconds,
            "answer": exp["normalize"](slow_answer),
            "same_answer": exp["normalize"](slow_answer) == exp["normalize"](fast_answer),
        })
    for previous, row in zip(rows, rows[1:]):
        row["slow_ratio"] = row["slow_steps"] / previous["slow_steps"]
        row["fast_ratio"] = row["fast_steps"] / previous["fast_steps"]
    if on_progress:
        on_progress(len(sizes), len(sizes), sizes[-1], "tools")
    tools = measure_tools(key, args)
    return rows, tools


def base_layout(fig, height, title=None, log_x=False, log_y=False, x_title="", y_title=""):
    axis = {"tickfont": {"color": "#52606d"}, "title_font": {"color": "#52606d"}, "gridcolor": "#e6e8eb"}
    fig.update_layout(
        template="none", height=height, margin={"l": 10, "r": 20, "t": 50 if title else 20, "b": 10},
        title={"text": title, "font": {"color": "#26313c", "size": 15}} if title else None,
        xaxis={**axis, "title": x_title, "type": "log" if log_x else "linear"},
        yaxis={**axis, "title": y_title, "type": "log" if log_y else "linear"},
        plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb", font={"color": "#26313c"},
        legend={"orientation": "h", "y": 1.12, "font": {"color": "#26313c"}},
    )
    return fig


def growth_chart(rows, exp):
    ns = [r["n"] for r in rows]
    fig = go.Figure()
    for key, name, color in (
        ("slow_steps", f"перша версія {exp['slow_o']}", SLOW_COLOR),
        ("fast_steps", f"пошук з розумом {exp['fast_o']}", FAST_COLOR),
    ):
        fig.add_trace(go.Scatter(
            x=ns, y=[r[key] for r in rows], name=name, mode="lines+markers",
            line={"color": color, "width": 2}, marker={"size": 9, "color": color},
            hovertemplate="n = %{x:,}<br>кроків: %{y:,}<extra>" + name + "</extra>",
        ))
    fig.update_layout(hovermode="x unified")
    return base_layout(fig, 360, "Кроки при подвоєнні даних", x_title="розмір даних n", y_title="кроків")


def tools_chart(entries):
    """entries: (назва, бібліотека, секунди). Горизонтальні стовпчики, лог-шкала часу."""
    entries = sorted(entries, key=lambda e: e[2], reverse=True)
    fig = go.Figure(go.Bar(
        x=[e[2] * 1000 for e in entries], y=[e[0] for e in entries], orientation="h",
        marker={"color": [LIB_COLORS.get(e[1], "#7d8792") for e in entries]},
        text=[human_time(e[2]) for e in entries], textposition="outside",
        hovertemplate="%{y}: %{text}<extra></extra>",
    ))
    fig = base_layout(fig, 70 + 42 * len(entries), "Час одного запиту (лог-шкала)",
                      log_x=True, x_title="мілісекунди")
    fig.update_layout(margin={"l": 10, "r": 80, "t": 50, "b": 10}, showlegend=False)
    # base_layout ставить осі "linear" — назви інструментів на такій осі зникають
    fig.update_yaxes(type="category", automargin=True)
    return fig


# ---------------------------------------------------------------------------
# Вкладка 1 · Місії диспетчера
# ---------------------------------------------------------------------------

def missions_tab():
    key = st.selectbox(
        "Оберіть місію від замовника", list(EXPERIMENTS),
        format_func=lambda k: EXPERIMENTS[k]["title"],
    )
    exp = EXPERIMENTS[key]
    show_client_brief(key)
    show_first_v1(key, exp)

    st.markdown('<div class="section-eyebrow">Сцена 2 · Що ми знаємо про дані?</div>', unsafe_allow_html=True)
    prop = st.radio(
        "Перечитай тікет. Яка властивість даних тут головна?",
        PROPERTY_OPTIONS, index=None, key=f"prop-{key}",
    )
    if prop is not None:
        chosen = PROPERTY_OPTIONS.index(prop)
        if chosen == exp["property"]:
            st.success(f"Так! Ця властивість дозволяє не перебирати все. Стратегія: **{STRATEGIES[chosen]}**.")
        else:
            st.warning(f"Не зовсім. Перечитай тікет ще раз — правильна властивість підсвічена нижче: "
                       f"**{PROPERTY_OPTIONS[exp['property']]}** → {STRATEGIES[exp['property']]}.")
        show_property_explanation(exp)

    show_algorithm_story(key, exp)
    code_slow, code_fast = st.columns(2)
    with code_slow:
        with st.expander("Перша версія — код"):
            st.code(inspect.getsource(exp["slow"]), language="python")
    with code_fast:
        with st.expander("Пошук з розумом — код"):
            st.code(inspect.getsource(exp["fast"]), language="python")

    st.subheader("Сцена 4 · Передбач")
    st.write("Даних стало **вдвічі більше**. Як зміниться кількість кроків?")
    guess_slow_col, guess_fast_col = st.columns(2)
    guess_slow = guess_slow_col.radio("Перша версія", RATIO_OPTIONS, index=None, key=f"gs-{key}")
    guess_fast = guess_fast_col.radio("Пошук з розумом", RATIO_OPTIONS, index=None, key=f"gf-{key}")

    st.subheader("Сцена 5 · Запусти дослід подвоєння")
    max_n = st.select_slider(
        "Найбільший розмір даних у досліді", options=exp["sizes"], value=exp["sizes"][-2],
        format_func=lambda v: f"{v:,}".replace(",", " "),
        help="Дослід запускає обидва рішення для n/8, n/4, n/2 і n — щоразу вдвічі більше.",
        key=f"n-{key}",
    )
    sizes = [max_n // 8, max_n // 4, max_n // 2, max_n]
    ready = prop is not None and guess_slow is not None and guess_fast is not None
    if not ready:
        st.caption("Щоб відкрити дослід, визнач властивість даних і обери обидва прогнози.")
    if st.button("Запустити дослід", type="primary", disabled=not ready, key=f"run-{key}"):
        progress = st.progress(0, text="Готуємо дані…")

        def update(done, total, n, phase):
            labels = {
                "data": f"📦 Генеруємо дані, n = {n:,}…",
                "slow": f"🐢 Перша версія, n = {n:,}…",
                "fast": f"⚡ Пошук з розумом, n = {n:,}…",
                "tools": "🧰 Міряємо готові інструменти Python і бібліотек…",
            }
            progress.progress(min(100, int(100 * done / total)), text=labels[phase])

        st.session_state["mission"] = (key, max_n, *run_experiment(exp, key, sizes, update))
        progress.progress(100, text="Дослід завершено")

    result = st.session_state.get("mission")
    if not (result and result[0] == key and result[1] == max_n and ready):
        return
    rows, tools = result[2], result[3]
    last = rows[-1]

    if all(r["same_answer"] for r in rows):
        st.success("Обидві версії дали однакову відповідь для кожного n — обидві правильні. Різниця лише в роботі.")
    else:
        st.error("Відповіді різні — в одній з версій помилка.")

    m1, m2, m3 = st.columns(3)
    m1.metric(f"Кроків при n = {last['n']:,}: перша версія", f"{last['slow_steps']:,}")
    m2.metric("пошук з розумом", f"{last['fast_steps']:,}")
    m3.metric("Перша версія робить більше в", f"{last['slow_steps'] / last['fast_steps']:,.0f} раз")

    log_scale = st.toggle("Логарифмічна шкала кроків", key=f"log-{key}")
    fig = growth_chart(rows, exp)
    if log_scale:
        fig.update_yaxes(type="log")
    st.plotly_chart(fig, width="stretch")

    st.dataframe(
        [
            {
                "n": r["n"],
                "перша: кроки": r["slow_steps"],
                "перша: × до попер.": round(r["slow_ratio"], 2) if "slow_ratio" in r else None,
                "з розумом: кроки": r["fast_steps"],
                "з розумом: × до попер.": round(r["fast_ratio"], 2) if "fast_ratio" in r else None,
                "час (перша / з розумом)": f"{human_time(r['slow_seconds'])} / {human_time(r['fast_seconds'])}",
            }
            for r in rows
        ],
        width="stretch", hide_index=True,
    )

    for label, guess, measured in (
        ("Перша версія", guess_slow, ratio_label(last["slow_ratio"])),
        ("Пошук з розумом", guess_fast, ratio_label(last["fast_ratio"])),
    ):
        if guess == measured:
            st.write(f"✅ {label}: прогноз «{guess}» підтвердився.")
        else:
            st.write(f"❌ {label}: ти передбачив «{guess}», а дослід показав «{measured}».")

    with st.expander("Чому так?", expanded=True):
        st.markdown(WHY[key])

    show_ready_tools(key, exp, last, tools)

    st.subheader("Фінал · Місто росте")
    target = st.select_slider(
        "Скільки записів буде в даних?",
        options=[10_000, 100_000, 1_000_000, 10_000_000, 100_000_000], value=10_000_000,
        format_func=lambda v: f"{v:,}".replace(",", " "), key=f"target-{key}",
    )
    slow_est = last["slow_seconds"] * GROWTH[exp["slow_o"]](target) / GROWTH[exp["slow_o"]](last["n"])
    fast_est = last["fast_seconds"] * GROWTH[exp["fast_o"]](target) / GROWTH[exp["fast_o"]](last["n"])
    e1, e2 = st.columns(2)
    e1.metric(f"Перша версія {exp['slow_o']}", human_time(slow_est))
    e2.metric(f"Пошук з розумом {exp['fast_o']}", human_time(fast_est))
    st.caption(
        f"Оцінка з досліду при n = {last['n']:,}: виміряний час множимо на те, у скільки разів зросте "
        f"{exp['slow_o']} та {exp['fast_o']}. На іншому комп'ютері секунди будуть інші, але різниця залишиться."
    )


def show_ready_tools(key, exp, last, tools):
    st.subheader("Сцена 6 · А що вже готове в Python і бібліотеках?")
    st.markdown(
        '<div class="tools-note">Свій пошук ми писали, щоб <b>зрозуміти</b> ідею. У роботі зазвичай беруть готове: '
        'стандартну бібліотеку (<code>in</code>, <code>bisect</code>, <code>itertools</code>) або сторонні '
        '(<code>numpy</code>, <code>pandas</code>, <code>sortedcontainers</code>). Вони написані на C і швидші за наш '
        'цикл на Python. Але Big O від цього не зникає: інструмент на C з O(n) на великих даних однаково програє O(log n).</div>',
        unsafe_allow_html=True,
    )
    entries = [
        (f"наш код: перша версія {exp['slow_o']}", "наш код", last["slow_seconds"]),
        (f"наш код: з розумом {exp['fast_o']}", "наш код", last["fast_seconds"]),
    ] + [(f"{t['name']} {t['o']}", t["lib"], t["seconds"]) for t in tools]
    st.plotly_chart(tools_chart(entries), width="stretch")
    st.dataframe(
        [
            {
                "інструмент": t["name"], "бібліотека": t["lib"], "Big O запиту": t["o"],
                "та сама відповідь": "✅" if t["answer"] == last["answer"] else "❌",
                "підготовка (один раз)": human_time(t["prepare"]),
                "один запит": human_time(t["seconds"]),
            }
            for t in tools
        ],
        width="stretch", hide_index=True,
    )
    st.caption(
        f"n = {last['n']:,}. «Підготовка» — перетворення даних один раз: список → масив numpy, "
        "SortedList чи pandas.Series. Вона окупається, лише коли запитів багато. Для стандартної бібліотеки "
        "підготовки немає — працює зі звичайним списком."
    )
    with st.expander("Код готових рішень"):
        for tool in READY_TOOLS[key]:
            st.markdown(f"**{tool['name']}** · `{tool['lib']}` · {tool['o']}")
            source = inspect.getsource(tool["run"])
            if tool["prepare"].__name__ != "as_is":
                source = inspect.getsource(tool["prepare"]) + "\n\n" + source
            st.code(source, language="python")


# ---------------------------------------------------------------------------
# Вкладка 2 · Гонка пошуків
# ---------------------------------------------------------------------------

RACE_SIZES = [1_000, 10_000, 100_000, 1_000_000]


def race_line_chart(results):
    fig = go.Figure()
    for racer in RACERS:
        name = racer["name"]
        xs = [n for n, rows in results]
        ys = [next(r["seconds"] for r in rows if r["name"] == name) * 1000 for _, rows in results]
        fig.add_trace(go.Scatter(
            x=xs, y=ys, name=f"{name} {racer['o']}", mode="lines+markers",
            line={"color": RACER_COLORS.get(name, "#7d8792"), "width": 2,
                  "dash": "solid" if racer["o"] == "O(n)" else "dot"},
            hovertemplate="n = %{x:,}<br>%{y:.4f} мс<extra>" + name + "</extra>",
        ))
    fig.update_layout(legend={"orientation": "h", "y": -0.2})
    fig = base_layout(fig, 430, "Час одного пошуку залежно від розміру журналу",
                      log_x=True, log_y=True, x_title="записів у журналі (лог-шкала)",
                      y_title="мілісекунди (лог-шкала)")
    fig.update_layout(legend={"orientation": "h", "y": -0.25})
    return fig


def race_tab():
    st.markdown(
        "Один і той самий відсортований журнал поїздок, один і той самий момент — шість способів його знайти: "
        "**наш код**, **стандартна бібліотека Python** і **сторонні бібліотеки**."
    )
    st.dataframe(
        [{"спосіб": r["name"], "звідки": r["lib"], "Big O": r["o"]} for r in RACERS],
        width="stretch", hide_index=True,
    )
    c1, c2 = st.columns(2)
    max_n = c1.select_slider(
        "Найбільший журнал", options=RACE_SIZES, value=1_000_000,
        format_func=lambda v: f"{v:,}".replace(",", " "),
    )
    position = c2.radio("Де шуканий момент?", list(POSITIONS), index=3, horizontal=True)
    if st.button("🏁 Старт гонки", type="primary"):
        results = []
        progress = st.progress(0, text="Гонка…")
        sizes = [n for n in RACE_SIZES if n <= max_n]
        for i, n in enumerate(sizes):
            progress.progress(int(100 * i / len(sizes)), text=f"Журнал на {n:,} записів…")
            data = race_data(n)
            results.append((n, race(data, POSITIONS[position](data))))
        progress.progress(100, text="Фініш")
        st.session_state["race"] = (max_n, position, results)

    saved = st.session_state.get("race")
    if saved and saved[0] == max_n and saved[1] == position:
        results = saved[2]
        n, rows = results[-1]
        st.plotly_chart(race_line_chart(results), width="stretch")
        st.dataframe(
            [
                {
                    "спосіб": r["name"], "звідки": r["lib"], "Big O": r["o"],
                    "знайдено": "так" if r["found"] else "ні",
                    "кроки": f"{r['steps']:,}" if r["steps"] is not None else "—",
                    "підготовка": human_time(r["prepare"]),
                    "один пошук": human_time(r["seconds"]),
                }
                for r in sorted(rows, key=lambda r: r["seconds"])
            ],
            width="stretch", hide_index=True,
        )
        fastest = min(rows, key=lambda r: r["seconds"])
        slowest = max(rows, key=lambda r: r["seconds"])
        st.info(
            f"На {n:,} записах найшвидший — **{fastest['name']}** ({human_time(fastest['seconds'])}), "
            f"найповільніший — **{slowest['name']}** ({human_time(slowest['seconds'])}): "
            f"різниця в {slowest['seconds'] / fastest['seconds']:,.0f} разів."
        )
        st.markdown(
            "- `x in list` у кілька разів швидший за наш цикл — він на C. Але лінії O(n) однаково йдуть **вгору**: "
            "у 10 разів більший журнал — у 10 разів довше.\n"
            "- Лінії O(log n) майже **пласкі**: мільйон записів — близько 20 порівнянь.\n"
            "- `numpy.searchsorted` для **одного** запиту не найшвидший: кожен виклик numpy має накладні витрати, "
            "а перетворення списку в масив займає час (колонка «підготовка»). numpy виграє, коли запитів **багато** — див. нижче.\n"
            "- `SortedList` тримає дані відсортованими навіть після вставок — зручно, коли журнал постійно поповнюється."
        )

    st.divider()
    st.subheader("Багато запитів одразу: цикл чи numpy?")
    q1, q2 = st.columns(2)
    batch_n = q1.select_slider("Записів у журналі", options=RACE_SIZES, value=1_000_000,
                               format_func=lambda v: f"{v:,}".replace(",", " "), key="batch-n")
    queries = q2.select_slider("Скільки моментів перевірити", options=[1_000, 10_000, 100_000, 1_000_000],
                               value=100_000, format_func=lambda v: f"{v:,}".replace(",", " "))
    if st.button("Порівняти", key="batch-run"):
        st.session_state["batch"] = (batch_n, queries, batch_race(batch_n, queries))
    batch = st.session_state.get("batch")
    if batch and batch[:2] == (batch_n, queries):
        cols = st.columns(len(batch[2]))
        for col, (name, secs) in zip(cols, batch[2].items()):
            col.metric(name, human_time(secs))
        st.caption(
            "Цикл Python викликає bisect для кожного моменту окремо. numpy.searchsorted отримує весь масив моментів "
            "і проходить його всередині C — без циклу Python. Векторизація: чим більше запитів, тим більший виграш."
        )

    st.divider()
    st.subheader("Пастка: бінарний пошук на невідсортованих даних")
    data, target, linear_result, binary_result = unsorted_trap()
    chips = "".join(f'<span class="trip-chip{" hit" if x == target else ""}">{x}</span>' for x in data)
    st.markdown(f'<div class="trip-strip"><span>Журнал (перемішаний):</span>{chips}</div>', unsafe_allow_html=True)
    t1, t2 = st.columns(2)
    t1.metric(f"linear_search(журнал, {target})", f"індекс {linear_result[0]}", f"{linear_result[1]} кроків")
    t2.metric(f"binary_search(журнал, {target})", f"індекс {binary_result[0]}", "не знайшов!", delta_color="inverse")
    st.warning(
        f"Момент {target} **є** в журналі, але бінарний пошук повернув -1 — без жодної помилки. "
        "Він відкидає половину, вважаючи, що зліва менші числа. Без порядку цей висновок хибний: пошук мовчки бреше."
    )

    st.divider()
    st.subheader("Чи варто спершу відсортувати?")
    payoff_n = st.select_slider("Записів у журналі", options=RACE_SIZES, value=1_000_000,
                                format_func=lambda v: f"{v:,}".replace(",", " "), key="payoff-n")
    if st.button("Виміряти", key="payoff-run"):
        st.session_state["payoff"] = (payoff_n, sort_payoff(payoff_n))
    payoff = st.session_state.get("payoff")
    if payoff and payoff[0] == payoff_n:
        p = payoff[1]
        a, b, c, d = st.columns(4)
        a.metric("sorted() один раз", human_time(p["sort"]))
        b.metric("один пошук in", human_time(p["linear"]))
        c.metric("один пошук bisect", human_time(p["binary"]))
        d.metric("Сортування окупається після", f"{p['breakeven']:,} пошуків")
        qs = list(range(0, max(4 * p["breakeven"], 10) + 1))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=qs, y=[q * p["linear"] * 1000 for q in qs], name="без сортування: q × in",
                                 line={"color": SLOW_COLOR, "width": 3}))
        fig.add_trace(go.Scatter(x=qs, y=[(p["sort"] + q * p["binary"]) * 1000 for q in qs],
                                 name="sorted() + q × bisect", line={"color": FAST_COLOR, "width": 3}))
        st.plotly_chart(base_layout(fig, 340, "Загальний час для q пошуків", x_title="кількість пошуків q",
                                    y_title="мілісекунди"), width="stretch")
        st.caption(
            "Сортування коштує O(n log n) — дорожче за один лінійний пошук. Для одного-двох пошуків сортувати не варто. "
            "Але диспетчерська шукає сотні разів на день — тоді сортування один раз швидко окупається."
        )


st.set_page_config(page_title="Таксі: пошук", page_icon="🚕", layout="wide")
inject_styles()
show_intro()
missions, racing = st.tabs(["🚕 Місії диспетчера", "🏁 Гонка пошуків"])
with missions:
    missions_tab()
with racing:
    race_tab()
