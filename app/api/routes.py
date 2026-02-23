from fastapi import APIRouter

from app.agents.orchestrator import CoachOrchestrator
from app.core.config import settings
from app.models.domain import MealPlanWeek, UserProfile, WorkoutAdjustment, WorkoutWeekPlan
from app.models.requests import (
    AddBiometricRequest,
    AddKnowledgeSnippetRequest,
    AddNutritionLogRequest,
    AddWorkoutLogRequest,
    AskCoachRequest,
    CreateMealPlanRequest,
    CreateWorkoutPlanRequest,
    LiveAdjustWorkoutRequest,
    SubstituteMealRequest,
    UpsertProfileRequest,
)
from app.models.responses import AskCoachResponse, IngestResponse
from app.repositories.factory import build_repository

router = APIRouter(prefix="/v1", tags=["coach"])
_repository = build_repository(settings)
_orchestrator = CoachOrchestrator(repository=_repository)


@router.post("/profile", response_model=UserProfile)
def upsert_profile(request: UpsertProfileRequest) -> UserProfile:
    return _orchestrator.upsert_profile(request)


@router.post("/workouts/plan", response_model=WorkoutWeekPlan)
def create_workout_plan(request: CreateWorkoutPlanRequest) -> WorkoutWeekPlan:
    return _orchestrator.create_workout_plan(request)


@router.post("/workouts/live-adjust", response_model=WorkoutAdjustment)
def live_adjust_workout(request: LiveAdjustWorkoutRequest) -> WorkoutAdjustment:
    return _orchestrator.live_adjust_workout(request)


@router.post("/nutrition/plan", response_model=MealPlanWeek)
def create_meal_plan(request: CreateMealPlanRequest) -> MealPlanWeek:
    return _orchestrator.create_meal_plan(request)


@router.post("/nutrition/substitute", response_model=MealPlanWeek)
def substitute_food(request: SubstituteMealRequest) -> MealPlanWeek:
    return _orchestrator.substitute_meal(request)


@router.post("/coach/ask", response_model=AskCoachResponse)
def ask_coach(request: AskCoachRequest) -> AskCoachResponse:
    return _orchestrator.ask(request)


@router.post("/data/biometrics", response_model=IngestResponse)
def add_biometric(request: AddBiometricRequest) -> IngestResponse:
    return _orchestrator.add_biometric(request)


@router.post("/data/workouts/log", response_model=IngestResponse)
def add_workout_log(request: AddWorkoutLogRequest) -> IngestResponse:
    return _orchestrator.add_workout_log(request)


@router.post("/data/nutrition/log", response_model=IngestResponse)
def add_nutrition_log(request: AddNutritionLogRequest) -> IngestResponse:
    return _orchestrator.add_nutrition_log(request)


@router.post("/knowledge/snippets", response_model=IngestResponse)
def add_knowledge_snippet(request: AddKnowledgeSnippetRequest) -> IngestResponse:
    return _orchestrator.add_knowledge_snippet(request)
