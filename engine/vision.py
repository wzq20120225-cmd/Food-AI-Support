"""Photo -> food identification + nutrition estimate, via the Claude API.

Design note: if no ANTHROPIC_API_KEY is configured, this falls back to a
small set of canned demo results instead of crashing. That keeps the rest of
the app (profile setup, the decision engine, the UI) fully demoable while
the real API key is being set up, and it makes the missing-key case a
normal, handled path rather than a surprise error during a live demo.
"""
import base64
import itertools
import json
import os

from dotenv import load_dotenv

load_dotenv()

VISION_PROMPT = """You are a nutrition-estimation assistant. Identify the single most \
prominent food item in this photo and estimate its nutrition for the portion shown.

Return ONLY a JSON object, no prose, in this exact shape:
{
  "name": "<food name>",
  "calories": <int>,
  "protein_g": <number>,
  "carbs_g": <number>,
  "fat_g": <number>,
  "fiber_g": <number>,
  "sugar_g": <number>,
  "sodium_mg": <number>,
  "vitamin_tags": [<subset of: "vitamin_c","vitamin_a","iron","calcium">],
  "allergens": [<subset of FDA's 9 major allergens: "milk","eggs","fish","shellfish",
                 "tree_nuts","peanuts","wheat","soybeans","sesame" — only ones visibly
                 present as ingredients>]
}
"""

_DEMO_RESULTS = itertools.cycle([
    {
        "name": "Peanut Butter Sandwich", "calories": 330, "protein_g": 12, "carbs_g": 35,
        "fat_g": 16, "fiber_g": 4, "sugar_g": 8, "sodium_mg": 380,
        "vitamin_tags": [], "allergens": ["peanuts", "wheat"],
    },
    {
        "name": "Grilled Salmon with Rice", "calories": 410, "protein_g": 28, "carbs_g": 45,
        "fat_g": 12, "fiber_g": 2, "sugar_g": 1, "sodium_mg": 150,
        "vitamin_tags": ["vitamin_a", "vitamin_d"], "allergens": ["fish"],
    },
    {
        "name": "Chocolate Chip Cookie", "calories": 220, "protein_g": 2, "carbs_g": 30,
        "fat_g": 11, "fiber_g": 1, "sugar_g": 20, "sodium_mg": 150,
        "vitamin_tags": [], "allergens": ["wheat", "eggs", "milk"],
    },
])


def is_configured() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def get_client():
    if not is_configured():
        return None
    import anthropic
    return anthropic.Anthropic()


def analyze_food_image(image_bytes: bytes, media_type: str = "image/jpeg", client=None) -> dict:
    """Returns a food dict shaped like the menu.json entries (minus id/category),
    either from the real Claude vision API or, with no key configured, a demo
    result — so the rest of the app never has to special-case "no API key"."""
    if client is None:
        client = get_client()
    if client is None:
        return next(_DEMO_RESULTS) | {"_demo_mode": True}

    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_b64}},
                {"type": "text", "text": VISION_PROMPT},
            ],
        }],
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").split("\n", 1)[-1]
    result = json.loads(raw)
    result["_demo_mode"] = False
    return result
