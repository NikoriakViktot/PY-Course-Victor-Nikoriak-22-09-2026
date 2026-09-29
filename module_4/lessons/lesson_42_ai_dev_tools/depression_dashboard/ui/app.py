import sys
from pathlib import Path

# allow absolute imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

st.set_page_config(
    page_title="Depression Analytics Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# урок 42: папка pages/ поруч зі скриптом — це мультисторінковий режим Streamlit: у меню з'являлись
# 5 зайвих порожніх сторінок. Модулі розділів тепер у views/.
from ui.views import overview, correlations, clustering, anomalies, prediction  # noqa: E402

PAGES = {
    "📊 Overview": overview,
    "📈 Correlations": correlations,
    "🧠 Clustering": clustering,
    "⚠️ Anomaly Detection": anomalies,
    "🤖 Prediction": prediction,
}


def main():
    st.sidebar.title("🧠 Depression Analytics")
    st.sidebar.markdown("*Навчальний проєкт. Не медичний інструмент.*")
    st.sidebar.divider()

    page = st.sidebar.radio("Navigation", list(PAGES.keys()))

    st.sidebar.divider()
    st.sidebar.markdown(
        "**Datasets**\n"
        "- Student Depression (27,901 rows)\n"
        "- Tech Burnout 2026 (100,000 rows)\n"
    )
    st.sidebar.markdown(
        "**Stack**\n"
        "Flask · Streamlit · Scikit-learn\n"
        "Pandas · Plotly · Docker"
    )

    PAGES[page].render()


if __name__ == "__main__":
    main()
