"""All user-facing copy, in English and Chinese. English is the default.

Decision-engine code never produces display strings directly — it returns
Reason objects keyed by a code + raw params (see decision_engine.py), and
`render_reason` below is the only place that turns those into localized text.
That keeps the judgment logic (and its tests) language-independent.
"""

LANG_OPTIONS = ["English", "中文"]
DEFAULT_LANG_OPTION = "English"


def lang_code(option: str) -> str:
    return "zh" if option == "中文" else "en"


STRINGS = {
    "app_title": {"en": "NutriPlate", "zh": "NutriPlate"},
    "app_tagline": {
        "en": "Scan any food or browse today's menu — matched to your goals, allergies, and health needs.",
        "zh": "拍照识别任意食物，或浏览今日菜单 —— 结合你的目标、过敏原和健康状况给出建议。",
    },
    "sidebar_header": {"en": "Your Health Profile", "zh": "我的健康档案"},
    "goal_label": {"en": "Dietary goal", "zh": "饮食目标"},
    "vitamin_focus_label": {"en": "Which vitamin/mineral do you want more of?", "zh": "想补充哪种维生素/矿物质？"},
    "allergens_header": {"en": "Allergies (FDA's 9 major allergens)", "zh": "过敏原（FDA 九大法定过敏原）"},
    "allergens_select_label": {"en": "Select what you're allergic to", "zh": "勾选你过敏的项目"},
    "select_placeholder": {"en": "Choose options", "zh": "请选择"},
    "custom_allergy_label": {
        "en": "Other allergy — describe it in words", "zh": "其他过敏——用文字描述",
    },
    "custom_allergy_placeholder": {"en": "e.g. I'm allergic to mango", "zh": "例如：我对芒果过敏"},
    "conditions_header": {"en": "Conditions / dietary restrictions", "zh": "慢性病 / 饮食限制"},
    "conditions_select_label": {"en": "Select what applies", "zh": "勾选符合的情况"},
    "custom_condition_label": {
        "en": "Other condition — describe it in words", "zh": "其他情况——用文字描述",
    },
    "custom_condition_placeholder": {
        "en": "e.g. my doctor told me to limit high-purine foods", "zh": "例如：医生让我少吃嘌呤高的食物",
    },
    "ai_parsing_status": {"en": "AI is reading your description…", "zh": "AI 正在解析你的描述…"},
    "ai_parsed_caption": {
        "en": "Detected — allergens: {allergens} · ingredients to avoid: {ingredients}",
        "zh": "已识别——过敏原：{allergens} · 需避开的成分：{ingredients}",
    },
    "ai_not_configured_caption": {
        "en": "AI isn't configured (no ANTHROPIC_API_KEY) — matching your words directly against food names for now.",
        "zh": "未配置 AI（ANTHROPIC_API_KEY）——暂时按关键词直接匹配菜品名称。",
    },
    "none_placeholder": {"en": "none", "zh": "无"},
    "tab_photo": {"en": "Scan food", "zh": "拍照识别"},
    "tab_menu": {"en": "Today's menu", "zh": "菜单浏览"},
    "photo_caption": {
        "en": "Point your camera at any food, or upload a photo — we'll identify it and check it against your profile.",
        "zh": "对着任意食物拍照，或上传图片——我们会识别食物并结合你的健康档案给出判断。",
    },
    "demo_mode_info": {
        "en": "No ANTHROPIC_API_KEY configured yet, so this shows a demo result so you can see the full flow. "
              "Add a key to turn on real recognition.",
        "zh": "当前未配置 ANTHROPIC_API_KEY，下方会显示演示用的示例识别结果，接好 API key 后自动切换为真实识别。",
    },
    "camera_label": {"en": "Take a photo", "zh": "拍照"},
    "upload_label": {"en": "…or upload an image", "zh": "或上传图片"},
    "analyzing_spinner": {"en": "Identifying your food…", "zh": "AI 正在识别食物…"},
    "demo_result_prefix": {"en": "Demo result:", "zh": "演示结果："},
    "real_result_prefix": {"en": "Identified:", "zh": "识别结果："},
    "calories_label": {"en": "Calories", "zh": "热量"},
    "calories_metric_label": {"en": "Calories (kcal)", "zh": "热量 (kcal)"},
    "nutrition_chart_title": {"en": "Nutrition (grams)", "zh": "营养成分（克）"},
    "serving_size_label": {"en": "Does the portion look right? Adjust if needed", "zh": "份量估算是否准确？可手动调整"},
    "serving_small": {"en": "Small", "zh": "小"},
    "serving_medium": {"en": "Medium (AI estimate)", "zh": "中（AI估算）"},
    "serving_large": {"en": "Large", "zh": "大"},
    "adjusted_calorie_caption": {
        "en": "At \"{serving}\" portion size, that's about {calories} kcal (estimate).",
        "zh": "按「{serving}」份量调整后，热量约为 {calories} kcal（估算值）。",
    },
    "meal_label": {"en": "Meal", "zh": "选择餐段"},
    "meal_breakfast": {"en": "Breakfast", "zh": "早餐"},
    "meal_lunch": {"en": "Lunch", "zh": "午餐"},
    "meal_dinner": {"en": "Dinner", "zh": "晚餐"},
    "menu_today_header": {"en": "Today's menu", "zh": "今天的菜单"},
    "combo_header": {"en": "Recommended for your goal", "zh": "根据你的目标自动搭配"},
    "budget_label": {"en": "Calorie budget per meal (kcal)", "zh": "单餐热量预算 (kcal)"},
    "shuffle_button": {"en": "New combo", "zh": "换一个搭配"},
    "combo_empty_warning": {
        "en": "No combo fits your current budget and restrictions. Try raising the budget, "
              "or press shuffle to reset.",
        "zh": "在当前预算和限制下找不到合适的搭配，试着调高预算或点「换一个搭配」重置。",
    },
    "combo_totals_label": {"en": "Combo total", "zh": "搭配合计"},
    "verdict_avoid": {"en": "Avoid", "zh": "不能吃"},
    "verdict_caution": {"en": "Use caution", "zh": "不建议吃"},
    "verdict_ok": {"en": "Good to eat", "zh": "可以吃"},
    "goal_weight_loss": {"en": "Weight loss", "zh": "减脂"},
    "goal_muscle_gain": {"en": "Muscle gain", "zh": "增肌"},
    "goal_vitamin_boost": {"en": "Vitamin boost", "zh": "补维生素"},
    "goal_balanced": {"en": "Balanced", "zh": "均衡饮食"},
    "goal_reason_weight_loss": {
        "en": "High protein & fiber, low calorie density — fits weight loss",
        "zh": "高蛋白、高纤维、热量密度低，适合减脂",
    },
    "goal_reason_muscle_gain": {"en": "High protein — fits muscle gain", "zh": "高蛋白，适合增肌"},
    "goal_reason_vitamin_boost": {"en": "Rich in {vitamin}", "zh": "富含{vitamin}"},
    "goal_reason_balanced": {"en": "Well-balanced nutrition", "zh": "营养搭配均衡"},
}

