# fit-agents-v1

V1 backend scaffold for a multi-agent personal trainer and nutritionist product.

## What this v1 includes

- FastAPI service with core endpoints.
- Agent-style modules:
  - `CoachOrchestrator`
  - `WorkoutPlannerAgent`
  - `SafetyAgent`
  - `NutritionAgent`
  - `KnowledgeAgent`
- Typed domain/request models via Pydantic.
- Pluggable repository layer: in-memory (default) or SQLite persistence.
- Starter tests for health, workout planning, live adaptation, and meal substitution.

## Project structure

```text
app/
  agents/
  api/
  core/
  models/
  repositories/
  main.py
tests/
pyproject.toml
```

## Quickstart

1. Create env and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

2. Run API:

```bash
uvicorn app.main:app --reload
```

3. Open docs:

- `http://127.0.0.1:8000/docs`

4. Run stability soak check:

```bash
python scripts/stability_check.py
```

## Storage backend

By default, the app uses in-memory storage.

- `APP_STORAGE=memory` for ephemeral local testing.
- `APP_STORAGE=sqlite` for persistent local storage.
- `SQLITE_PATH=./data/fit_agents.db` to choose the SQLite file path.

Example:

```bash
export APP_STORAGE=sqlite
export SQLITE_PATH=./data/fit_agents.db
uvicorn app.main:app --reload
```

## CI/CD

This repository now includes GitHub Actions workflows:

- CI: `/.github/workflows/ci.yml`
- Runs on every push and pull request.
- Tests on Python 3.10 and 3.12.
- Executes compile checks and `pytest`.

- CD: `/.github/workflows/cd.yml`
- Runs on pushes to `main` (and manually via `workflow_dispatch`).
- Builds Docker image from `/Dockerfile`.
- Pushes image to GHCR as `ghcr.io/<owner>/<repo>`.
- Optionally calls a deploy webhook if `DEPLOY_WEBHOOK_URL` secret is configured.

Required setup in GitHub:

- Enable GitHub Actions for the repository.
- Keep package permissions enabled for `GITHUB_TOKEN` (workflow already requests `packages: write`).
- Optional: add repository secret `DEPLOY_WEBHOOK_URL` if you want automatic deploy trigger after image publish.

## Main endpoints

- `GET /health`
- `POST /v1/profile`
- `POST /v1/workouts/plan`
- `POST /v1/workouts/live-adjust`
- `POST /v1/nutrition/plan`
- `POST /v1/nutrition/substitute`
- `POST /v1/coach/ask`
- `POST /v1/data/biometrics`
- `POST /v1/data/workouts/log`
- `POST /v1/data/nutrition/log`
- `POST /v1/knowledge/snippets`

## Example requests

Create/update profile:

```bash
curl -X POST http://127.0.0.1:8000/v1/profile \
  -H "Content-Type: application/json" \
  -d '{
    "profile": {
      "user_id": "jaime",
      "goal": "strength",
      "equipment": ["barbell", "dumbbells"],
      "food_allergies": ["peanuts"]
    }
  }'
```

Live workout adjustment:

```bash
curl -X POST http://127.0.0.1:8000/v1/workouts/live-adjust \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "jaime",
    "session": {"exercise_name": "Squat", "sets": 4, "reps": 5, "load_kg": 100, "rest_seconds": 180},
    "feedback": {"rpe_1_to_10": 9, "fatigue_1_to_10": 8, "pain_1_to_10": 6, "mood_1_to_10": 4}
  }'
```

Meal substitution:

```bash
curl -X POST http://127.0.0.1:8000/v1/nutrition/substitute \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "jaime",
    "meal_plan": {"user_id":"jaime","rationale":"demo","days":[]},
    "unwanted_food": "chicken"
  }'
```

## Next steps (v2)

- Replace in-memory repo with Postgres + `pgvector`.
- Add document ingestion pipeline for books/courses/papers and retrieval ranking.
- Track adherence and outcomes for adaptive planning.
- Add auth, user sessions, and persistent logs.
- Add mobile/web UI for in-workout interactions.
- Add camera + pose-estimation service for technique feedback.
