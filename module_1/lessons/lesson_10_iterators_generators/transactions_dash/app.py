"""
╔══════════════════════════════════════════════════════════════════════════════╗
║   Dash-застосунок: Потокова Симуляція Біржових Транзакцій                    ║
║   Урок 10 · Ітератори та Генератори · Real-World Pipeline                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║   Запуск:  pip install dash plotly                                           ║
║            python app.py        →  http://127.0.0.1:8059                     ║
║                                                                              ║
║   dcc.Interval → update_data() → STATE.advance(n) → next(генератор) × n      ║
║                → render()       → STATE.snapshot() → графіки                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

Генератори й стан — у stream_core.py. Тут лише інтерфейс.

Що виправлено порівняно з першою версією застосунку:
  1. next() спільного генератора викликався з кількох потоків Dash одночасно →
     «ValueError: generator already executing». Тепер next() — лише під замком
     у MarketState.advance().
  2. Графіки читали deque, поки в них писали. Тепер вони малюють копію
     (MarketState.snapshot()), а всі графіки будуються з одного знімка.
  3. Файл завантажувався в пам'ять цілком і перемішувався. Тепер джерело за
     замовчуванням — нескінченний генератор, а файл читається потоково
     (replay_ndjson), угоди компаній зливаються за часом.
  4. Вісь X була рядками «HH:MM:SS» з різних днів упереміш. Тепер час угод
     лише зростає і на осі — справжній datetime.
  5. Якщо вибраних компаній не було у файлі, генератор крутився вічно.
     Тепер потік завершується, а застосунок показує «потік завершився».
  6. Зміна набору компаній перезапускала генератор і скидала ціни.
     Тепер генератор один на всі компанії, вибір лише фільтрує відображення.
"""

import os

import dash
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html

from stream_core import COMPANIES, MarketState, moving_average, replay_ndjson, transaction_stream

DEFAULT_SELECTED = ["Нафтогаз", "Розетка", "Київстар"]

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_CANDIDATES = [
    os.path.join(HERE, "data", "transactions.ndjson"),
    os.path.join(HERE, "..", "data", "transactions.ndjson"),   # файл з ноутбука уроку 10
]


def data_path():
    for path in DATA_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


def make_stream(source):
    path = data_path()
    if source == "file" and path:
        return replay_ndjson(path, list(COMPANIES))
    return transaction_stream(COMPANIES)


STATE = MarketState(make_stream("generator"), window=80)

DARK_BG    = "#0F1117"
CARD_BG    = "#1A1D27"
BORDER     = "#2D3147"
TEXT_MUTED = "#8B92A5"

PLOTLY_LAYOUT = dict(
    paper_bgcolor=DARK_BG,
    plot_bgcolor=CARD_BG,
    font=dict(color="#CBD5E1", size=12),
    margin=dict(l=10, r=10, t=36, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=BORDER, borderwidth=1),
    xaxis=dict(gridcolor=BORDER, showgrid=True, zeroline=False),
    yaxis=dict(gridcolor=BORDER, showgrid=True, zeroline=False),
)


# ─────────────────────────────────────────────────────────────────────────────
# ПОБУДОВА ГРАФІКІВ — з одного знімка стану
# ─────────────────────────────────────────────────────────────────────────────

def waiting(title):
    fig = go.Figure()
    fig.update_layout(title=title, **PLOTLY_LAYOUT)
    return fig


def build_main_chart(snap, focus, ma_window):
    points = snap["series"].get(focus, [])
    if len(points) < 2:
        return waiting(f"{focus} — очікування даних...")
    times = [t for t, _, _ in points]
    prices = [p for _, p, _ in points]
    color = COMPANIES[focus]["color"]
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times, y=moving_average(prices, ma_window), mode="lines",
        line=dict(color=color, width=1, dash="dot"), name=f"MA({ma_window})", opacity=0.6,
    ))
    fig.add_trace(go.Scatter(
        x=times, y=prices, mode="lines", fill="tonexty", fillcolor=f"rgba({r},{g},{b},0.08)",
        line=dict(color=color, width=2.5), name=focus,
    ))
    fig.add_trace(go.Scatter(
        x=[times[-1]], y=[prices[-1]], mode="markers",
        marker=dict(color=color, size=10, line=dict(color="white", width=2)),
        name="Остання угода", showlegend=False,
    ))
    fig.update_layout(title=dict(text=f"📊  {focus}  —  Ціна акції (₴)", x=0.01, font_size=14),
                      **PLOTLY_LAYOUT)
    return fig


