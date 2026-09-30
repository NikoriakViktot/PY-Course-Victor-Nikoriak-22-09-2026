# ============================================================
#  🍽️  Bistro Analytics — інтерфейс дашборда на Streamlit
#  Урок 7: Функції — реальний міні-проєкт
# ============================================================
#
#  Запуск:
#      pip install streamlit plotly seaborn
#      streamlit run app.py
#
#  Уся логіка — у pipeline.py (чисті функції: predicates, transformers,
#  reducers). Цей файл лише:
#      1. читає фільтри з бічної панелі;
#      2. викликає run_pipeline(...) — один виклик на кожну зміну;
#      3. показує результат: KPI, графіки, таблиці.
#
#  Як Streamlit оновлює сторінку: після кожної зміни фільтра він
#  перезапускає цей файл згори донизу. Тому run_pipeline() викликається
#  заново з новими аргументами — і повертає новий результат.
# ============================================================

import inspect

import plotly.graph_objects as go
import streamlit as st

from pipeline import (
    DAY_UA, SEX_UA, SMOKER_UA, TIME_UA, apply_filters, calc_kpis, enrich_order,
    load_orders, run_pipeline,
)

# Кольори: категоріальна палітра у фіксованому порядку + один колір для величин
DAY_COLORS = {"Thur": "#2a78d6", "Fri": "#eb6834", "Sat": "#1baf7a", "Sun": "#eda100"}
TIME_COLORS = {"Lunch": "#2a78d6", "Dinner": "#eb6834"}
SEX_COLORS = {"Male": "#2a78d6", "Female": "#eb6834"}
MAIN_COLOR = "#2a78d6"
GRID = "#ecebe8"

DEFAULTS = {
    "f_day": list(DAY_UA),
    "f_time": list(TIME_UA),
    "f_smoker": list(SMOKER_UA),
    "f_sex": list(SEX_UA),
    "f_size": (1, 6),
    "f_bill": (0.0, 55.0),
}


@st.cache_data
def cached_orders():
    """Завантажуємо 244 чеки один раз — Streamlit запам'ятовує результат."""
    return load_orders()


def style(fig, height=300, **layout):
    fig.update_layout(
        height=height, margin={"t": 30, "b": 10, "l": 10, "r": 60},
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis={"gridcolor": GRID}, yaxis={"gridcolor": GRID},
        **layout,
    )
    return fig


def reset_filters():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value


st.set_page_config(page_title="Bistro Analytics", page_icon="🍽️", layout="wide")
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)

ALL_ORDERS = cached_orders()

# ── Бічна панель: фільтри ────────────────────────────────────────────────────
with st.sidebar:
    st.header("Фільтри")
    days = st.multiselect("День", list(DAY_UA), format_func=DAY_UA.get, key="f_day")
    times = st.multiselect("Зміна", list(TIME_UA), format_func=TIME_UA.get, key="f_time")
    smoker = st.multiselect("Курці", list(SMOKER_UA), format_func=SMOKER_UA.get, key="f_smoker")
    sexes = st.multiselect("Стать", list(SEX_UA), format_func=SEX_UA.get, key="f_sex")
    size_range = st.slider("Гостей за столом", 1, 6, key="f_size")
    bill_range = st.slider("Сума рахунку, $", 0.0, 55.0, step=1.0, key="f_bill")
    st.button("Скинути фільтри", on_click=reset_filters)

# ── Один виклик pipeline на кожну зміну фільтрів ────────────────────────────
data = run_pipeline(ALL_ORDERS, days, times, smoker, size_range, bill_range, sexes)
kpis = data["kpis"]
enriched = data["enriched"]

st.title("🍽️ Bistro Analytics")
st.caption(
    f"Аналітика ресторану · урок 7 · {kpis['count']} з {len(ALL_ORDERS)} чеків · "
    "Filter → Map → Reduce"
)

if not enriched:
    st.warning("Немає чеків для вибраних фільтрів. Зміни фільтри або натисни «Скинути фільтри».")
    st.stop()

