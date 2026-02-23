from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _seed_profile(user_id: str = "demo-user") -> None:
    response = client.post(
        "/v1/profile",
        json={
            "profile": {
                "user_id": user_id,
                "goal": "strength",
                "equipment": ["barbell", "dumbbells"],
                "food_preferences": ["high protein"],
                "food_allergies": ["peanuts"],
            }
        },
    )
    assert response.status_code == 200


def test_create_workout_plan() -> None:
    _seed_profile()
    response = client.post("/v1/workouts/plan", json={"user_id": "demo-user", "days_per_week": 4})
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "demo-user"
    assert len(body["days"]) == 4


def test_live_adjust_stops_on_high_pain() -> None:
    _seed_profile("pain-user")
    response = client.post(
        "/v1/workouts/live-adjust",
        json={
            "user_id": "pain-user",
            "session": {"exercise_name": "Back squat", "sets": 4, "reps": 5, "load_kg": 100, "rest_seconds": 180},
            "feedback": {"rpe_1_to_10": 8, "fatigue_1_to_10": 7, "pain_1_to_10": 9, "mood_1_to_10": 5},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["safety"]["level"] == "stop"
    assert body["session"]["sets"] == 0


def test_substitute_chicken() -> None:
    _seed_profile("nutrition-user")
    plan_response = client.post(
        "/v1/nutrition/plan",
        json={"user_id": "nutrition-user", "days": 2, "meals_per_day": 3},
    )
    assert plan_response.status_code == 200
    meal_plan = plan_response.json()

    substitute_response = client.post(
        "/v1/nutrition/substitute",
        json={"user_id": "nutrition-user", "meal_plan": meal_plan, "unwanted_food": "chicken"},
    )
    assert substitute_response.status_code == 200
    updated = substitute_response.json()
    flattened = " ".join(
        item["name"].lower()
        for day in updated["days"]
        for meal in day["meals"]
        for item in meal["items"]
    )
    assert "chicken" not in flattened


def test_ingest_biometric_data() -> None:
    _seed_profile("bio-user")
    response = client.post(
        "/v1/data/biometrics",
        json={
            "entry": {
                "user_id": "bio-user",
                "when": "2026-02-17",
                "weight_kg": 79.4,
                "resting_hr": 58,
                "sleep_hours": 7.2,
                "stress_1_to_10": 4,
                "soreness_1_to_10": 3,
            }
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