def build_multi_chart(snap, selected):
    fig = go.Figure()
    for name in selected:
        points = snap["series"].get(name, [])
        base = snap["first_price"].get(name)
        if len(points) < 2 or not base:
            continue
        fig.add_trace(go.Scatter(
            x=[t for t, _, _ in points], y=[p / base * 100 for _, p, _ in points], mode="lines",
            line=dict(color=COMPANIES[name]["color"], width=1.8), name=name,
        ))
    if not fig.data:
        return waiting("📉  Нормалізовані ціни — очікування даних...")
    fig.update_layout(title=dict(text="📉  Нормалізовані ціни (перша угода = 100)", x=0.01, font_size=13),
                      **PLOTLY_LAYOUT)
    fig.update_yaxes(ticksuffix=" %")
    return fig


def build_volume_chart(snap, selected):
    fig = go.Figure()
    for name in selected:
        points = snap["series"].get(name, [])
        if points:
            fig.add_trace(go.Bar(
                x=[t for t, _, _ in points], y=[v for _, _, v in points], name=name,
                marker_color=COMPANIES[name]["color"], opacity=0.75,
            ))
    fig.update_layout(title=dict(text="📦  Обсяг торгів (акцій/угода)", x=0.01, font_size=13),
                      barmode="stack", **PLOTLY_LAYOUT)
    return fig


def build_heatmap(snap, selected):
    changes = [snap["last"][n]["change_pct"] if n in snap["last"] else 0.0 for n in selected]
    fig = go.Figure(go.Bar(
        y=selected, x=changes, orientation="h",
        marker=dict(color=changes, colorscale=[[0, "#F87171"], [0.5, "#334155"], [1, "#34D399"]],
                    cmin=-2, cmax=2, showscale=True, colorbar=dict(title="Δ%", thickness=10, len=0.7)),
        text=[f"{c:+.3f}%" for c in changes], textposition="outside",
    ))
    fig.update_layout(title=dict(text="🌡  Остання зміна ціни (%)", x=0.01, font_size=13), **PLOTLY_LAYOUT)
    fig.update_xaxes(range=[-3, 3], gridcolor=BORDER)
    return fig


def build_metrics(snap, selected):
    cards = []
    for name in selected:
        tx = snap["last"].get(name)
        price = tx["price"] if tx else COMPANIES[name]["base"]
        change = tx["change_pct"] if tx else 0.0
        arrow = "▲" if change >= 0 else "▼"
        cards.append(html.Div([
            html.Div(f"{name} · {snap['counts'].get(name, 0):,} угод",
                     style={"color": TEXT_MUTED, "fontSize": "0.78rem", "marginBottom": "4px"}),
            html.Div(f"₴ {price:,.2f}",
                     style={"color": "#E2E8F0", "fontSize": "1.35rem", "fontWeight": "700"}),
            html.Div(f"{arrow} {abs(change):.3f}%",
                     style={"color": "#34D399" if change >= 0 else "#F87171", "fontSize": "0.88rem"}),
        ], style={"background": CARD_BG, "border": f"1px solid {BORDER}", "borderRadius": "12px",
                  "padding": "14px 18px", "flex": "1", "minWidth": "110px"}))
    return html.Div(cards, style={"display": "flex", "gap": "10px", "flexWrap": "wrap"})


