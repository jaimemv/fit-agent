from datetime import date, timedelta

from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.nutrition_agent import NutritionAgent
from app.agents.safety_agent import SafetyAgent
from app.agents.workout_agent import WorkoutPlannerAgent
from app.models.domain import MealPlanWeek, WorkoutAdjustment, WorkoutWeekPlan
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
from app.repositories.base import Repository


class CoachOrchestrator:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.safety_agent = SafetyAgent()
        self.workout_agent = WorkoutPlannerAgent()
        self.nutrition_agent = NutritionAgent()
        self.knowledge_agent = KnowledgeAgent(repository=repository)

    def upsert_profile(self, request: UpsertProfileRequest):
        profile = self.repository.upsert_profile(request.profile)
        if not self.repository.get_recent_biometrics(profile.user_id):
            self.repository.seed_demo_data(profile.user_id)
        return profile

    def create_workout_plan(self, request: CreateWorkoutPlanRequest) -> WorkoutWeekPlan:
        profile = self._get_profile_or_default(request.user_id)
        recent_workouts = self.repository.get_recent_workouts(request.user_id, limit=50)
        last_30d = [w for w in recent_workouts if w.when >= (date.today() - timedelta(days=30))]
        return self.workout_agent.create_week_plan(
            profile=profile,
            workout_count_last_30d=len(last_30d),
            days_per_week=request.days_per_week,
            week_start=request.week_start,
        )

    def live_adjust_workout(self, request: LiveAdjustWorkoutRequest) -> WorkoutAdjustment:
        self._get_profile_or_default(request.user_id)
        safety = self.safety_agent.evaluate(request.feedback)
        return self.workout_agent.adjust_live_session(session=request.session, safety=safety)

    def create_meal_plan(self, request: CreateMealPlanRequest) -> MealPlanWeek:
        profile = self._get_profile_or_default(request.user_id)
        merged_exclusions = list(set(request.excluded_foods + profile.food_allergies))
        return self.nutrition_agent.create_meal_plan(
            profile=profile,
            days=request.days,
            meals_per_day=request.meals_per_day,
            excluded_foods=merged_exclusions,
        )

    def substitute_meal(self, request: SubstituteMealRequest) -> MealPlanWeek:
        self._get_profile_or_default(request.user_id)
        return self.nutrition_agent.substitute_food(
            meal_plan=request.meal_plan,
            unwanted_food=request.unwanted_food,
        )

    def ask(self, request: AskCoachRequest) -> AskCoachResponse:
        self._get_profile_or_default(request.user_id)
        if request.domain == "knowledge":
            answer, notes = self.knowledge_agent.answer(request.question)
            return AskCoachResponse(answer=answer, supporting_notes=notes)
        if request.domain == "nutrition":
            answer = "Use your meal plan target and distribute protein over 3-5 meals."
            return AskCoachResponse(answer=answer, supporting_notes=["Personalized meal planning endpoint: /v1/nutrition/plan"])
        answer = "Use RPE, pain, and fatigue to auto-adjust load and volume session by session."
        return AskCoachResponse(answer=answer, supporting_notes=["Live workout endpoint: /v1/workouts/live-adjust"])

    def add_biometric(self, request: AddBiometricRequest) -> IngestResponse:
        self._get_profile_or_default(request.entry.user_id)
        self.repository.add_biometric(request.entry)
        return IngestResponse(status="ok", message="Biometric entry stored.")

    def add_workout_log(self, request: AddWorkoutLogRequest) -> IngestResponse:
        self._get_profile_or_default(request.entry.user_id)
        self.repository.add_workout_log(request.entry)
        return IngestResponse(status="ok", message="Workout log stored.")

    def add_nutrition_log(self, request: AddNutritionLogRequest) -> IngestResponse:
        self._get_profile_or_default(request.entry.user_id)
        self.repository.add_nutrition_log(request.entry)
        return IngestResponse(status="ok", message="Nutrition log stored.")

    def add_knowledge_snippet(self, request: AddKnowledgeSnippetRequest) -> IngestResponse:
        self.repository.add_knowledge_snippet(request.snippet)
        return IngestResponse(status="ok", message="Knowledge snippet ingested.")

    def _get_profile_or_default(self, user_id: str):
        profile = self.repository.get_profile(user_id)
        if profile is None:
            profile_request = self._default_profile_request(user_id)
            profile = self.repository.upsert_profile(profile_request.profile)
            self.repository.seed_demo_data(user_id)
        return profile

    def _default_profile_request(self, user_id: str) -> UpsertProfileRequest:
        from app.models.domain import UserProfile

        return UpsertProfileRequest(
            profile=UserProfile(
                user_id=user_id,
                goal="health",
                equipment=["bodyweight", "dumbbells"],
                food_preferences=["balanced"],
            )
        )
