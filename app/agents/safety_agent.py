from app.models.domain import SafetyDecision, WorkoutFeedback


class SafetyAgent:
    """Conservative safety guardrails for in-session decisions."""

    def evaluate(self, feedback: WorkoutFeedback) -> SafetyDecision:
        reasons: list[str] = []
        recommendations: list[str] = []
        level = "ok"

        if feedback.pain_1_to_10 >= 8:
            level = "stop"
            reasons.append("Pain is severe (>=8/10).")
            recommendations.append("Stop the exercise and switch to pain-free movement.")
            recommendations.append("If pain persists, consult a qualified professional.")
            return SafetyDecision(level=level, reasons=reasons, recommendations=recommendations)

        if feedback.pain_1_to_10 >= 6:
            level = "caution"
            reasons.append("Pain is elevated (>=6/10).")
            recommendations.append("Reduce load and range of motion; reassess every set.")

        if feedback.fatigue_1_to_10 >= 8:
            if level != "stop":
                level = "caution"
            reasons.append("Fatigue is high (>=8/10).")
            recommendations.append("Reduce volume by 20-30% and extend rest intervals.")

        if feedback.rpe_1_to_10 >= 9:
            if level != "stop":
                level = "caution"
            reasons.append("Effort is near maximal (RPE >=9).")
            recommendations.append("Avoid additional hard sets on the same movement.")

        if feedback.mood_1_to_10 <= 2:
            if level != "stop":
                level = "caution"
            reasons.append("Mood/readiness is very low.")
            recommendations.append("Prioritize technique and shorter session duration.")

        if level == "ok":
            recommendations.append("Session can continue as planned.")

        return SafetyDecision(level=level, reasons=reasons, recommendations=recommendations)