# ── KPI ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Виручка", f"${kpis['revenue']:,.0f}")
k2.metric("✨ Чайові", f"${kpis['tips']:,.0f}")
k3.metric("🧾 Середній чек", f"${kpis['avg_bill']:.2f}")
k4.metric("📊 Середні чайові", f"{kpis['avg_tip_pct']:.1f}%")

# ── Ряд 1: виручка по днях + обід / вечеря ──────────────────────────────────
left, right = st.columns([7, 5])
with left:
    st.subheader("Виручка по днях")
    rows = data["by_day"][::-1]
    fig = go.Figure(go.Bar(
        y=[r["day_ua"] for r in rows], x=[r["revenue"] for r in rows], orientation="h",
        marker_color=[DAY_COLORS.get(r["day"], MAIN_COLOR) for r in rows],
        text=[f"${r['revenue']:,.0f}" for r in rows], textposition="outside", cliponaxis=False,
        customdata=[(r["tips"], r["orders"], r["avg_bill"]) for r in rows],
        hovertemplate="<b>%{y}</b><br>Виручка: $%{x:,.2f}<br>Чайові: $%{customdata[0]:,.2f}"
                      "<br>Чеків: %{customdata[1]}<br>Середній чек: $%{customdata[2]:.2f}<extra></extra>",
    ))
    st.plotly_chart(style(fig, xaxis_title="Виручка, $"), use_container_width=True)
with right:
    st.subheader("Обід чи вечеря: чайові")
    rows = data["by_time"]
    fig = go.Figure(go.Bar(
        x=[r["time_ua"] for r in rows], y=[r["avg_tip_pct"] for r in rows],
        marker_color=[TIME_COLORS.get(r["time"], MAIN_COLOR) for r in rows],
        text=[f"{r['avg_tip_pct']}%" for r in rows], textposition="outside", cliponaxis=False,
        customdata=[(r["avg_bill"], r["orders"]) for r in rows],
        hovertemplate="<b>%{x}</b><br>Середні чайові: %{y:.1f}%<br>Середній чек: $%{customdata[0]:.2f}"
                      "<br>Чеків: %{customdata[1]}<extra></extra>",
    ))
    st.plotly_chart(style(fig, yaxis_title="Середні чайові, %"), use_container_width=True)

# ── Ряд 2: рахунок vs чайові + розмір столу ─────────────────────────────────
left, right = st.columns([7, 5])
with left:
    st.subheader("Рахунок і чайові (кожен чек)")
    fig = go.Figure()
    for day in DAY_UA:
        group = [o for o in enriched if o.day == day]
        if group:
            fig.add_trace(go.Scatter(
                x=[o.total_bill for o in group], y=[o.tip for o in group], mode="markers",
                name=DAY_UA[day],
                marker={"color": DAY_COLORS[day], "size": [6 + o.size * 2 for o in group],
                        "opacity": 0.75, "line": {"color": "white", "width": 1}},
                customdata=[(o.tip_pct, o.size) for o in group],
                hovertemplate="Рахунок: $%{x:.2f}<br>Чайові: $%{y:.2f}"
                              "<br>Чайові: %{customdata[0]:.1f}%<br>Гостей: %{customdata[1]}<extra>"
                              + DAY_UA[day] + "</extra>",
            ))
    st.plotly_chart(style(fig, xaxis_title="Рахунок, $", yaxis_title="Чайові, $",
                          legend={"orientation": "h", "y": 1.1}), use_container_width=True)
with right:
    st.subheader("Розмір столу → виручка")
    rows = data["by_size"]
    fig = go.Figure(go.Bar(
        x=[r["size_label"] for r in rows], y=[r["revenue"] for r in rows],
        marker_color=MAIN_COLOR,
        customdata=[(r["avg_tip_pct"], r["orders"]) for r in rows],
        hovertemplate="<b>%{x}</b><br>Виручка: $%{y:,.2f}<br>Середні чайові: %{customdata[0]:.1f}%"
                      "<br>Чеків: %{customdata[1]}<extra></extra>",
    ))
    st.plotly_chart(style(fig, yaxis_title="Виручка, $"), use_container_width=True)

