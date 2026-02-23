from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.models.domain import (
    BiometricEntry,
    KnowledgeSnippet,
    LiveWorkoutSession,
    MealPlanWeek,
    NutritionLogEntry,
    UserProfile,
    WorkoutFeedback,
    WorkoutLogEntry,
)


class UpsertProfileRequest(BaseModel):
    profile: UserProfile


class CreateWorkoutPlanRequest(BaseModel):
    user_id: str
    week_start: date | None = None
    days_per_week: int = Field(default=4, ge=2, le=6)


class LiveAdjustWorkoutRequest(BaseModel):
    user_id: str
    session: LiveWorkoutSession
    feedback: WorkoutFeedback


class CreateMealPlanRequest(BaseModel):
    user_id: str
    days: int = Field(default=7, ge=1, le=14)
    meals_per_day: int = Field(default=4, ge=2, le=6)
    excluded_foods: list[str] = Field(default_factory=list)


class SubstituteMealRequest(BaseModel):
    user_id: str
    meal_plan: MealPlanWeek
    unwanted_food: str


class AskCoachRequest(BaseModel):
    user_id: str
    question: str
    domain: Literal["workout", "nutrition", "knowledge"] = "knowledge"
    context: dict[str, Any] = Field(default_factory=dict)


class AddBiometricRequest(BaseModel):
    entry: BiometricEntry


class AddWorkoutLogRequest(BaseModel):
    entry: WorkoutLogEntry


class AddNutritionLogRequest(BaseModel):
    entry: NutritionLogEntry


class AddKnowledgeSnippetRequest(BaseModel):
    snippet: KnowledgeSnippet
