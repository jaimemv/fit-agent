from datetime import date

from app.models.domain import (
    ExercisePrescription,
    LiveWorkoutSession,
    SafetyDecision,
    UserProfile,
    WorkoutAdjustment,
    WorkoutDayPlan,
    WorkoutWeekPlan,
)


class WorkoutPlannerAgent:
    def create_week_plan(
        self,
        *,
        profile: UserProfile,
        workout_count_last_30d: int,
        days_per_week: int,
        week_start: date | None = None,
    ) -> WorkoutWeekPlan:
        week_start = week_start or date.today()
        rationale = (
            f"Goal={profile.goal}; equipment={', '.join(profile.equipment)}; "
            f"historical sessions(last30d)={workout_count_last_30d}."
        )
        split = self._build_split(profile.goal, days_per_week)
        return WorkoutWeekPlan(user_id=profile.user_id, week_start=week_start, rationale=rationale, days=split)

    def adjust_live_session(
        self,
        *,
        session: LiveWorkoutSession,
        safety: SafetyDecision,
    ) -> WorkoutAdjustment:
        adjusted = session.model_copy(deep=True)
        summary = "No changes."
        coach_message = "Continue with controlled reps and solid technique."

        if safety.level == "stop":
            adjusted.sets = 0
            summary = "Session stopped for safety."
            coach_message = "Stop this exercise now and switch to pain-free movement."
        elif safety.level == "caution":
            adjusted.sets = max(1, round(adjusted.sets * 0.7))
            adjusted.rest_seconds = int(adjusted.rest_seconds * 1.25)
            if adjusted.load_kg is not None:
                adjusted.load_kg = round(adjusted.load_kg * 0.9, 1)
            summary = "Reduced volume/load and increased rest due to fatigue/pain risk."
            coach_message = "Keep technique strict and reassess after each set."

        return WorkoutAdjustment(
            session=adjusted,
            change_summary=summary,
            coach_message=coach_message,
            safety=safety,
        )

    def _build_split(self, goal: str, days_per_week: int) -> list[WorkoutDayPlan]:
        templates = [
            ("Lower Strength", "Build lower body strength"),
            ("Upper Strength", "Build upper body strength"),
            ("Lower Hypertrophy", "Increase lower body volume"),
            ("Upper Hypertrophy", "Increase upper body volume"),
            ("Conditioning", "Improve aerobic/anaerobic conditioning"),
            ("Full Body Technique", "Groove movement quality"),
        ]
        selected = templates[:days_per_week]

        days: list[WorkoutDayPlan] = []
        for idx, (title, objective) in enumerate(selected, start=1):
            days.append(
                WorkoutDayPlan(
                    day_index=idx,
                    title=title,
                    objective=f"{objective}. Goal focus: {goal}.",
                    exercises=self._default_exercises_for_day(title),
                )
            )
        return days

    def _default_exercises_for_day(self, day_title: str) -> list[ExercisePrescription]:
        if "Lower" in day_title:
            return [
                ExercisePrescription(
                    name="Squat variation",
                    sets=4,
                    reps="5-8",
                    load_guidance="RPE 7-8",
                    rest_seconds=150,
                ),
                ExercisePrescription(
                    name="Hip hinge variation",
                    sets=3,
                    reps="6-10",
                    load_guidance="RPE 7",
                    rest_seconds=120,
                ),
                ExercisePrescription(
                    name="Split squat",
                    sets=3,
                    reps="8-12",
                    load_guidance="Moderate",
                    rest_seconds=90,
                ),
            ]
        if "Upper" in day_title:
            return [
                ExercisePrescription(
                    name="Horizontal press",
                    sets=4,
                    reps="5-8",
                    load_guidance="RPE 7-8",
                    rest_seconds=150,
                ),
                ExercisePrescription(
                    name="Horizontal row",
                    sets=4,
                    reps="6-10",
                    load_guidance="RPE 7-8",
                    rest_seconds=120,
                ),
                ExercisePrescription(
                    name="Overhead press",
                    sets=3,
                    reps="6-10",
                    load_guidance="RPE 7",
                    rest_seconds=120,
                ),
            ]
        if "Conditioning" in day_title:
            return [
                ExercisePrescription(
                    name="Bike/Rower intervals",
                    sets=8,
                    reps="30s hard / 90s easy",
                    load_guidance="Hard but repeatable",
                    rest_seconds=0,
                ),
                ExercisePrescription(
                    name="Core circuit",
                    sets=3,
                    reps="10-15 each",
                    load_guidance="Controlled tempo",
                    rest_seconds=60,
                ),
            ]
        return [
            ExercisePrescription(
                name="Movement prep + light full body circuit",
                sets=3,
                reps="8-12",
                load_guidance="Easy-moderate",
                rest_seconds=75,
            )
        ]