VITAMIN_NAMES = {
    "vitamin_c": {"en": "Vitamin C", "zh": "维生素C"},
    "vitamin_a": {"en": "Vitamin A", "zh": "维生素A"},
    "iron": {"en": "Iron", "zh": "铁"},
    "calcium": {"en": "Calcium", "zh": "钙"},
}

NUTRIENT_DISPLAY_NAMES = {
    "protein_g": {"en": "Protein", "zh": "蛋白质"},
    "carbs_g": {"en": "Carbs", "zh": "碳水"},
    "fat_g": {"en": "Fat", "zh": "脂肪"},
    "sugar_g": {"en": "Sugar", "zh": "糖"},
    "sodium_mg": {"en": "Sodium", "zh": "钠"},
}

REASON_TEMPLATES = {
    "allergy": {
        "en": "Contains allergen(s): {items}",
        "zh": "含过敏原：{items}",
    },
    "custom_ingredient": {
        "en": "Contains an ingredient you flagged to avoid: {items}",
        "zh": "包含你标注要避开的成分：{items}",
    },
    "hard_condition": {
        "en": "Not safe for your condition ({items})",
        "zh": "你的情况（{items}）不能吃这个",
    },
    "soft_condition": {
        "en": "{condition}: {nutrient} is {value}, above your limit of {max}",
        "zh": "{condition}：{nutrient} 为 {value}，超过建议上限 {max}",
    },
    "goal_calories": {
        "en": "Calories are high ({value} kcal) for your weight-loss goal",
        "zh": "热量较高（{value} kcal），与你的减脂目标不太匹配",
    },
    "goal_sugar": {
        "en": "Sugar is high ({value}g) for your weight-loss goal",
        "zh": "含糖量较高（{value}g），与你的减脂目标不太匹配",
    },
    "ok": {
        "en": "Fits your goals and health profile",
        "zh": "符合你的目标和健康情况",
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    text = STRINGS[key][lang]
    return text.format(**kwargs) if kwargs else text


def vitamin_name(key: str, lang: str) -> str:
    return VITAMIN_NAMES[key][lang]


def nutrient_name(key: str, lang: str) -> str:
    return NUTRIENT_DISPLAY_NAMES.get(key, {}).get(lang, key)


def render_reason(reason, lang: str) -> str:
    """Turn a Reason(code, params) from the decision engine into display text."""
    from engine.profile import ALLERGEN_LABELS, CONDITIONS

    p = reason.params
    if reason.code == "allergy":
        items = ", ".join(ALLERGEN_LABELS[a][lang] for a in p["allergens"])
        return REASON_TEMPLATES["allergy"][lang].format(items=items)
    if reason.code == "custom_ingredient":
        items = ", ".join(p["ingredients"])
        return REASON_TEMPLATES["custom_ingredient"][lang].format(items=items)
    if reason.code == "hard_condition":
        items = ", ".join(CONDITIONS[c]["label"][lang] for c in p["conditions"])
        return REASON_TEMPLATES["hard_condition"][lang].format(items=items)
    if reason.code == "soft_condition":
        return REASON_TEMPLATES["soft_condition"][lang].format(
            condition=CONDITIONS[p["condition"]]["label"][lang],
            nutrient=nutrient_name(p["nutrient"], lang),
            value=p["value"],
            max=p["max"],
        )
    if reason.code == "goal_calories":
        return REASON_TEMPLATES["goal_calories"][lang].format(value=p["value"])
    if reason.code == "goal_sugar":
        return REASON_TEMPLATES["goal_sugar"][lang].format(value=p["value"])
    return REASON_TEMPLATES["ok"][lang]