# ── Ряд 3: розподіл чайових + стать ─────────────────────────────────────────
left, right = st.columns([7, 5])
with left:
    st.subheader("Розподіл чайових, %")
    tip_pcts = [o.tip_pct for o in enriched]
    fig = go.Figure(go.Histogram(
        x=tip_pcts, nbinsx=22, marker_color=MAIN_COLOR,
        marker_line={"color": "white", "width": 2},
        hovertemplate="Чайові: %{x}%<br>Чеків: %{y}<extra></extra>",
    ))
    fig.add_vline(x=kpis["avg_tip_pct"], line_dash="dash", line_color="#52514e",
                  annotation_text=f"середнє {kpis['avg_tip_pct']}%")
    st.plotly_chart(style(fig, xaxis_title="Чайові, %", yaxis_title="Чеків"), use_container_width=True)
with right:
    st.subheader("Виручка за статтю клієнта")
    rows = data["by_sex"]
    fig = go.Figure(go.Bar(
        x=[r["sex_ua"] for r in rows], y=[r["revenue"] for r in rows],
        marker_color=[SEX_COLORS.get(r["sex"], MAIN_COLOR) for r in rows],
        text=[f"{r['avg_tip_pct']}% чайових" for r in rows], textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Виручка: $%{y:,.2f}<extra></extra>",
    ))
    st.plotly_chart(style(fig, yaxis_title="Виручка, $"), use_container_width=True)

# ── Таблиці ─────────────────────────────────────────────────────────────────
st.subheader("🏆 Топ-5 чеків за чайовими")
st.dataframe(
    [{"День": o.day_ua, "Зміна": o.time_ua, "Гостей": o.size, "Рахунок, $": o.total_bill,
      "Чайові, $": o.tip, "Чайові, %": o.tip_pct} for o in data["top_tips"]],
    use_container_width=True, hide_index=True,
)
with st.expander(f"📋 Усі чеки після фільтрів · list[RichOrder] · {kpis['count']} записів"):
    st.dataframe(
        [{"День": o.day_ua, "Зміна": o.time_ua, "Гостей": o.size, "Стать": SEX_UA.get(o.sex, o.sex),
          "Курці": SMOKER_UA.get(o.smoker, o.smoker), "Рахунок, $": o.total_bill,
          "Чайові, $": o.tip, "Чайові, %": o.tip_pct, "$ на особу": o.bill_per_person}
         for o in enriched],
        use_container_width=True, hide_index=True,
    )

# ── Як це працює: зв'язок з уроком 7 ────────────────────────────────────────
with st.expander("🧩 Як це працює: функції з уроку 7"):
    st.markdown(
        "Кожна зміна фільтра перезапускає цей скрипт, і він робить **один виклик**:\n\n"
        "```python\n"
        "data = run_pipeline(ALL_ORDERS, days, times, smoker, size_range, bill_range, sexes)\n"
        "```\n\n"
        "Усередині `run_pipeline` — три кроки з уроку 7:\n\n"
        "1. **predicates** — `apply_filters()` залишає чеки, для яких усі перевірки `pred_*` дають `True`;\n"
        "2. **transformer** — `enrich_order()` робить з кожного `Order` новий `RichOrder` з полями "
        "`tip_pct`, `bill_per_person`;\n"
        "3. **reducers** — `calc_kpis()`, `group_by_day()`, `group_by_time()`… зводять список до чисел "
        "і таблиць для графіків.\n\n"
        "Жодна з цих функцій нічого не малює і не друкує — тому їх можна перевірити окремо "
        "(див. `test_pipeline.py`) і використати з іншим інтерфейсом."
    )
    code_left, code_right = st.columns(2)
    code_left.code(inspect.getsource(apply_filters), language="python")
    code_right.code(inspect.getsource(enrich_order) + "\n\n" + inspect.getsource(calc_kpis), language="python")
