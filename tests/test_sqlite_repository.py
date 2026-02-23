from datetime import date

from app.models.domain import BiometricEntry, KnowledgeSnippet, UserProfile, WorkoutLogEntry
from app.repositories.sqlite import SQLiteRepository


def test_sqlite_repository_persists_profile(tmp_path) -> None:
    db_file = tmp_path / "fit_agents.db"
    repo = SQLiteRepository(str(db_file))

    profile = UserProfile(user_id="u1", goal="strength", equipment=["barbell"])
    repo.upsert_profile(profile)

    loaded = repo.get_profile("u1")
    assert loaded is not None
    assert loaded.user_id == "u1"
    assert loaded.goal == "strength"


def test_sqlite_repository_recent_entries_order(tmp_path) -> None:
    db_file = tmp_path / "fit_agents.db"
    repo = SQLiteRepository(str(db_file))

    repo.add_biometric(
        BiometricEntry(user_id="u2", when=date(2026, 2, 1), weight_kg=82.0),
    )
    repo.add_biometric(
        BiometricEntry(user_id="u2", when=date(2026, 2, 3), weight_kg=81.2),
    )
    repo.add_workout_log(
        WorkoutLogEntry(user_id="u2", when=date(2026, 2, 2), exercise_name="Squat", sets=3, reps=5),
    )

    biometrics = repo.get_recent_biometrics("u2", limit=2)
    workouts = repo.get_recent_workouts("u2", limit=1)

    assert len(biometrics) == 2
    assert biometrics[0].when == date(2026, 2, 3)
    assert workouts[0].exercise_name == "Squat"


def test_sqlite_repository_knowledge_search_and_append(tmp_path) -> None:
    db_file = tmp_path / "fit_agents.db"
    repo = SQLiteRepository(str(db_file))

    repo.add_knowledge_snippet(
        KnowledgeSnippet(
            source="Custom Paper",
            topic="creatine",
            note="Creatine can support strength and high-intensity performance.",
        )
    )

    hits = repo.search_knowledge("creatine", limit=3)
    assert len(hits) >= 1
    assert any("creatine" in h.topic.lower() or "creatine" in h.note.lower() for h in hits)
