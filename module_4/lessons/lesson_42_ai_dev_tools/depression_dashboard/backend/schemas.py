"""Вхід /api/predict — анкета, перевірена Pydantic (урок 42).

Було: сервер брав будь-який JSON і `pd.DataFrame([input_data])[features]` — зайві поля мовчки
ігнорувались (повзунок CGPA ні на що не впливав), похідні ознаки приходили від клієнта,
Age=-500 давав 200, а пропущене поле — 500 з текстом pandas у відповіді.
Стало: лише поля анкети, у межах шкал датасету; похідні ознаки рахує сервер (data_service.add_features).
"""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SleepDuration = Literal["Less than 5 hours", "5-6 hours", "7-8 hours", "More than 8 hours"]
SLEEP_HOURS: dict[str, float] = {"Less than 5 hours": 4.0, "5-6 hours": 5.5, "7-8 hours": 7.5,
                                 "More than 8 hours": 9.0}
DIETARY: dict[str, int] = {"Unhealthy": 0, "Moderate": 1, "Healthy": 2}


class StudentProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")          # невідоме поле — 422, а не тиша

    age: int = Field(ge=15, le=100)
    gender: Literal["Male", "Female"]
    sleep_duration: SleepDuration
    academic_pressure: float = Field(ge=0, le=5)
    work_pressure: float = Field(ge=0, le=5)
    study_satisfaction: float = Field(ge=0, le=5)
    job_satisfaction: float = Field(ge=0, le=5)
    work_study_hours: float = Field(ge=0, le=24)
    financial_stress: float = Field(ge=1, le=5)
    dietary_habits: Literal["Unhealthy", "Moderate", "Healthy"]
    family_history: bool
    suicidal_thoughts: bool

    def to_row(self) -> dict[str, float | int]:
        """Анкета → рядок у колонках датасету, як їх бачить модель до add_features."""
        return {
            "Age": self.age,
            "Academic Pressure": self.academic_pressure,
            "Work Pressure": self.work_pressure,
            "Study Satisfaction": self.study_satisfaction,
            "Job Satisfaction": self.job_satisfaction,
            "Sleep_hours": SLEEP_HOURS[self.sleep_duration],
            "Work/Study Hours": self.work_study_hours,
            "Financial Stress": self.financial_stress,
            "Gender_enc": int(self.gender == "Female"),
            "Family_History_enc": int(self.family_history),
            "Suicidal_enc": int(self.suicidal_thoughts),
            "Dietary_enc": DIETARY[self.dietary_habits],
        }
