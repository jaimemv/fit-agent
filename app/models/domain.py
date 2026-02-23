from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


GoalType = Literal["fat_loss", "muscle_gain", "strength", "recomposition", "health"]


class UserProfile(BaseModel):
    user_id: str
    age: int | None = None
    sex: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    goal: GoalType = "health"
    activity_level: str = "moderate"
    injuries: list[str] = Field(default_factory=list)
    equipment: list[str] = Field(default_factory=lambda: ["bodyweight"])
    food_preferences: list[str] = Field(default_factory=list)
    food_allergies: list[str] = Field(default_factory=list)


class BiometricEntry(BaseModel):
    user_id: str
    when: date
    weight_kg: float | None = None
    resting_hr: int | None = None
    sleep_hours: float | None = None
    stress_1_to_10: int | None = None
    soreness_1_to_10: int | None = None


class WorkoutLogEntry(BaseModel):
    user_id: str
    when: date
    exercise_name: str
    sets: int
    reps: int
    load_kg: float | None = None
    rpe_1_to_10: int | None = None
    pain_1_to_10: int | None = None


class NutritionLogEntry(BaseModel):
    user_id: str
    when: date
    calories: int | None = None
    protein_g: int | None = None
    carbs_g: int | None = None
    fats_g: int | None = None
    notes: str | None = None


class ExercisePrescription(BaseModel):
    name: str
    sets: int
    reps: str
    load_guidance: str
    rest_seconds: int


class WorkoutDayPlan(BaseModel):
    day_index: int
    title: str
    objective: str
    exercises: list[ExercisePrescription]


class WorkoutWeekPlan(BaseModel):
    user_id: str
    week_start: date
    rationale: str
    days: list[WorkoutDayPlan]


class LiveWorkoutSession(BaseModel):
    exercise_name: str
    sets: int
    reps: int
    load_kg: float | None = None
    rest_seconds: int = 90


class WorkoutFeedback(BaseModel):
    rpe_1_to_10: int = Field(ge=1, le=10)
    fatigue_1_to_10: int = Field(ge=1, le=10)
    pain_1_to_10: int = Field(ge=0, le=10)
    mood_1_to_10: int = Field(ge=1, le=10)
    notes: str | None = None


class SafetyDecision(BaseModel):
    level: Literal["ok", "caution", "stop"]
    reasons: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class WorkoutAdjustment(BaseModel):
    session: LiveWorkoutSession
    change_summary: str
    coach_message: str
    safety: SafetyDecision


class FoodItem(BaseModel):
    name: str
    amount: str


class Meal(BaseModel):
    name: str
    items: list[FoodItem]


class MealPlanDay(BaseModel):
    day_index: int
    target_kcal: int
    meals: list[Meal]


class MealPlanWeek(BaseModel):
    user_id: str
    rationale: str
    days: list[MealPlanDay]


class KnowledgeSnippet(BaseModel):
    source: str
    topic: str
    note: str
