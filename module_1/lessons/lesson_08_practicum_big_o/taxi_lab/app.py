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


def ratio_label(ratio):
    """Виміряне відношення → найближчий варіант відповіді."""
    return min(RATIO_OPTIONS, key=lambda option: abs(int(option[1]) - ratio))


def run_experiment(exp, sizes):
    rows = []
    for n in sizes:
        args = exp["make_input"](n)
        start = time.perf_counter()
        slow_answer, slow_steps = exp["slow"](*args)
        slow_seconds = time.perf_counter() - start
        start = time.perf_counter()
        fast_answer, fast_steps = exp["fast"](*args)
        fast_seconds = time.perf_counter() - start
        rows.append({
            "n": n,
            "slow_steps": slow_steps, "fast_steps": fast_steps,
            "slow_seconds": slow_seconds, "fast_seconds": fast_seconds,
            "same_answer": slow_answer == fast_answer,
        })
    for previous, row in zip(rows, rows[1:]):
        row["slow_ratio"] = row["slow_steps"] / previous["slow_steps"]
        row["fast_ratio"] = row["fast_steps"] / previous["fast_steps"]
    return rows


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
        height=380, margin={"l": 10, "r": 90, "t": 10, "b": 10},
        xaxis={"title": "кількість поїздок n", "gridcolor": "#ecebe8"},
        yaxis={"title": "кроків", "gridcolor": "#ecebe8"},
        plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb", hovermode="x unified",
        legend={"orientation": "h", "y": 1.08},
    )
    return fig


st.set_page_config(page_title="Таксі: Big O", page_icon="🚕", layout="wide")
st.title("🚕 Таксі: як росте робота програми")
st.write(
    "Диспетчерська служба таксі починала з тисячі поїздок на день. Місто росте, "
    "поїздок стає більше. Для кожної задачі диспетчера є два **правильні** рішення. "
    "Вони дають однакову відповідь, але по-різному поводяться, коли даних стає більше."
)

key = st.selectbox(
    "Задача диспетчера", list(EXPERIMENTS),
    format_func=lambda k: f"{EXPERIMENTS[k]['title']}",
)
exp = EXPERIMENTS[key]
st.info(exp["question"])

code_slow, code_fast = st.columns(2)
with code_slow:
    with st.expander("Повільне рішення — код"):
        st.code(inspect.getsource(exp["slow"]), language="python")
with code_fast:
    with st.expander("Швидке рішення — код"):
        st.code(inspect.getsource(exp["fast"]), language="python")

st.subheader("1. Передбач")
st.write("Поїздок стало **вдвічі більше**. У скільки разів зросте кількість кроків?")
guess_slow_col, guess_fast_col = st.columns(2)
guess_slow = guess_slow_col.radio("Повільне рішення", RATIO_OPTIONS, index=None, key=f"gs-{key}")
guess_fast = guess_fast_col.radio("Швидке рішення", RATIO_OPTIONS, index=None, key=f"gf-{key}")

st.subheader("2. Запусти")
max_n = st.select_slider(
    "Найбільша кількість поїздок у досліді",
    options=[800, 1600, 3200, 6400], value=3200,
    help="Дослід запускає обидва рішення для n/8, n/4, n/2 і n — щоразу вдвічі більше.",
)
sizes = [max_n // 8, max_n // 4, max_n // 2, max_n]
ready = guess_slow is not None and guess_fast is not None
if not ready:
    st.caption("Спершу обери обидва прогнози — так дослід покаже, чи збігається інтуїція з реальністю.")
if st.button("Запустити дослід", type="primary", disabled=not ready):
    with st.spinner("Рахуємо кроки…"):
        st.session_state["result"] = (key, max_n, run_experiment(exp, sizes))

result = st.session_state.get("result")
if result and result[0] == key and result[1] == max_n and ready:
    rows = result[2]
    last = rows[-1]

    if all(r["same_answer"] for r in rows):
        st.success("Обидва рішення дали однакову відповідь для кожного n — вони однаково правильні.")
    else:
        st.error("Відповіді різні — в одному з рішень помилка.")

    m1, m2, m3 = st.columns(3)
    m1.metric(f"Кроків при n = {last['n']:,}: повільне", f"{last['slow_steps']:,}")
    m2.metric("швидке", f"{last['fast_steps']:,}")
    m3.metric("Повільне робить більше в", f"{last['slow_steps'] / last['fast_steps']:,.0f} раз")

    st.plotly_chart(growth_chart(rows), use_container_width=True)

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
        use_container_width=True, hide_index=True,
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

    st.subheader("3. Місто росте")
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
