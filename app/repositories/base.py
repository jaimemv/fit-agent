from typing import Protocol

from app.models.domain import (
    BiometricEntry,
    KnowledgeSnippet,
    NutritionLogEntry,
    UserProfile,
    WorkoutLogEntry,
)


class Repository(Protocol):
    def upsert_profile(self, profile: UserProfile) -> UserProfile:
        ...

    def get_profile(self, user_id: str) -> UserProfile | None:
        ...

    def add_biometric(self, entry: BiometricEntry) -> None:
        ...

    def get_recent_biometrics(self, user_id: str, limit: int = 14) -> list[BiometricEntry]:
        ...

    def add_workout_log(self, entry: WorkoutLogEntry) -> None:
        ...

    def get_recent_workouts(self, user_id: str, limit: int = 50) -> list[WorkoutLogEntry]:
        ...

    def add_nutrition_log(self, entry: NutritionLogEntry) -> None:
        ...

    def get_recent_nutrition(self, user_id: str, limit: int = 30) -> list[NutritionLogEntry]:
        ...

    def search_knowledge(self, query: str, limit: int = 3) -> list[KnowledgeSnippet]:
        ...

    def add_knowledge_snippet(self, snippet: KnowledgeSnippet) -> None:
        ...

    def seed_demo_data(self, user_id: str) -> None:
        ...