def build_tape(snap, selected):
    rows = []
    for tx in reversed(snap["tape"]):
        if tx["company"] not in selected:
            continue
        c = tx["change_pct"]
        rows.append(html.Div([
            html.Span(tx["time"].strftime("%H:%M:%S"), style={"width": "70px", "color": TEXT_MUTED}),
            html.Span(tx["company"], style={"width": "110px", "fontWeight": "700", "color": "#CBD5E1"}),
            html.Span(f"₴ {tx['price']:,.2f}", style={"width": "100px", "color": "#CBD5E1"}),
            html.Span(f"{'▲' if c >= 0 else '▼'}{abs(c):.3f}%",
                      style={"width": "80px", "color": "#34D399" if c >= 0 else "#F87171"}),
            html.Span(f"{tx['volume']:,} акц.", style={"color": TEXT_MUTED}),
        ], style={"display": "flex", "justifyContent": "space-between", "padding": "5px 10px",
                  "borderBottom": f"1px solid {BORDER}", "fontSize": "0.82rem"}))
    return html.Div([
        html.Div(f"⏱ Останні угоди · усього оброблено {snap['total']:,}",
                 style={"color": "#94A3B8", "fontSize": "0.8rem", "padding": "0 10px 6px"}),
        *rows,
    ], style={"background": CARD_BG, "border": f"1px solid {BORDER}", "borderRadius": "12px",
              "padding": "10px", "marginTop": "4px"})


# ─────────────────────────────────────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────────────────────────────────────

_label_style = {"color": "#CBD5E1", "fontSize": "0.85rem", "marginBottom": "6px",
                "marginTop": "14px", "display": "block"}
_hr_style = {"borderColor": BORDER, "margin": "12px 0"}
_code_style = {"backgroundColor": "#0F1117", "padding": "1px 4px", "borderRadius": "3px"}
_tab_style = {"backgroundColor": CARD_BG, "color": TEXT_MUTED, "border": f"1px solid {BORDER}",
              "borderBottom": "none", "padding": "8px 16px", "fontSize": "0.9rem"}
_tab_selected_style = {"backgroundColor": DARK_BG, "color": "#E2E8F0", "border": f"1px solid {BORDER}",
                       "borderBottom": "2px solid #6366F1", "padding": "8px 16px",
                       "fontSize": "0.9rem", "fontWeight": "700"}


def slider(id_, lo, hi, step, value, marks):
    return html.Div(dcc.Slider(id=id_, min=lo, max=hi, step=step, value=value,
                               marks={m: str(m) for m in marks},
                               tooltip={"placement": "bottom", "always_visible": False}),
                    style={"marginBottom": "4px"})


sidebar = html.Div([
    html.H3("⚙️ Панель керування", style={"color": "#E2E8F0", "margin": "0 0 4px 0", "fontSize": "1rem"}),
    html.Hr(style=_hr_style),

    html.Label("Джерело даних", style=_label_style),
    dcc.RadioItems(
        id="source",
        options=[
            {"label": "  Генератор (нескінченний потік)", "value": "generator"},
            {"label": "  Файл NDJSON з ноутбука" + ("" if data_path() else " — файл не знайдено"),
             "value": "file", "disabled": data_path() is None},
        ],
        value="generator",
        labelStyle={"display": "block", "color": "#CBD5E1", "fontSize": "0.85rem", "padding": "3px 0"},
        inputStyle={"marginRight": "6px", "accentColor": "#6366F1"},
    ),

    html.Label("Компанії", style=_label_style),
    dcc.Checklist(
        id="selected-companies",
        options=[{"label": f"  {name}", "value": name} for name in COMPANIES],
        value=DEFAULT_SELECTED,
        labelStyle={"display": "block", "color": "#CBD5E1", "fontSize": "0.88rem",
                    "padding": "3px 0", "cursor": "pointer"},
        inputStyle={"marginRight": "6px", "accentColor": "#6366F1"},
    ),

    html.Hr(style=_hr_style),
    html.Label("Розмір вікна (точок на компанію)", style=_label_style),
    slider("window-size", 20, 300, 10, 80, [20, 80, 160, 300]),
    html.Label("Ковзне середнє (MA)", style=_label_style),
    slider("ma-window", 3, 30, 1, 7, [3, 7, 15, 30]),
    html.Label("Затримка між угодами (сек)", style=_label_style),
    slider("speed", 0.05, 1.5, 0.05, 0.25, [0.05, 0.25, 0.75, 1.5]),
    html.Label("Оновлювати графіки кожні N угод", style=_label_style),
    slider("refresh-every", 1, 20, 1, 5, [1, 5, 10, 20]),

    html.Hr(style=_hr_style),
    html.Label("Фокус основного графіка", style=_label_style),
    dcc.Dropdown(
        id="focus-company",
        options=[{"label": name, "value": name} for name in DEFAULT_SELECTED],
        value=DEFAULT_SELECTED[0], clearable=False,
        style={"color": "#0F1117", "fontSize": "0.88rem"},
    ),

    html.Hr(style=_hr_style),
    dcc.Checklist(
        id="is-running",
        options=[{"label": "  ▶  Запустити стрімінг", "value": "run"}],
        value=["run"],
        labelStyle={"color": "#CBD5E1", "fontSize": "0.9rem", "cursor": "pointer", "fontWeight": "600"},
        inputStyle={"marginRight": "6px", "accentColor": "#34D399"},
    ),

    html.Div([
        html.Span("🧠 ", style={"fontWeight": "bold"}), html.B("Як це працює:"), html.Br(),
        "Угоди дає генератор ", html.Code("transaction_stream()", style=_code_style),
        " — нескінченний ", html.Code("while True", style=_code_style), " + ",
        html.Code("yield", style=_code_style), ".", html.Br(), html.Br(),
        "Кожен тік бере з нього N угод через ", html.Code("next()", style=_code_style),
        ". У пам'яті — лише останні точки вікна (", html.Code("deque(maxlen)", style=_code_style),
        "), а не вся історія.", html.Br(), html.Br(),
        "Це і є ", html.B("Infinite Stream Pattern"), ".",
    ], style={"background": "linear-gradient(135deg, #1E293B 0%, #0F1117 100%)",
              "border": "1px solid #334155", "borderLeft": "4px solid #6366F1", "borderRadius": "8px",
              "padding": "12px 16px", "marginTop": "16px", "fontSize": "0.82rem", "color": "#94A3B8",
              "lineHeight": "1.6"}),
], style={"width": "280px", "minWidth": "280px", "backgroundColor": CARD_BG,
          "borderRight": f"1px solid {BORDER}", "padding": "20px 16px", "overflowY": "auto",
          "height": "100vh", "position": "sticky", "top": "0"})

