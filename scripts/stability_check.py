"""Basic stability soak check for fit-agents-v1.

Run:
  python scripts/stability_check.py
"""

from fastapi.testclient import TestClient

from app.main import app


def run_stability_check(loops: int = 200) -> tuple[int, list[tuple]]:
    client = TestClient(app)
    user_id = "stability-user"

    seed_response = client.post(
        "/v1/profile",
        json={
            "profile": {
                "user_id": user_id,
                "goal": "strength",
                "equipment": ["barbell", "dumbbells"],
                "food_allergies": ["peanuts"],
            }
        },
    )
    if seed_response.status_code != 200:
        return loops, [("seed_profile", seed_response.status_code, seed_response.text[:200])]

    failures: list[tuple] = []

    for i in range(1, loops + 1):
        r = client.post("/v1/workouts/plan", json={"user_id": user_id, "days_per_week": 4})
        if r.status_code != 200:
            failures.append((i, "workouts/plan", r.status_code))
            continue
        if len(r.json().get("days", [])) != 4:
            failures.append((i, "workouts/plan_days_invariant"))

        r = client.post(
            "/v1/workouts/live-adjust",
            json={
                "user_id": user_id,
                "session": {
                    "exercise_name": "Deadlift",
                    "sets": 3,
                    "reps": 3,
                    "load_kg": 140,
                    "rest_seconds": 210,
                },
                "feedback": {
                    "rpe_1_to_10": 8,
                    "fatigue_1_to_10": 7,
                    "pain_1_to_10": 9,
                    "mood_1_to_10": 5,
                },
            },
        )
        if r.status_code != 200:
            failures.append((i, "workouts/live-adjust", r.status_code))
        else:
            body = r.json()
            if body.get("safety", {}).get("level") != "stop" or body.get("session", {}).get("sets") != 0:
                failures.append((i, "workouts/live-adjust_stop_invariant"))

        plan_resp = client.post("/v1/nutrition/plan", json={"user_id": user_id, "days": 2, "meals_per_day": 4})
        if plan_resp.status_code != 200:
            failures.append((i, "nutrition/plan", plan_resp.status_code))
            continue

        sub_resp = client.post(
            "/v1/nutrition/substitute",
            json={"user_id": user_id, "meal_plan": plan_resp.json(), "unwanted_food": "chicken"},
        )
        if sub_resp.status_code != 200:
            failures.append((i, "nutrition/substitute", sub_resp.status_code))
        else:
            flat = " ".join(
                item["name"].lower()
                for day in sub_resp.json().get("days", [])
                for meal in day.get("meals", [])
                for item in meal.get("items", [])
            )
            if "chicken" in flat:
                failures.append((i, "nutrition/substitute_invariant"))

        for path, payload in [
            ("/v1/data/biometrics", {"entry": {"user_id": user_id, "when": "2026-02-17", "weight_kg": 79.5}}),
            (
                "/v1/data/workouts/log",
                {"entry": {"user_id": user_id, "when": "2026-02-17", "exercise_name": "Bench Press", "sets": 3, "reps": 5}},
            ),
            ("/v1/data/nutrition/log", {"entry": {"user_id": user_id, "when": "2026-02-17", "calories": 2300}}),
            (
                "/v1/knowledge/snippets",
                {"snippet": {"source": "paper", "topic": "recovery", "note": f"Iteration {i}"}},
            ),
        ]:
            ing = client.post(path, json=payload)
            if ing.status_code != 200:
                failures.append((i, path, ing.status_code))

        ask = client.post("/v1/coach/ask", json={"user_id": user_id, "question": "protein", "domain": "knowledge"})
        if ask.status_code != 200:
            failures.append((i, "coach/ask", ask.status_code))

    return loops, failures


if __name__ == "__main__":
    loops_count, found_failures = run_stability_check()
    print(f"loops={loops_count}")
    print(f"failures={len(found_failures)}")
    if found_failures:
        print(f"first_failure={found_failures[0]}")
    else:
        print("first_failure=None")
