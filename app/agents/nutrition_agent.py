from app.models.domain import FoodItem, Meal, MealPlanDay, MealPlanWeek, UserProfile


class NutritionAgent:
    def create_meal_plan(
        self,
        *,
        profile: UserProfile,
        days: int,
        meals_per_day: int,
        excluded_foods: list[str] | None = None,
    ) -> MealPlanWeek:
        excluded = {f.lower() for f in (excluded_foods or [])}
        target_kcal = self._estimate_target_kcal(profile)
        meal_templates = self._meal_templates()

        day_plans: list[MealPlanDay] = []
        for day_idx in range(1, days + 1):
            meals: list[Meal] = []
            for i in range(meals_per_day):
                template = meal_templates[(day_idx + i) % len(meal_templates)]
                meals.append(self._without_excluded(template, excluded))
            day_plans.append(MealPlanDay(day_index=day_idx, target_kcal=target_kcal, meals=meals))

        rationale = (
            f"Calories set for goal={profile.goal}; allergies excluded={', '.join(profile.food_allergies) or 'none'}."
        )
        return MealPlanWeek(user_id=profile.user_id, rationale=rationale, days=day_plans)

    def substitute_food(self, *, meal_plan: MealPlanWeek, unwanted_food: str) -> MealPlanWeek:
        old = unwanted_food.lower()
        replacement_map = {
            "chicken": "turkey",
            "rice": "potatoes",
            "salmon": "tofu",
            "egg": "greek yogurt",
            "oats": "whole-grain bread",
        }
        replacement = replacement_map.get(old, "alternative protein/carb source")

        updated_days: list[MealPlanDay] = []
        for day in meal_plan.days:
            updated_meals: list[Meal] = []
            for meal in day.meals:
                updated_items = []
                for item in meal.items:
                    if old in item.name.lower():
                        updated_items.append(FoodItem(name=item.name.lower().replace(old, replacement), amount=item.amount))
                    else:
                        updated_items.append(item)
                updated_meals.append(Meal(name=meal.name, items=updated_items))
            updated_days.append(MealPlanDay(day_index=day.day_index, target_kcal=day.target_kcal, meals=updated_meals))

        return MealPlanWeek(
            user_id=meal_plan.user_id,
            rationale=f"{meal_plan.rationale} Substitution applied: {unwanted_food} -> {replacement}.",
            days=updated_days,
        )

    def _estimate_target_kcal(self, profile: UserProfile) -> int:
        if profile.goal == "fat_loss":
            return 2100
        if profile.goal == "muscle_gain":
            return 2800
        if profile.goal == "strength":
            return 2600
        if profile.goal == "recomposition":
            return 2400
        return 2300

    def _without_excluded(self, meal: Meal, excluded: set[str]) -> Meal:
        replacements = {
            "chicken breast": "turkey breast",
            "salmon": "lean beef",
            "rice": "potatoes",
            "greek yogurt": "skyr yogurt",
        }
        filtered = []
        for item in meal.items:
            if item.name.lower() in excluded:
                filtered.append(FoodItem(name=replacements.get(item.name.lower(), "seasonal alternative"), amount=item.amount))
            else:
                filtered.append(item)
        return Meal(name=meal.name, items=filtered)

    def _meal_templates(self) -> list[Meal]:
        return [
            Meal(
                name="Breakfast",
                items=[
                    FoodItem(name="oats", amount="70g"),
                    FoodItem(name="greek yogurt", amount="200g"),
                    FoodItem(name="berries", amount="100g"),
                ],
            ),
            Meal(
                name="Lunch",
                items=[
                    FoodItem(name="chicken breast", amount="170g"),
                    FoodItem(name="rice", amount="180g cooked"),
                    FoodItem(name="mixed vegetables", amount="150g"),
                ],
            ),
            Meal(
                name="Snack",
                items=[
                    FoodItem(name="whole-grain bread", amount="2 slices"),
                    FoodItem(name="peanut butter", amount="25g"),
                    FoodItem(name="banana", amount="1 medium"),
                ],
            ),
            Meal(
                name="Dinner",
                items=[
                    FoodItem(name="salmon", amount="170g"),
                    FoodItem(name="potatoes", amount="250g"),
                    FoodItem(name="salad", amount="150g"),
                ],
            ),
        ]
