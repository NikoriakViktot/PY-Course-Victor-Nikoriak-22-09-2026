"""
Таксі: хеш-таблиці зсередини — демонстрація до уроку 17 (П3. Хеш-структури).

Запуск:
    pip install streamlit plotly duckdb pandas geopandas
    streamlit run app.py

Логіка — у taxi_core.py. Тут лише інтерфейс, чотири вкладки:
хеш-таблиця зсередини · list/tuple/set/dict · пам'ять · NYC Taxi + DuckDB.
"""
import html
import inspect
import math

import plotly.graph_objects as go
import streamlit as st

import taxi_core as core

TYPE_COLORS = {"list": "#eb6834", "tuple": "#f2a541", "set": "#2a78d6", "dict": "#3d9970"}
HASH_COLORS = ["#2a78d6", "#d4a017", "#8e6cc8", "#eb6834"]


def inject_styles():
    st.markdown(
        """
        <style>
        .block-container {padding-top: 2rem; padding-bottom: 4rem; max-width: 1180px;}
        .hero {padding:28px 30px; border-radius:26px; color:#16202a; margin-bottom:20px;
               background:linear-gradient(135deg,#fff9d9 0%,#fff1a8 52%,#ffd84d 100%); box-shadow:0 18px 50px rgba(92,72,0,.13);}
        .hero small {font-size:.78rem; letter-spacing:.13em; font-weight:800; text-transform:uppercase; color:#806500;}
        .hero h1 {font-size:clamp(1.9rem,3.6vw,3.2rem); line-height:1.05; margin:.4rem 0 .7rem; color:#16202a; letter-spacing:-.03em;}
        .hero p {font-size:1.02rem; line-height:1.55; max-width:820px; margin:0;}
        .eyebrow {font-size:.75rem;font-weight:850;letter-spacing:.12em;text-transform:uppercase;color:#8a6e00;margin:14px 0 4px;}
        .pipeline {display:flex; gap:8px; align-items:stretch; flex-wrap:wrap; margin:8px 0 18px;}
        .pipe {flex:1; min-width:140px; padding:14px; border-radius:14px; background:#17212b; color:#eef3f7; text-align:center;}
        .pipe small {display:block; color:#9eabb8; font-size:.68rem; text-transform:uppercase; letter-spacing:.08em; font-weight:800;}
        .pipe b {display:block; font-family:monospace; font-size:1.05rem; color:#ffd84d; margin-top:6px; word-break:break-all;}
        .pipe-arrow {align-self:center; font-weight:900; color:#687481;}
        .slots {display:grid; grid-template-columns:repeat(auto-fill,minmax(118px,1fr)); gap:8px; margin:10px 0 16px;}
        .slot {border-radius:12px; padding:9px 10px; min-height:66px; background:#f4f6f8; border:1px solid #dce1e6; color:#26313c; font-size:.76rem;}
        .slot .idx {font-family:monospace; font-size:.68rem; color:#7d8792; font-weight:800;}
        .slot .key {display:block; font-weight:750; margin-top:3px; line-height:1.25; word-break:break-word;}
        .slot.home {background:#eaf4ff; border-color:#9cc8f5;}
        .slot.moved {background:#fff3dc; border-color:#f2b84b;}
        .slot.hit {box-shadow:0 0 0 3px #19a267;}
        .slot.path {box-shadow:0 0 0 3px #eb6834;}
        .slot.chain-long {background:#fff0eb; border-color:#ff9b82;}
        .chain-item {display:inline-block; margin:3px 3px 0 0; padding:2px 6px; border-radius:6px; background:#fff; border:1px solid #cfd6dd; font-weight:700;}
        .legend {display:flex; gap:14px; flex-wrap:wrap; font-size:.78rem; color:#52606d; margin:-4px 0 10px;}
        .legend span:before {content:""; display:inline-block; width:11px; height:11px; border-radius:3px; margin-right:5px; vertical-align:-1px; background:var(--c);}
        .note {padding:15px 17px; border-radius:15px; background:#f1f8f4; border:1px solid #bde5cf; color:#1f4d36; margin:6px 0 18px; font-size:.88rem; line-height:1.55;}
        .warn {padding:15px 17px; border-radius:15px; background:#fff8d9; border:1px solid #f1d46b; color:#604e08; margin:6px 0 18px; font-size:.88rem; line-height:1.55;}
        .db-cards {display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin:8px 0 18px;}
        .db-card {padding:14px; border-radius:14px; background:#fff; border:1px solid #dfe3e8; color:#202a34; font-size:.84rem; line-height:1.45;}
        .db-card b {display:block; margin-bottom:5px;}
        @media(max-width:800px){.db-cards{grid-template-columns:1fr}.pipe-arrow{display:none}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_intro():
    st.markdown(
        """
        <section class="hero">
          <small>Урок 17 · Практикум П3 · Хеш-структури</small>
          <h1>Чому <code>x in set</code> миттєвий,<br>а <code>x in list</code> — ні?</h1>
          <p>Зазирнемо всередину словника й множини: як ключ перетворюється на номер комірки, що таке колізія,
          чому таблиця сама розширюється і скільки за цю швидкість платимо пам'яттю. А наприкінці — справжні
          3 мільйони поїздок нью-йоркського таксі і база даних DuckDB, яка всередині використовує ті самі хеш-таблиці.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def base_layout(fig, height, title=None, x_title="", y_title="", log_x=False, log_y=False):
    axis = {"tickfont": {"color": "#52606d"}, "title_font": {"color": "#52606d"}, "gridcolor": "#e6e8eb"}
    fig.update_layout(
        template="none", height=height, margin={"l": 10, "r": 20, "t": 50 if title else 20, "b": 10},
        title={"text": title, "font": {"color": "#26313c", "size": 15}} if title else None,
        xaxis={**axis, "title": x_title, "type": "log" if log_x else "linear"},
        yaxis={**axis, "title": y_title, "type": "log" if log_y else "linear"},
        plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb", font={"color": "#26313c"},
        legend={"orientation": "h", "y": -0.22, "font": {"color": "#26313c"}},
    )
    return fig


def predict(question, options, answer, key, explanation):
    """Прогноз перед дослідом: відповідь і пояснення відкриваються після вибору."""
    choice = st.radio(question, options, index=None, key=key)
    if choice is not None:
        if choice == answer:
            st.success(f"Так! {explanation}")
        else:
            st.warning(f"Насправді — «{answer}». {explanation}")
    return choice


# ---------------------------------------------------------------------------
# Вкладка 1 · Хеш-таблиця зсередини
# ---------------------------------------------------------------------------

def render_slots(table, highlight=None, path=()):
    cells = []
    for index, content in enumerate(table.slots):
        classes = ["slot"]
        if table.mode == "chaining":
            body = "".join(f'<span class="chain-item">{html.escape(str(k))}</span>' for k in content) or "·"
            if len(content) >= 3:
                classes.append("chain-long")
            elif content:
                classes.append("home")
            if highlight is not None and highlight in content:
                classes.append("hit")
        else:
            if content is core.EMPTY:
                body = "·"
            else:
                body = html.escape(str(content))
                classes.append("home" if table.home(content) == index else "moved")
            if highlight is not None and content == highlight:
                classes.append("hit")
            elif index in path:
                classes.append("path")
        cells.append(f'<div class="{" ".join(classes)}"><span class="idx">[{index}]</span>'
                     f'<span class="key">{body}</span></div>')
    st.markdown(f'<div class="slots">{"".join(cells)}</div>', unsafe_allow_html=True)


def probe_path(table, key):
    """Комірки, які переглянув пошук у відкритій адресації."""
    index, path = table.home(key), []
    for _ in range(table.capacity):
        path.append(index)
        item = table.slots[index]
        if item is core.EMPTY or item == key:
            break
        index = (index + 1) % table.capacity
    return path


def hash_tab():
    st.markdown('<div class="eyebrow">Крок 1 · Ключ → номер комірки</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    raw_key = c1.text_input("Ключ (назва зони або номер поїздки)", value="JFK Airport")
    capacity = c2.selectbox("Комірок у таблиці", [8, 16, 32, 64], index=0)
    key = int(raw_key) if raw_key.strip().lstrip("-").isdigit() else raw_key
    h = hash(key)
    st.markdown(
        f"""
        <div class="pipeline">
          <div class="pipe"><small>ключ</small><b>{html.escape(repr(key))}</b></div><div class="pipe-arrow">→</div>
          <div class="pipe"><small>hash(ключ)</small><b>{h}</b></div><div class="pipe-arrow">→</div>
          <div class="pipe"><small>% {capacity}</small><b>{h % capacity}</b></div><div class="pipe-arrow">→</div>
          <div class="pipe"><small>комірка</small><b>[{h % capacity}]</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "hash() перетворює будь-який незмінний ключ на ціле число за O(1) (для рядка — один раз, далі Python його "
        "пам'ятає). Остача від ділення дає номер комірки. Спробуй число: hash(237) == 237. А hash рядка "
        "змінюється після перезапуску Python (захист PYTHONHASHSEED) — тому порядок у set рядків щоразу інший."
    )

    st.markdown('<div class="eyebrow">Крок 2 · Наповнюємо таблицю справжніми зонами NYC</div>', unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    mode = m1.radio("Як розв'язувати колізії", ["probing", "chaining"], horizontal=True,
                    format_func=lambda m: {"probing": "відкрита адресація (як dict)",
                                           "chaining": "кошики-списки (як у ноутбуці)"}[m])
    hash_name = m2.selectbox("Хеш-функція", list(core.HASH_FUNCS))
    keys = st.session_state.setdefault("hash_keys", [])
    all_keys = core.make_keys(260)
    b1, b2, b3, b4 = st.columns(4)
    if b1.button("+1 зона"):
        keys.extend(all_keys[len(keys):len(keys) + 1])
    if b2.button("+5 зон"):
        keys.extend(all_keys[len(keys):len(keys) + 5])
    if b3.button("+50 зон"):
        keys.extend(all_keys[len(keys):len(keys) + 50])
    if b4.button("Скинути"):
        keys.clear()

    table = core.TeachingHashTable(mode=mode, hash_func=core.HASH_FUNCS[hash_name])
    last_probes = None
    for k in keys:
        last_probes = table.add(k)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Ключів", table.size)
    k2.metric("Комірок", table.capacity)
    k3.metric("Заповнення", f"{table.load:.0%}", help="Коли перевищить 2/3 — таблиця подвоюється")
    k4.metric("Останнє додавання", f"{last_probes} порівн." if last_probes else "—")

    search = st.text_input("Знайти ключ у таблиці", value=keys[-1] if keys else "")
    highlight, path = None, ()
    if search and keys:
        found, probes = table.contains(search)
        if mode == "probing":
            path = probe_path(table, search)
        highlight = search if found else None
        (st.success if found else st.info)(
            f"{'Знайдено' if found else 'Немає'} за {probes} порівн.: домашня комірка "
            f"[{table.home(search)}]" + (f", шлях {path}" if mode == "probing" and len(path) > 1 else "")
        )
    st.markdown(
        '<div class="legend"><span style="--c:#eaf4ff">ключ у своїй комірці</span>'
        '<span style="--c:#fff3dc">зсунутий колізією</span><span style="--c:#fff0eb">довгий кошик</span>'
        '<span style="--c:#19a267">знайдено</span><span style="--c:#eb6834">шлях пошуку</span></div>',
        unsafe_allow_html=True,
    )
    render_slots(table, highlight, path)
    if table.resizes:
        steps = " → ".join(f"{old}→{new} комірок (на {at + 1}-му ключі)" for old, new, at in table.resizes)
        st.markdown(
            f'<div class="note"><b>Таблиця розширювалась:</b> {steps}. Щоразу всі ключі перераховувались у нові '
            "комірки — це O(n), але трапляється все рідше (місткість подвоюється), тож у середньому додавання "
            "лишається O(1).</div>",
            unsafe_allow_html=True,
        )
    if hash_name != "hash() — вбудований" and table.size > 10:
        st.markdown(
            '<div class="warn"><b>Погана хеш-функція:</b> різні ключі отримують однакові номери, комірок вистачає, '
            "але ключі товпляться в кількох місцях. Пошук перетворюється на перебір — O(n), як у списку.</div>",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="eyebrow">Крок 3 · Дослід: скільки порівнянь на один пошук?</div>', unsafe_allow_html=True)
    predict(
        "Передбач: таблиця з 256 зонами і вбудованим hash(). Скільки порівнянь у середньому потрібно, щоб знайти ключ?",
        ["1–2", "≈ 16 (√n)", "≈ 128 (n/2)"], "1–2", "key_hash_predict",
        "Заповнення не більше 2/3, тож у більшості ключів своя комірка. Але з функцією «завжди 0» — n/2, як у списку.",
    )
    sizes = [16, 32, 64, 128, 256]
    fig = go.Figure()
    for (name, func), color in zip(core.HASH_FUNCS.items(), HASH_COLORS):
        growth = core.probe_growth(core.make_keys, sizes, func, mode)
        fig.add_trace(go.Scatter(x=[n for n, _ in growth], y=[p for _, p in growth], name=name,
                                 mode="lines+markers", line={"color": color, "width": 3}))
    st.plotly_chart(base_layout(fig, 360, "Середня кількість порівнянь на пошук",
                                x_title="ключів у таблиці", y_title="порівнянь"), width="stretch")
    st.markdown(
        '<div class="note"><b>Чому хеш-таблиця швидка:</b> (1) hash() — одна дія незалежно від того, скільки ключів у '
        "таблиці; (2) номер комірки — арифметика, а не пошук; (3) таблиця тримає щонайменше третину комірок "
        "порожніми, тому колізій мало. Ціна — пам'ять (вкладка «Пам'ять») і вимога, щоб ключ був незмінним "
        "(вкладка «list · tuple · set · dict»).</div>",
        unsafe_allow_html=True,
    )
    with st.expander("Код навчальної таблиці"):
        st.code(inspect.getsource(core.TeachingHashTable), language="python")


# ---------------------------------------------------------------------------
# Вкладка 2 · list / tuple / set / dict
# ---------------------------------------------------------------------------

def types_tab():
    st.markdown('<div class="eyebrow">Чотири контейнери — чотири компроміси</div>', unsafe_allow_html=True)
    st.dataframe(
        [dict(zip(["тип", "приклад", "порядок", "змінюваний", "повтори", "може бути ключем",
                   "x in …", "доступ"], row)) for row in core.CONTAINER_PROPERTIES],
        width="stretch", hide_index=True,
    )
    st.caption("* tuple може бути ключем, лише якщо всі його елементи теж hashable.")

    st.markdown('<div class="eyebrow">Що може бути ключем dict і елементом set</div>', unsafe_allow_html=True)
    st.dataframe(
        [{"тип": r["тип"], "вираз": r["вираз"], "hashable": "✅" if r["hashable"] else "❌",
          "hash(...)": r["результат"]} for r in core.hashability_report()],
        width="stretch", hide_index=True,
    )
    st.markdown(
        '<div class="note">Ключ визначає комірку через hash(). Якби список змінився вже після того, як потрапив у '
        "таблицю, його hash став би іншим — і ключ «загубився б» у чужій комірці. Тому Python не дає хешувати "
        "змінювані типи: list, set, dict. Незмінні tuple і frozenset — можна.</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="eyebrow">Пастка: рівні ключі — один ключ</div>', unsafe_allow_html=True)
    st.code('demo = {}\ndemo[1] = "int"\ndemo[1.0] = "float"\ndemo[True] = "bool"\nprint(demo)', language="python")
    predict("Передбач: що надрукує print(demo)?",
            ["{1: 'int', 1.0: 'float', True: 'bool'}", "{1: 'bool'}", "TypeError"],
            "{1: 'bool'}", "key_equal_predict",
            f"Результат: {core.equal_keys_demo()}. 1 == 1.0 == True і hash у них однаковий (1), тож це один "
            "ключ: значення перезаписується, а сам ключ лишається першим — 1.")

    st.markdown('<div class="eyebrow">Гонка: x in … для відсутнього ключа</div>', unsafe_allow_html=True)
    predict("Передбач: на 1 000 000 номерів у скільки разів x in set швидший за x in list?",
            ["≈ ×10", "≈ ×1 000", "≈ ×100 000"], "≈ ×100 000", "race_predict",
            "list переглядає мільйон елементів, set — одну-дві комірки.")
    if st.button("🏁 Запустити гонку", type="primary"):
        with st.spinner("Будуємо контейнери й міряємо…"):
            st.session_state["types_race"] = core.membership_race([1_000, 10_000, 100_000, 1_000_000])
    rows = st.session_state.get("types_race")
    if rows:
        lookup_fig, build_fig = go.Figure(), go.Figure()
        for name, color in TYPE_COLORS.items():
            data = [r for r in rows if r["type"] == name]
            dash = "solid" if name in ("list", "tuple") else "dot"
            lookup_fig.add_trace(go.Scatter(x=[r["n"] for r in data], y=[r["lookup"] * 1e6 for r in data], name=name,
                                            mode="lines+markers", line={"color": color, "width": 3, "dash": dash}))
            build_fig.add_trace(go.Bar(x=[f"{r['n']:,}" for r in data], y=[r["build"] * 1000 for r in data],
                                       name=name, marker={"color": color}))
        c1, c2 = st.columns(2)
        c1.plotly_chart(base_layout(lookup_fig, 380, "Один пошук x in … (лог-шкали)", "елементів", "мікросекунди",
                                    log_x=True, log_y=True), width="stretch")
        c2.plotly_chart(base_layout(build_fig, 380, "Побудова контейнера зі списку", "елементів", "мілісекунди",
                                    log_y=True), width="stretch")
        big = {r["type"]: r for r in rows if r["n"] == 1_000_000}
        st.info(
            f"1 000 000 елементів: x in list — {core.human_time(big['list']['lookup'])}, x in set — "
            f"{core.human_time(big['set']['lookup'])} (у {big['list']['lookup'] / big['set']['lookup']:,.0f} разів "
            f"швидше). Зате побудова set — {core.human_time(big['set']['build'])} проти "
            f"{core.human_time(big['list']['build'])} для list: кожен елемент треба захешувати й покласти в комірку. "
            "Множина окупається, коли запитів багато."
        )


# ---------------------------------------------------------------------------
# Вкладка 3 · Пам'ять
# ---------------------------------------------------------------------------

def memory_tab():
    st.markdown('<div class="eyebrow">Швидкість не безкоштовна</div>', unsafe_allow_html=True)
    predict("Передбач: 100 000 номерів поїздок. У скільки разів set займає більше пам'яті, ніж list (лише сам контейнер)?",
            ["однаково", "≈ ×2", "≈ ×5", "≈ ×10"], "≈ ×5", "mem_predict",
            "list зберігає лише посилання — 8 байт на елемент. set зберігає ще й hash кожного ключа і тримає "
            "третину комірок порожніми, а місткість — степінь двійки.")
    n = st.select_slider("Скільки номерів", options=[10_000, 100_000, 1_000_000], value=100_000,
                         format_func=lambda v: f"{v:,}".replace(",", " "))
    rows = core.memory_table(n)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[r["тип"] for r in rows], y=[r["контейнер (getsizeof)"] / 2 ** 20 for r in rows],
                         name="сам контейнер", marker={"color": [TYPE_COLORS[r["тип"]] for r in rows]}))
    fig.add_trace(go.Bar(x=[r["тип"] for r in rows],
                         y=[(r["разом з числами (deep_size)"] - r["контейнер (getsizeof)"]) / 2 ** 20 for r in rows],
                         name="+ самі числа (int по 28 байт)", marker={"color": "#c9d0d8"}))
    fig.update_layout(barmode="stack")
    st.plotly_chart(base_layout(fig, 360, f"Пам'ять для {n:,} номерів поїздок", y_title="МБ"), width="stretch")
    st.dataframe(
        [{"тип": r["тип"], "контейнер": core.human_bytes(r["контейнер (getsizeof)"]),
          "разом з числами": core.human_bytes(r["разом з числами (deep_size)"]),
          "tracemalloc (реально виділено)": core.human_bytes(r["tracemalloc"]),
          "байт на елемент": f"{r['байт на елемент (контейнер)']:.1f}"} for r in rows],
        width="stretch", hide_index=True,
    )
    st.caption(
        "getsizeof рахує лише сам контейнер — масив посилань або хеш-таблицю. Числа — окремі об'єкти по 28 байт. "
        "tracemalloc показує, скільки пам'яті Python справді виділив під час побудови, — і це збігається з getsizeof."
    )

    st.markdown('<div class="eyebrow">Як росте розмір: сходинки</div>', unsafe_allow_html=True)
    curve = core.getsizeof_curve(64)
    fig = go.Figure()
    for name, color in TYPE_COLORS.items():
        fig.add_trace(go.Scatter(x=[r["n"] for r in curve], y=[r[name] for r in curve], name=name,
                                 line={"color": color, "width": 3, "shape": "hv"}))
    st.plotly_chart(base_layout(fig, 360, "sys.getsizeof для n = 0…64", "елементів", "байт"), width="stretch")
    st.markdown(
        '<div class="note"><b>tuple</b> росте рівно на 8 байт за елемент — розмір відомий наперед. <b>list</b> '
        "виділяє запас, щоб append був швидким. <b>set</b> і <b>dict</b> стрибають: коли таблиця заповнюється на "
        "2/3, вона розширюється — ті самі «переїзди», що у вкладці «Хеш-таблиця зсередини».</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="eyebrow">Скільки важить рядок</div>', unsafe_allow_html=True)
        st.dataframe(core.string_sizes(), width="stretch", hide_index=True)
        st.caption("Латиниця — 1 байт на символ, кирилиця — 2, якщо є емодзі — 4 для всіх символів рядка.")
    with c2:
        st.markdown('<div class="eyebrow">Скільки важить число</div>', unsafe_allow_html=True)
        st.dataframe(core.int_sizes(), width="stretch", hide_index=True)
        cache = core.small_int_cache()
        st.caption(f"int у Python — повноцінний об'єкт, не 8 байт як у C. Числа від -5 до 256 Python створює "
                   f"заздалегідь: 256 is 256 → {cache['256 is 256']}, 257 is 257 → {cache['257 is 257']}.")
    with st.expander("Як порахувати «глибокий» розмір — і до чого тут множина"):
        st.code(inspect.getsource(core.deep_size), language="python")
        st.caption("Один об'єкт може бути в контейнері кілька разів. Множина id() дає перевірку «вже рахували?» за O(1).")


# ---------------------------------------------------------------------------
# Вкладка 4 · NYC Taxi + DuckDB
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Підключаємо DuckDB…")
def get_connection(use_nyc):
    return core.connect(use_nyc=use_nyc)


@st.cache_data(show_spinner="Готуємо карту зон…")
def get_geojson():
    return core.zones_geojson()


def data_source_panel():
    """Повертає True, якщо працюємо зі справжніми даними NYC."""
    if core.parquet_ready():
        size = core.human_bytes(core.PARQUET.stat().st_size)
        use_nyc = not st.toggle("Використати згенеровані поїздки замість справжніх", value=False)
        if use_nyc:
            st.success(f"Справжні дані NYC TLC Yellow Taxi, січень 2023 · `{core.PARQUET.name}` · {size}")
        return use_nyc
    st.info(
        "Файлу з поїздками NYC ще немає. Можна завантажити його з офіційного сайту NYC Taxi & Limousine Commission "
        "(~45 МБ, один раз) — або працювати на згенерованих поїздках по справжніх зонах."
    )
    if st.button("⬇️ Завантажити дані NYC (~45 МБ)"):
        bar = st.progress(0.0, text="Завантаження…")
        try:
            core.download_parquet(lambda part: bar.progress(part, text=f"Завантаження… {part:.0%}"))
            st.rerun()
        except Exception as error:          # мережа, проксі, диск
            st.error(f"Не вдалося завантажити: {error}. Працюємо на згенерованих даних.")
    return False


def answer_rows(answer):
    if isinstance(answer, int):
        return [{"відповідь": answer}]
    rows = []
    for item in answer:
        if isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], tuple):
            rows.append({"звідки": item[0][0], "куди": item[0][1], "поїздок": item[1]})
        else:
            rows.append({f"#{i}": v for i, v in enumerate(item)})
    return rows


def db_tab():
    try:
        import duckdb  # noqa: F401
    except ImportError:
        st.error("Для цієї вкладки потрібен DuckDB: `pip install duckdb`")
        return

    st.markdown(
        """
        <div class="db-cards">
          <div class="db-card"><b>🗃️ Таблиця = список рядків</b>Реляційна база зберігає дані таблицями: <code>trips</code> —
          поїздки, <code>zones</code> — довідник зон. Кожен рядок — як кортеж, кожен стовпець має тип.</div>
          <div class="db-card"><b>🔑 Первинний ключ = ключ dict</b><code>zones.location_id</code> унікальний, як ключ
          словника. За ним одна таблиця «посилається» на іншу: <code>trips.pu_id → zones.location_id</code>.</div>
          <div class="db-card"><b>🧮 SQL описує «що», а не «як»</b>Ми пишемо <code>GROUP BY</code> чи <code>JOIN</code>,
          а база сама будує хеш-таблиці — ті самі, що Counter і dict у Python.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    use_nyc = data_source_panel()
    con = get_connection(use_nyc)
    total = core.total_trips(con)
    st.caption(f"У таблиці trips: {total:,} поїздок · у довіднику zones: "
               f"{con.execute('SELECT count(*) FROM zones').fetchone()[0]} зон.")
    with st.expander("Як виглядають таблиці"):
        st.dataframe(con.execute("SELECT * FROM trips LIMIT 5").df(), hide_index=True)
        st.dataframe(con.execute("SELECT * FROM zones ORDER BY location_id LIMIT 5").df(), hide_index=True)

    st.markdown('<div class="eyebrow">Ті самі питання — у Python і в SQL</div>', unsafe_allow_html=True)
    n = st.select_slider("Скільки поїздок взяти у вибірку", options=[10_000, 100_000, 500_000, 1_000_000],
                         value=100_000, format_func=lambda v: f"{v:,}".replace(",", " "))
    if st.button("Порахувати обома способами", type="primary"):
        with st.spinner("Вибірка, Python і SQL…"):
            rows, fetch_s = core.take_sample(con, min(n, total))
            st.session_state["db"] = {
                "key": (use_nyc, n), "rows_n": len(rows), "fetch_s": fetch_s,
                "results": core.compare_python_sql(con, rows),
                "full": core.full_table_timing(con),
                "keys": core.duplicate_keys(con), "inflation": core.join_inflation(con),
                "memory": core.row_memory(con, rows),
            }
            del rows
    saved = st.session_state.get("db")
    if not saved or saved["key"] != (use_nyc, n):
        return

    st.caption(f"Вибірка: {saved['rows_n']:,} поїздок · перенесення з DuckDB у список кортежів Python: "
               f"{core.human_time(saved['fetch_s'])}.")
    for result in saved["results"]:
        st.markdown(f"#### {result['title']}")
        left, right = st.columns(2)
        with left:
            st.markdown(f"**Python** · `{result['py_tool']}` · {core.human_time(result['py_s'])}")
            st.dataframe(answer_rows(result["py"])[:10], width="stretch", hide_index=True)
        with right:
            st.markdown(f"**SQL (DuckDB)** · {core.human_time(result['sql_s'])}")
            st.code(result["sql"], language="sql")
            st.dataframe(answer_rows(result["sql_answer"])[:10], width="stretch", hide_index=True)
        (st.success if result["match"] else st.error)(
            "Відповіді збігаються." if result["match"] else "Відповіді різні!")
    with st.expander("Python-код цих відповідей"):
        for func in (core.py_top_routes, core.py_distinct_zones, core.py_top_pickup_zones, core.py_avg_fare_by_borough):
            st.code(inspect.getsource(func), language="python")
    full_answer, full_s = saved["full"]
    st.info(f"А тепер SQL на **всіх {total:,}** поїздках одразу: топ маршрутів за {core.human_time(full_s)}. "
            f"DuckDB читає з файлу лише потрібні стовпці й рахує на C у кількох потоках, не створюючи "
            f"3 мільйони Python-об'єктів. Найпопулярніший маршрут: зона {full_answer[0][0]} → {full_answer[0][1]} "
            f"({full_answer[0][2]:,} поїздок).")

    st.markdown('<div class="eyebrow">EXPLAIN: хеш-таблиці всередині бази</div>', unsafe_allow_html=True)
    queries = {r["title"]: r["sql"] for r in saved["results"]}
    title = st.selectbox("План якого запиту показати", list(queries), index=2)
    plan = core.explain(con, queries[title])
    operators = core.hash_operators(plan)
    if operators:
        st.success(f"У плані: **{', '.join(operators)}**. HASH_GROUP_BY — це Counter/dict: ключ групи → лічильник. "
                   "HASH_JOIN — це словник-індекс: база кладе меншу таблицю (zones) у хеш-таблицю за ключем і для "
                   "кожної поїздки робить пошук за O(1) — як наш lookup.get(pu_id).")
    st.code(plan, language="text")

    st.markdown('<div class="eyebrow">Ключі мають бути унікальними — інакше JOIN бреше</div>', unsafe_allow_html=True)
    raw, unique, dupes = saved["keys"]
    infl = saved["inflation"]
    d1, d2, d3 = st.columns(3)
    d1.metric("Рядків у файлі зон", raw)
    d2.metric("Унікальних LocationID", unique)
    d3.metric("Зайвих поїздок після JOIN з повторами", f"+{infl['raw'] - infl['clean']:,}")
    st.markdown(
        f'<div class="warn">У файлі зон ключі {", ".join(f"{k} ({z}) ×{c}" for k, z, c in dupes)} повторюються — '
        "зона складається з кількох шматків карти. <b>dict</b> просто перезаписав повтор (ключ унікальний за "
        "означенням). <b>SQL JOIN</b> з таким довідником з'єднав кожну поїздку з кожним повтором — і поїздок "
        "«стало більше». Саме тому в базі даних ключ оголошують <code>PRIMARY KEY</code>: база не дасть вставити "
        "повтор.</div>",
        unsafe_allow_html=True,
    )
    if infl["missing"]:
        missing = ", ".join(f"{zone_id} ({count:,} поїздок)" for zone_id, count in infl["missing"])
        st.caption(f"Зон {missing} немає в довіднику. Python: lookup.get(id, 'Невідома зона'). "
                   "SQL: LEFT JOIN дає NULL, coalesce підставляє 'Невідома зона'.")

    st.markdown('<div class="eyebrow">Скільки важить одна поїздка</div>', unsafe_allow_html=True)
    mem = saved["memory"]
    entries = [("Python: кортеж (int, int, float)", mem["python"]), ("numpy-колонки (DuckDB → fetchnumpy)", mem["numpy"])]
    if mem["parquet"]:
        entries.append(("parquet на диску (стиснено, 19 стовпців)", mem["parquet"] / mem["total"]))
    fig = go.Figure(go.Bar(x=[v for _, v in entries], y=[k for k, _ in entries], orientation="h",
                           marker={"color": ["#eb6834", "#3d9970", "#2a78d6"][:len(entries)]},
                           text=[f"{v:.0f} Б → {core.human_bytes(v * mem['total'])} на {mem['total']:,}" for _, v in entries],
                           textposition="auto"))
    st.plotly_chart(base_layout(fig, 260, "Байт на одну поїздку (3 стовпці)", x_title="байт"), width="stretch")
    st.caption("Кожне число в Python — окремий об'єкт з заголовком; у колонці numpy/DuckDB — просто 8 байт підряд. "
               "Тому великі дані тримають у базі чи колонках, а в Python забирають уже відповідь.")

    st.markdown('<div class="eyebrow">Карта: звідки їдуть найчастіше</div>', unsafe_allow_html=True)
    try:
        geojson = get_geojson()
    except ImportError:
        st.info("Для карти потрібен geopandas: `pip install geopandas`")
        return
    counts = dict(core.pickups_by_zone(con))
    names = {f["properties"]["LocationID"]: f["properties"]["zone"] for f in geojson["features"]}
    ids = list(names)
    fig = go.Figure(go.Choropleth(
        geojson=geojson, featureidkey="properties.LocationID", locations=ids,
        z=[math.log10(counts.get(i, 0) + 1) for i in ids],
        text=[f"{names[i]}: {counts.get(i, 0):,} поїздок" for i in ids], hoverinfo="text",
        colorscale="YlOrRd", marker_line_width=0.3, marker_line_color="#ffffff",
        colorbar={"title": "поїздок", "tickvals": [0, 1, 2, 3, 4, 5],
                  "ticktext": ["1", "10", "100", "1 тис", "10 тис", "100 тис"]},
    ))
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=560, margin={"l": 0, "r": 0, "t": 10, "b": 0}, paper_bgcolor="#fcfcfb")
    st.plotly_chart(fig, width="stretch")
    st.caption("Колір — кількість посадок у зоні (лог-шкала). Назва для кожної зони — пошук у dict за LocationID.")


st.set_page_config(page_title="Таксі: хеш-таблиці", page_icon="🚕", layout="wide")
inject_styles()
show_intro()
tab_hash, tab_types, tab_memory, tab_db = st.tabs(
    ["🔬 Хеш-таблиця зсередини", "⚖️ list · tuple · set · dict", "🧠 Пам'ять", "🗄️ NYC Taxi + DuckDB"]
)
with tab_hash:
    hash_tab()
with tab_types:
    types_tab()
with tab_memory:
    memory_tab()
with tab_db:
    db_tab()