main_content = html.Div([
    html.Div([
        html.Div([
            html.H1("📈 Stock Streaming — Генераторна Симуляція",
                    style={"color": "#E2E8F0", "margin": "0", "fontSize": "1.5rem"}),
            html.P("Урок 10 · Ітератори та Генератори · Real-World Pipeline",
                   style={"color": TEXT_MUTED, "margin": "4px 0 0 0", "fontSize": "0.85rem"}),
        ]),
        html.Div(id="status-indicator", style={"alignSelf": "center", "fontSize": "1rem", "fontWeight": "700"}),
    ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "flex-start",
              "marginBottom": "12px"}),
    html.Hr(style=_hr_style),
    html.Div(id="metrics-row", style={"marginBottom": "16px"}),
    dcc.Tabs(id="main-tabs", children=[
        dcc.Tab(label="Фокус: одна компанія", style=_tab_style, selected_style=_tab_selected_style,
                children=[dcc.Graph(id="main-chart", config={"displayModeBar": False},
                                    style={"height": "340px"})]),
        dcc.Tab(label="Порівняння (нормалізовано)", style=_tab_style, selected_style=_tab_selected_style,
                children=[dcc.Graph(id="multi-chart", config={"displayModeBar": False},
                                    style={"height": "340px"})]),
    ]),
    html.Div([
        html.Div(dcc.Graph(id="volume-chart", config={"displayModeBar": False}, style={"height": "280px"}),
                 style={"flex": "3"}),
        html.Div(dcc.Graph(id="heatmap", config={"displayModeBar": False}, style={"height": "280px"}),
                 style={"flex": "2"}),
    ], style={"display": "flex", "gap": "12px", "marginTop": "12px", "marginBottom": "16px"}),
    html.Div(id="trades-tape"),
    dcc.Interval(id="interval", interval=1250, n_intervals=0, disabled=False),
    dcc.Store(id="tick-store", data=0),
    dcc.Store(id="source-store"),
], style={"flex": "1", "backgroundColor": DARK_BG, "padding": "20px 24px", "overflowY": "auto",
          "minHeight": "100vh"})

