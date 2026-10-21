from engine.decision_engine import Reason, judge_food
from engine.i18n import render_reason
from engine.profile import UserProfile

PEANUT_SNACK = {
    "id": "x1", "name": "Peanut Noodles", "category": "carb",
    "calories": 380, "protein_g": 12, "carbs_g": 50, "fat_g": 14, "fiber_g": 3, "sugar_g": 8, "sodium_mg": 480,
    "vitamin_tags": [], "allergens": ["peanuts", "wheat"],
}


def test_render_reason_covers_both_languages_for_every_code():
    reasons = [
        Reason("allergy", {"allergens": ["peanuts"]}),
        Reason("custom_ingredient", {"ingredients": ["mango"]}),
        Reason("hard_condition", {"conditions": ["celiac"]}),
        Reason("soft_condition", {"condition": "diabetes", "nutrient": "sugar_g", "value": 20, "max": 15}),
        Reason("goal_calories", {"value": 450}),
        Reason("goal_sugar", {"value": 20}),
        Reason("ok"),
    ]
    for reason in reasons:
        for lang in ["en", "zh"]:
            text = render_reason(reason, lang)
            assert isinstance(text, str) and text


def test_allergy_reason_renders_allergen_name_in_both_languages():
    profile = UserProfile(goal="balanced", allergens={"peanuts"})
    verdict = judge_food(PEANUT_SNACK, profile)
    assert "Peanuts" in render_reason(verdict.reasons[0], "en")
    assert "花生" in render_reason(verdict.reasons[0], "zh")
