from collections import defaultdict
from datetime import date

from app.models.domain import (
    BiometricEntry,
    KnowledgeSnippet,
    NutritionLogEntry,
    UserProfile,
    WorkoutLogEntry,
)


class InMemoryRepository:
    def __init__(self) -> None:
        self._profiles: dict[str, UserProfile] = {}
        self._biometrics: dict[str, list[BiometricEntry]] = defaultdict(list)
        self._workouts: dict[str, list[WorkoutLogEntry]] = defaultdict(list)
        self._nutrition: dict[str, list[NutritionLogEntry]] = defaultdict(list)
        self._knowledge: list[KnowledgeSnippet] = [
            KnowledgeSnippet(
                source="NSCA Essentials",
                topic="progressive overload",
                note="Increase training stress gradually via load, reps, sets, or density.",
            ),
            KnowledgeSnippet(
                source="Sports Nutrition Position Stand",
                topic="protein",
                note="Daily protein targets are usually distributed over multiple meals.",
            ),
            KnowledgeSnippet(
                source="ACSM Guidelines",
                topic="pain management",
                note="Sharp or escalating pain during training is a signal to stop and reassess.",
            ),
        ]

    def upsert_profile(self, profile: UserProfile) -> UserProfile:
        self._profiles[profile.user_id] = profile
        return profile

    def get_profile(self, user_id: str) -> UserProfile | None:
        return self._profiles.get(user_id)

    def add_biometric(self, entry: BiometricEntry) -> None:
        self._biometrics[entry.user_id].append(entry)

    def get_recent_biometrics(self, user_id: str, limit: int = 14) -> list[BiometricEntry]:
        return sorted(self._biometrics.get(user_id, []), key=lambda x: x.when, reverse=True)[:limit]

    def add_workout_log(self, entry: WorkoutLogEntry) -> None:
        self._workouts[entry.user_id].append(entry)

    def get_recent_workouts(self, user_id: str, limit: int = 50) -> list[WorkoutLogEntry]:
        return sorted(self._workouts.get(user_id, []), key=lambda x: x.when, reverse=True)[:limit]

    def add_nutrition_log(self, entry: NutritionLogEntry) -> None:
        self._nutrition[entry.user_id].append(entry)

    def get_recent_nutrition(self, user_id: str, limit: int = 30) -> list[NutritionLogEntry]:
        return sorted(self._nutrition.get(user_id, []), key=lambda x: x.when, reverse=True)[:limit]

    def search_knowledge(self, query: str, limit: int = 3) -> list[KnowledgeSnippet]:
        q = query.lower()
        ranked: list[KnowledgeSnippet] = []
        for snippet in self._knowledge:
            score = 0
            if q in snippet.topic.lower():
                score += 2
            if q in snippet.note.lower():
                score += 1
            if score > 0:
                ranked.append(snippet)
        if not ranked:
            ranked = self._knowledge
        return ranked[:limit]

    def add_knowledge_snippet(self, snippet: KnowledgeSnippet) -> None:
        self._knowledge.append(snippet)

    def seed_demo_data(self, user_id: str) -> None:
        self._biometrics[user_id].append(
            BiometricEntry(
                user_id=user_id,
                when=date.today(),
                weight_kg=80.0,
                resting_hr=60,
                sleep_hours=7.5,
                stress_1_to_10=4,
                soreness_1_to_10=3,
            )
        )
