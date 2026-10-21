"""User health profile: goals, allergies, and medical dietary restrictions."""
import json
from dataclasses import dataclass, field

# FDA's 9 legally recognized major food allergens (FASTER Act, 2021).
FDA_ALLERGENS = [
    "milk", "eggs", "fish", "shellfish", "tree_nuts",
    "peanuts", "wheat", "soybeans", "sesame",
]

ALLERGEN_LABELS = {
    "milk": {"en": "Milk", "zh": "奶制品"},
    "eggs": {"en": "Eggs", "zh": "蛋类"},
    "fish": {"en": "Fish", "zh": "鱼类"},
    "shellfish": {"en": "Shellfish", "zh": "贝类/甲壳类"},
    "tree_nuts": {"en": "Tree Nuts", "zh": "坚果"},
    "peanuts": {"en": "Peanuts", "zh": "花生"},
    "wheat": {"en": "Wheat", "zh": "小麦"},
    "soybeans": {"en": "Soybeans", "zh": "大豆"},
    "sesame": {"en": "Sesame", "zh": "芝麻"},
}

# Common dietary-relevant conditions and the nutrient limit each implies.
# These are soft limits (produce a caution, not a hard block) except where noted.
CONDITIONS = {
    "diabetes": {
        "label": {"en": "Diabetes", "zh": "糖尿病"},
        "limit": "sugar_g", "max": 15, "hard_block": False,
    },
    "hypertension": {
        "label": {"en": "Hypertension", "zh": "高血压"},
        "limit": "sodium_mg", "max": 300, "hard_block": False,
    },
    "high_cholesterol": {
        "label": {"en": "High Cholesterol", "zh": "高胆固醇"},
        "limit": "fat_g", "max": 15, "hard_block": False,
    },
    "lactose_intolerance": {
        "label": {"en": "Lactose Intolerance", "zh": "乳糖不耐受"},
        "limit": "allergen:milk", "max": None, "hard_block": True,
    },
    "celiac": {
        "label": {"en": "Celiac Disease / Gluten Intolerance", "zh": "麸质不耐受/乳糜泻"},
        "limit": "allergen:wheat", "max": None, "hard_block": True,
    },
}

GOALS = ["weight_loss", "muscle_gain", "vitamin_boost", "balanced"]
VITAMIN_FOCUS_OPTIONS = ["vitamin_c", "vitamin_a", "iron", "calcium"]


@dataclass
class UserProfile:
    goal: str = "balanced"
    vitamin_focus: str | None = None
    allergens: set[str] = field(default_factory=set)
    conditions: set[str] = field(default_factory=set)
    custom_note_raw: str = ""
    custom_allergens: set[str] = field(default_factory=set)
    custom_avoid_ingredients: list[str] = field(default_factory=list)

    def all_allergens(self) -> set[str]:
        return self.allergens | self.custom_allergens


CUSTOM_RESTRICTION_PROMPT = """You are a dietary-safety parser. The user describes a food allergy or medical \
dietary restriction in their own words (possibly in Chinese or English). Map it onto this fixed vocabulary \
where possible:

FDA allergens: {allergens}

Return ONLY a JSON object, no prose, in this exact shape:
{{
  "matched_allergens": ["<subset of the FDA allergens list above that apply>"],
  "avoid_ingredients": ["<English ingredient/keyword to avoid, for anything not in the fixed list>"]
}}

User's description: "{text}"
"""


def parse_custom_restriction(text: str, client=None) -> dict:
    """Turn a free-text restriction (e.g. '我对芒果过敏') into structured rules.

    Requires an Anthropic client (see engine/vision.py for how one is built).
    Falls back to an empty result if no client/API key is available, so the
    rest of the app keeps working without AI configured.
    """
    text = text.strip()
    if not text or client is None:
        return {"matched_allergens": [], "avoid_ingredients": []}

    prompt = CUSTOM_RESTRICTION_PROMPT.format(allergens=", ".join(FDA_ALLERGENS), text=text)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    # Models occasionally wrap JSON in a code fence despite instructions; strip it defensively.
    if raw.startswith("```"):
        raw = raw.strip("`").split("\n", 1)[-1]
    parsed = json.loads(raw)
    return {
        "matched_allergens": [a for a in parsed.get("matched_allergens", []) if a in FDA_ALLERGENS],
        "avoid_ingredients": parsed.get("avoid_ingredients", []),
    }
