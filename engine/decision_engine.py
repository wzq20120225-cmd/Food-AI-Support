"""Shared decision engine: judges a single food and builds goal-based combos.

Both the photo-recognition flow and the menu-browsing flow feed into this
module, so the judgment logic (and any future fix to it) lives in one place.

Reasons are returned as (code, params) pairs, never pre-formatted strings —
engine/i18n.py's render_reason() is the only place that turns them into
display text, in whichever language is active. This keeps judge_food()
language-independent and its tests readable regardless of UI language.
"""
from dataclasses import dataclass, field

from engine.profile import CONDITIONS, UserProfile

VERDICT_AVOID = "avoid"      # 🚫 allergy or medically-mandatory restriction — never overridden
VERDICT_CAUTION = "caution"  # ⚠️ exceeds a soft nutrient limit for the user's condition/goal
VERDICT_OK = "ok"            # ✅ fine to eat


@dataclass
class Reason:
    code: str
    params: dict = field(default_factory=dict)


@dataclass
class Verdict:
    level: str
    reasons: list[Reason] = field(default_factory=list)


def _matched_allergens(food: dict, profile: UserProfile) -> list[str]:
    food_allergens = set(food.get("allergens", []))
    return sorted(food_allergens & profile.all_allergens())


def _matched_custom_ingredients(food: dict, profile: UserProfile) -> list[str]:
    name = food.get("name", "").lower()
    return [kw for kw in profile.custom_avoid_ingredients if kw.lower() in name]


def _hard_blocking_conditions(food: dict, profile: UserProfile) -> list[str]:
    """Conditions where ANY amount of a restricted allergen is medically unsafe
    (e.g. celiac + wheat), as opposed to a soft nutrient-threshold caution."""
    hits = []
    for cond in profile.conditions:
        rule = CONDITIONS.get(cond)
        if not rule or not rule["hard_block"]:
            continue
        _, allergen = rule["limit"].split(":")
        if allergen in food.get("allergens", []):
            hits.append(cond)
    return hits


def _soft_condition_cautions(food: dict, profile: UserProfile) -> list[Reason]:
    reasons = []
    for cond in profile.conditions:
        rule = CONDITIONS.get(cond)
        if not rule or rule["hard_block"]:
            continue
        value = food.get(rule["limit"], 0)
        if value > rule["max"]:
            reasons.append(Reason("soft_condition", {
                "condition": cond, "nutrient": rule["limit"], "value": value, "max": rule["max"],
            }))
    return reasons


def _goal_caution(food: dict, profile: UserProfile) -> Reason | None:
    if profile.goal == "weight_loss" and food.get("calories", 0) > 400:
        return Reason("goal_calories", {"value": food["calories"]})
    if profile.goal == "weight_loss" and food.get("sugar_g", 0) > 15:
        return Reason("goal_sugar", {"value": food["sugar_g"]})
    return None


def judge_food(food: dict, profile: UserProfile) -> Verdict:
    """Judge a single food against a user's profile.

    Priority is deliberate and must not change: allergy/medical hard-block
    always wins over a nutrition-based caution, even if the food would
    otherwise score well for the user's goal. A food is never shown as safe
    just because it happens to be "healthy" on some other axis.
    """
    allergy_hits = _matched_allergens(food, profile)
    custom_hits = _matched_custom_ingredients(food, profile)
    hard_condition_hits = _hard_blocking_conditions(food, profile)

    if allergy_hits or custom_hits or hard_condition_hits:
        reasons = []
        if allergy_hits:
            reasons.append(Reason("allergy", {"allergens": allergy_hits}))
        if custom_hits:
            reasons.append(Reason("custom_ingredient", {"ingredients": custom_hits}))
        if hard_condition_hits:
            reasons.append(Reason("hard_condition", {"conditions": hard_condition_hits}))
        return Verdict(VERDICT_AVOID, reasons)

    caution_reasons = _soft_condition_cautions(food, profile)
    goal_caution = _goal_caution(food, profile)
    if goal_caution:
        caution_reasons.append(goal_caution)

    if caution_reasons:
        return Verdict(VERDICT_CAUTION, caution_reasons)

    return Verdict(VERDICT_OK, [Reason("ok")])


def score_food(food: dict, profile: UserProfile) -> float:
    """Goal-based score used only to RANK foods that already passed judge_food
    (i.e. are not VERDICT_AVOID). Higher is a better fit for the stated goal."""
    protein = food.get("protein_g", 0)
    carbs = food.get("carbs_g", 0)
    fat = food.get("fat_g", 0)
    fiber = food.get("fiber_g", 0)
    calories = food.get("calories", 0)

    if profile.goal == "weight_loss":
        return protein * 2 + fiber * 1.5 - calories * 0.05 - fat * 0.5
    if profile.goal == "muscle_gain":
        return protein * 3 + carbs * 0.5
    if profile.goal == "vitamin_boost" and profile.vitamin_focus:
        return 10 if profile.vitamin_focus in food.get("vitamin_tags", []) else 0
    # balanced: reward covering more food groups' worth of nutrients at once
    return protein + carbs * 0.3 + fiber * 2 - fat * 0.3


def recommend_combo(
    foods: list[dict], profile: UserProfile, calorie_budget: int = 700, exclude_ids: set[str] = frozenset()
) -> dict:
    """Greedily build a protein + carb + veggie (+ optional fruit) combo that
    fits the calorie budget and scores highest for the user's goal.

    Foods that judge_food marks as AVOID are filtered out before scoring —
    an unsafe food can never appear in a recommendation, regardless of score.
    `exclude_ids` lets the UI offer a "give me another combo" button.
    """
    safe_foods = [
        f for f in foods
        if judge_food(f, profile).level != VERDICT_AVOID and f.get("id") not in exclude_ids
    ]
    by_category: dict[str, list[dict]] = {}
    for f in safe_foods:
        by_category.setdefault(f.get("category", "other"), []).append(f)

    def best_in(category: str, remaining_budget: int) -> dict | None:
        candidates = [f for f in by_category.get(category, []) if f["calories"] <= remaining_budget]
        if not candidates:
            return None
        return max(candidates, key=lambda f: score_food(f, profile))

    combo = []
    budget = calorie_budget
    for category in ["protein", "carb", "veggie", "fruit"]:
        pick = best_in(category, budget)
        if pick:
            combo.append(pick)
            budget -= pick["calories"]

    total = {
        "calories": sum(f["calories"] for f in combo),
        "protein_g": sum(f["protein_g"] for f in combo),
        "carbs_g": sum(f["carbs_g"] for f in combo),
        "fat_g": sum(f["fat_g"] for f in combo),
    }
    return {"items": combo, "totals": total}
