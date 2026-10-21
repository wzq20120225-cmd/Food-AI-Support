from engine.decision_engine import VERDICT_AVOID, VERDICT_CAUTION, VERDICT_OK, judge_food, recommend_combo
from engine.profile import UserProfile

PEANUT_SNACK = {
    "id": "x1", "name": "Peanut Noodles", "category": "carb",
    "calories": 380, "protein_g": 12, "carbs_g": 50, "fat_g": 14, "fiber_g": 3, "sugar_g": 8, "sodium_mg": 480,
    "vitamin_tags": [], "allergens": ["peanuts", "wheat"],
}
HEALTHY_CHICKEN = {
    "id": "x2", "name": "Grilled Chicken Breast", "category": "protein",
    "calories": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6, "fiber_g": 0, "sugar_g": 0, "sodium_mg": 74,
    "vitamin_tags": ["potassium"], "allergens": [],
}
SUGARY_COOKIE = {
    "id": "x3", "name": "Chocolate Chip Cookie", "category": "dessert",
    "calories": 220, "protein_g": 2, "carbs_g": 30, "fat_g": 11, "fiber_g": 1, "sugar_g": 20, "sodium_mg": 150,
    "vitamin_tags": [], "allergens": ["wheat", "eggs", "milk"],
}


def test_allergy_blocks_regardless_of_other_merits():
    profile = UserProfile(goal="muscle_gain", allergens={"peanuts"})
    # High protein, fits the muscle-gain goal well — but must still be blocked.
    verdict = judge_food(PEANUT_SNACK, profile)
    assert verdict.level == VERDICT_AVOID
    assert any(r.code == "allergy" and "peanuts" in r.params["allergens"] for r in verdict.reasons)


def test_safe_food_with_no_restrictions_is_ok():
    profile = UserProfile(goal="balanced")
    verdict = judge_food(HEALTHY_CHICKEN, profile)
    assert verdict.level == VERDICT_OK


def test_diabetes_flags_high_sugar_as_caution_not_hard_block():
    profile = UserProfile(goal="balanced", conditions={"diabetes"})
    verdict = judge_food(SUGARY_COOKIE, profile)
    assert verdict.level == VERDICT_CAUTION


def test_celiac_hard_blocks_wheat_even_without_listed_allergy():
    profile = UserProfile(goal="balanced", conditions={"celiac"})
    verdict = judge_food(SUGARY_COOKIE, profile)
    assert verdict.level == VERDICT_AVOID


def test_custom_free_text_restriction_blocks_by_name_match():
    profile = UserProfile(goal="balanced", custom_avoid_ingredients=["cookie"])
    verdict = judge_food(SUGARY_COOKIE, profile)
    assert verdict.level == VERDICT_AVOID
    assert any(r.code == "custom_ingredient" and "cookie" in r.params["ingredients"] for r in verdict.reasons)


def test_recommend_combo_never_includes_an_allergen():
    profile = UserProfile(goal="muscle_gain", allergens={"peanuts"})
    foods = [PEANUT_SNACK, HEALTHY_CHICKEN]
    combo = recommend_combo(foods, profile, calorie_budget=700)
    picked_ids = {f["id"] for f in combo["items"]}
    assert "x1" not in picked_ids
    assert "x2" in picked_ids


def test_recommend_combo_respects_exclude_ids_for_shuffle():
    profile = UserProfile(goal="balanced")
    foods = [HEALTHY_CHICKEN]
    combo = recommend_combo(foods, profile, calorie_budget=700, exclude_ids={"x2"})
    assert combo["items"] == []