app = dash.Dash(__name__, title="Stock Streaming — Генератори Python")
app.index_string = f"""<!DOCTYPE html>
<html>
<head>
    {{%metas%}}
    <title>{{%title%}}</title>
    {{%favicon%}}
    {{%css%}}
    <style>
        body, html {{ background-color: {DARK_BG}; margin: 0; padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        * {{ box-sizing: border-box; }}
        .Select-control, .Select-menu-outer {{ background-color: {DARK_BG} !important;
            border-color: {BORDER} !important; color: #CBD5E1 !important; }}
        .Select-value-label, .Select-option {{ color: #CBD5E1 !important; }}
        .rc-slider-track {{ background-color: #6366F1 !important; }}
        .rc-slider-handle {{ border-color: #6366F1 !important; background-color: #6366F1 !important; }}
    </style>
</head>
<body>
    {{%app_entry%}}
    <footer>{{%config%}}{{%scripts%}}{{%renderer%}}</footer>
</body>
</html>"""
app.layout = html.Div([sidebar, main_content],
                      style={"display": "flex", "minHeight": "100vh", "backgroundColor": DARK_BG})


# ─────────────────────────────────────────────────────────────────────────────
# CALLBACKS
# ─────────────────────────────────────────────────────────────────────────────

@app.callback(
    Output("interval", "interval"),
    Output("interval", "disabled"),
    Input("speed", "value"),
    Input("refresh-every", "value"),
    Input("is-running", "value"),
)
def configure_interval(speed, refresh_every, is_running):
    interval = max(50, int((speed or 0.25) * (refresh_every or 5) * 1000))
    return interval, not is_running


@app.callback(
    Output("focus-company", "options"),
    Output("focus-company", "value"),
    Input("selected-companies", "value"),
    State("focus-company", "value"),
)
def sync_focus_options(selected, current_focus):
    selected = selected or DEFAULT_SELECTED
    value = current_focus if current_focus in selected else selected[0]
    return [{"label": name, "value": name} for name in selected], value


@app.callback(
    Output("source-store", "data"),
    Input("source", "value"),
    State("source-store", "data"),
)
def switch_source(source, current):
    """Нове джерело — новий генератор і стан з нуля. Та сама вибірка — нічого не чіпаємо."""
    if current is not None and source != current:
        STATE.replace_stream(make_stream(source))
    return source


@app.callback(
    Output("tick-store", "data"),
    Input("interval", "n_intervals"),
    State("window-size", "value"),
    State("refresh-every", "value"),
    State("tick-store", "data"),
    prevent_initial_call=True,
)
def update_data(n_intervals, window_size, refresh_every, tick):
    """Бере з генератора N угод. next() викликається лише всередині STATE.advance() під замком."""
    STATE.set_window(window_size or 80)
    STATE.advance(refresh_every or 5)
    return (tick or 0) + 1


@app.callback(
    Output("status-indicator", "children"),
    Output("metrics-row", "children"),
    Output("main-chart", "figure"),
    Output("multi-chart", "figure"),
    Output("volume-chart", "figure"),
    Output("heatmap", "figure"),
    Output("trades-tape", "children"),
    Input("tick-store", "data"),
    Input("is-running", "value"),
    State("selected-companies", "value"),
    State("focus-company", "value"),
    State("ma-window", "value"),
)
def render(tick, is_running, selected, focus, ma_window):
    """Усі графіки — з одного знімка стану, тож вони завжди узгоджені між собою."""
    snap = STATE.snapshot()
    selected = selected or DEFAULT_SELECTED
    focus = focus if focus in COMPANIES else selected[0]
    if snap["finished"]:
        status = html.Span("⏹ Потік завершився", style={"color": "#F87171"})
    elif is_running:
        status = html.Span("🟢 Live", style={"color": "#34D399"})
    else:
        status = html.Span("⏸ Пауза", style={"color": "#94A3B8"})
    return (
        status,
        build_metrics(snap, selected),
        build_main_chart(snap, focus, ma_window or 7),
        build_multi_chart(snap, selected),
        build_volume_chart(snap, selected),
        build_heatmap(snap, selected),
        build_tape(snap, selected),
    )


if __name__ == "__main__":
    app.run(debug=False, port=8059)
