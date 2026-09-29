import streamlit as st
import plotly.graph_objects as go
from ui.components.api_client import post_predict, post_train


def _gauge(prob: float, label: str) -> go.Figure:
    # урок 42: пороги — як у бекенді (_risk_label: 0.5 і 0.75); було 0.3/0.5 і смуги 30/60
    color = "#E53935" if prob >= 0.75 else "#FFA726" if prob >= 0.5 else "#4CAF50"
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(prob * 100, 1),
        title={"text": f"Depression Probability<br><sub>{label}</sub>"},
        delta={"reference": 50, "increasing": {"color": "#E53935"},
               "decreasing": {"color": "#4CAF50"}},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%"},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 50], "color": "#E8F5E9"},
                {"range": [50, 75], "color": "#FFF3E0"},
                {"range": [75, 100], "color": "#FFEBEE"},
            ],
            "threshold": {"line": {"color": "red", "width": 4}, "value": 50},
        },
        number={"suffix": "%"},
    ))
    fig.update_layout(height=280, margin=dict(t=60, b=20))
    return fig


_SLEEP_OPTIONS = ["Less than 5 hours", "5-6 hours", "7-8 hours", "More than 8 hours"]
_DIETARY_OPTIONS = ["Unhealthy", "Moderate", "Healthy"]


def render():
    st.header("🤖 Depression Risk Prediction")
    st.caption("RandomForest classifier trained on 27,901 student records")
    # урок 42: застосунок оцінює ризик депресії й питає про суїцидальні думки — без застереження не можна
    st.warning("Навчальна модель на відкритому датасеті, а не діагноз. Якщо вам зараз важко — "
               "зверніться до фахівця; в Україні безкоштовна лінія психологічної підтримки: 7333 (Lifeline Ukraine).")

    with st.form("prediction_form"):
        st.subheader("Personal Profile")
        c1, c2, c3 = st.columns(3)
        age = c1.slider("Age", 15, 60, 22)
        gender = c2.selectbox("Gender", ["Male", "Female"])
        sleep_label = c3.selectbox("Sleep Duration", _SLEEP_OPTIONS, index=1)

        st.subheader("Academic & Work")
        c4, c5, c6 = st.columns(3)
        academic_pressure = c4.slider("Academic Pressure (0-5)", 0.0, 5.0, 3.0, 0.5)
        # урок 42: у датасеті (студенти) Work Pressure і Job Satisfaction майже завжди 0 —
        # старі значення за замовчуванням 1.0 і 3.0 були поза навчальними даними
        work_pressure = c5.slider("Work Pressure (0-5)", 0.0, 5.0, 0.0, 0.5)
        work_hours = c6.slider("Work/Study Hours per day", 0.0, 16.0, 6.0, 0.5)

        st.subheader("Lifestyle & Wellbeing")
        # урок 42: повзунок CGPA прибрано — CGPA не входить в ознаки моделі й ні на що не впливав
        c8, c9 = st.columns(2)
        study_sat = c8.slider("Study Satisfaction (0-5)", 0.0, 5.0, 3.0, 0.5)
        job_sat = c9.slider("Job Satisfaction (0-5)", 0.0, 5.0, 0.0, 0.5)

        c10, c11, c12 = st.columns(3)
        financial_stress = c10.slider("Financial Stress (1-5)", 1.0, 5.0, 2.0, 0.5)
        diet_label = c11.selectbox("Dietary Habits", _DIETARY_OPTIONS, index=1)
        family_history = c12.checkbox("Family History of Mental Illness")
        suicidal_thoughts = st.checkbox("History of Suicidal Thoughts")

        submitted = st.form_submit_button("🔮 Predict Depression Risk", type="primary")

    if submitted:
        # урок 42: лише анкета; похідні ознаки (Risk_Score, Pressure_Sum…) рахує сервер
        payload = {
            "age": age,
            "gender": gender,
            "sleep_duration": sleep_label,
            "academic_pressure": academic_pressure,
            "work_pressure": work_pressure,
            "study_satisfaction": study_sat,
            "job_satisfaction": job_sat,
            "work_study_hours": work_hours,
            "financial_stress": financial_stress,
            "dietary_habits": diet_label,
            "family_history": family_history,
            "suicidal_thoughts": suicidal_thoughts,
        }

        with st.spinner("Running inference …"):
            result = post_predict(payload)

        st.divider()
        st.subheader("Prediction Result")

        risk_colors = {"Low": "green", "Medium": "orange", "High": "red"}
        risk = result["risk_level"]
        st.markdown(
            f"### Risk Level: :{risk_colors[risk]}[{risk}]",
            unsafe_allow_html=False,
        )

        st.plotly_chart(_gauge(result["probability_depressed"], risk), use_container_width=True)

        col1, col2 = st.columns(2)
        col1.metric("Probability Depressed", f"{result['probability_depressed']:.1%}")
        col2.metric("Probability Not Depressed", f"{result['probability_not_depressed']:.1%}")

        if risk == "High":
            st.error(
                "⚠️ High risk profile detected. Key factors: financial stress, "
                "sleep deficit, academic pressure. Consider professional consultation."
            )
        elif risk == "Medium":
            st.warning("Moderate risk. Monitor sleep, stress, and workload.")
        else:
            st.success("Low risk profile. Keep maintaining healthy habits.")

    st.divider()
    with st.expander("🔄 Re-train Models (admin)"):
        # урок 42: навчання перезаписує модель — лише з токеном адміністратора (ADMIN_TOKEN бекенду)
        token = st.text_input("Admin token", type="password")
        if st.button("Train all models (takes ~30s)", type="secondary", disabled=not token):
            with st.spinner("Training RandomForest, KMeans, IsolationForest …"):
                result = post_train(token)
            st.success(f"Training complete! AUC={result['metrics']['auc']:.4f} | "
                       f"Accuracy={result['metrics']['accuracy']:.4f}")
