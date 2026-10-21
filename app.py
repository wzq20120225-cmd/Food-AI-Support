"""NutriPlate — personalized nutrition assistant.

Two entry points (photo recognition, menu browsing) share one decision
engine (engine/decision_engine.py) and one copy deck (engine/i18n.py), so
the judgment logic and the translations each live in exactly one place.

Styling is handled entirely by .streamlit/config.toml and native Streamlit
components (st.badge, st.pills, Material Symbols) — no injected CSS.
"""
import json

import streamlit as st

from engine import i18n, theme, vision
from engine.decision_engine import judge_food, recommend_combo
from engine.i18n import nutrient_name, t, vitamin_name
from engine.profile import (
    ALLERGEN_LABELS, CONDITIONS, FDA_ALLERGENS, GOALS, UserProfile,
    VITAMIN_FOCUS_OPTIONS, parse_custom_restriction,
)
from engine.theme import GOAL_ICON, NUTRIENT_ICON

st.set_page_config(page_title="NutriPlate", page_icon=":material/nutrition:", layout="centered")

MEAL_KEYS = ["breakfast", "lunch", "dinner"]
SERVING_KEYS = ["small", "medium", "large"]
GOAL_REASON_KEY = {
    "weight_loss": "goal_reason_weight_loss",
    "muscle_gain": "goal_reason_muscle_gain",
    "vitamin_boost": "goal_reason_vitamin_boost",
    "balanced": "goal_reason_balanced",
}


@st.cache_data
def load_menu() -> dict:
    with open("data/menu.json", encoding="utf-8") as f:
        return json.load(f)


def header_row() -> str:
    with st.container(horizontal=True, vertical_alignment="center"):
        st.title(t("app_title", "en"), icon=":material/nutrition:")
        st.space("stretch")
        option = st.segmented_control(
            "Language", i18n.LANG_OPTIONS, default=i18n.DEFAULT_LANG_OPTION,
            required=True, key="lang_option", label_visibility="collapsed",
        )
    lang = i18n.lang_code(option)
    st.caption(t("app_tagline", lang))
    return lang


def profile_sidebar(lang: str) -> UserProfile:
    st.sidebar.header(t("sidebar_header", lang), icon=":material/person:")

    goal = st.sidebar.segmented_control(
        t("goal_label", lang), GOALS, default=GOALS[0], required=True,
        format_func=lambda g: f"{GOAL_ICON[g]} {t(f'goal_{g}', lang)}", key="goal",
    )
    vitamin_focus = None
    if goal == "vitamin_boost":
        vitamin_focus = st.sidebar.segmented_control(
            t("vitamin_focus_label", lang), VITAMIN_FOCUS_OPTIONS, default=VITAMIN_FOCUS_OPTIONS[0],
            required=True, format_func=lambda v: vitamin_name(v, lang), key="vitamin_focus",
        )

    with st.sidebar.container(border=True):
        st.subheader(t("allergens_header", lang), icon=":material/allergy:")
        allergens = set(st.pills(
            t("allergens_select_label", lang), FDA_ALLERGENS, selection_mode="multi", wrap=True,
            format_func=lambda a: ALLERGEN_LABELS[a][lang], key="allergens", label_visibility="collapsed",
        ) or [])
        custom_allergy_text = st.text_input(
            t("custom_allergy_label", lang), placeholder=t("custom_allergy_placeholder", lang),
            key="custom_allergy_text",
        )

    with st.sidebar.container(border=True):
        st.subheader(t("conditions_header", lang), icon=":material/health_and_safety:")
        conditions = set(st.pills(
            t("conditions_select_label", lang), list(CONDITIONS.keys()), selection_mode="multi", wrap=True,
            format_func=lambda c: CONDITIONS[c]["label"][lang], key="conditions", label_visibility="collapsed",
        ) or [])
        custom_condition_text = st.text_input(
            t("custom_condition_label", lang), placeholder=t("custom_condition_placeholder", lang),
            key="custom_condition_text",
        )

    profile = UserProfile(goal=goal, vitamin_focus=vitamin_focus, allergens=allergens, conditions=conditions)

    custom_text = " ".join(x for x in [custom_allergy_text, custom_condition_text] if x).strip()
    profile.custom_note_raw = custom_text
    if custom_text:
        if vision.is_configured():
            with st.sidebar.status(t("ai_parsing_status", lang), expanded=False):
                client = vision.get_client()
                parsed = parse_custom_restriction(custom_text, client=client)
            profile.custom_allergens = set(parsed["matched_allergens"])
            profile.custom_avoid_ingredients = parsed["avoid_ingredients"]
            if profile.custom_allergens or profile.custom_avoid_ingredients:
                allergen_labels = [ALLERGEN_LABELS[a][lang] for a in profile.custom_allergens]
                st.sidebar.caption(t(
                    "ai_parsed_caption", lang,
                    allergens=", ".join(allergen_labels) or t("none_placeholder", lang),
                    ingredients=", ".join(profile.custom_avoid_ingredients) or t("none_placeholder", lang),
                ))
        else:
            st.sidebar.caption(t("ai_not_configured_caption", lang))
            profile.custom_avoid_ingredients = custom_text.split()

    return profile


def photo_tab(profile: UserProfile, lang: str):
    st.caption(t("photo_caption", lang))

    if not vision.is_configured():
        st.info(t("demo_mode_info", lang), icon=":material/science:")

    image = (
        st.camera_input(t("camera_label", lang), key="camera_input")
        or st.file_uploader(t("upload_label", lang), type=["jpg", "jpeg", "png"], key="file_uploader")
    )
    if not image:
        return

    with st.spinner(t("analyzing_spinner", lang)):
        food = vision.analyze_food_image(image.getvalue())

    if food.get("_demo_mode"):
        st.warning(food["name"], icon=":material/science:", title=t("demo_result_prefix", lang))
    else:
        st.success(food["name"], icon=":material/check_circle:", title=t("real_result_prefix", lang))

    col1, col2 = st.columns([1, 1.4])
    with col1:
        st.metric(t("calories_metric_label", lang), food["calories"], icon=NUTRIENT_ICON["calories"], border=True)
        verdict = judge_food(food, profile)
        st.badge(**theme.badge_kwargs(verdict.level, lang))
        for reason in verdict.reasons:
            st.caption(i18n.render_reason(reason, lang))
    with col2:
        st.altair_chart(theme.nutrition_chart(food, lang), width="stretch")

    serving = st.segmented_control(
        t("serving_size_label", lang), SERVING_KEYS, default="medium", required=True,
        format_func=lambda s: t(f"serving_{s}", lang), key="serving_size",
    )
    if serving != "medium":
        multiplier = 0.7 if serving == "small" else 1.4
        st.caption(t(
            "adjusted_calorie_caption", lang,
            serving=t(f"serving_{serving}", lang), calories=round(food["calories"] * multiplier),
        ))


def food_card(food: dict, profile: UserProfile, lang: str):
    verdict = judge_food(food, profile)
    with st.container(border=True):
        with st.container(horizontal=True, vertical_alignment="center"):
            st.markdown(f"**{food['name']}**")
            st.space("stretch")
            st.badge(**theme.badge_kwargs(verdict.level, lang))
        st.caption(f"{food['calories']} kcal")
        with st.expander(t("nutrition_chart_title", lang), icon=":material/bar_chart:"):
            for reason in verdict.reasons:
                st.caption(i18n.render_reason(reason, lang))
            st.altair_chart(theme.nutrition_chart(food, lang), width="stretch")


def menu_tab(profile: UserProfile, lang: str):
    menu = load_menu()
    meal = st.segmented_control(
        t("meal_label", lang), MEAL_KEYS, default="breakfast", required=True,
        format_func=lambda m: t(f"meal_{m}", lang), key="meal",
    )
    items = menu[meal]

    # The recommended combo is the app's actual value proposition — show it
    # before the raw menu list, not after it. A scanned tool should lead with
    # its answer, not make the user scroll past every item to find it.
    st.subheader(t("combo_header", lang), icon=":material/auto_awesome:")
    col_budget, col_shuffle = st.columns([3, 1], vertical_alignment="bottom")
    with col_budget:
        budget = st.slider(t("budget_label", lang), 300, 900, 600, step=50, key="calorie_budget")

    exclude_ids = set(st.session_state.get("excluded_ids", set()))
    with col_shuffle:
        if st.button(t("shuffle_button", lang), icon=":material/shuffle:"):
            last_combo = st.session_state.get("last_combo")
            if last_combo:
                exclude_ids |= {f["id"] for f in last_combo["items"]}
                st.session_state["excluded_ids"] = exclude_ids

    combo = recommend_combo(items, profile, calorie_budget=budget, exclude_ids=exclude_ids)
    st.session_state["last_combo"] = combo

    if not combo["items"]:
        st.warning(t("combo_empty_warning", lang))
    else:
        for food in combo["items"]:
            reason_key = GOAL_REASON_KEY[profile.goal]
            reason = (
                t(reason_key, lang, vitamin=vitamin_name(profile.vitamin_focus, lang))
                if profile.goal == "vitamin_boost"
                else t(reason_key, lang)
            )
            with st.container(border=True):
                with st.container(horizontal=True, vertical_alignment="center"):
                    st.markdown(f"**{food['name']}**")
                    st.space("stretch")
                    st.markdown(f"{food['calories']} kcal")
                st.caption(reason)

        totals = combo["totals"]
        st.markdown(f"**{t('combo_totals_label', lang)}**")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(t("calories_metric_label", lang), totals["calories"], icon=NUTRIENT_ICON["calories"], border=True)
        m2.metric(nutrient_name("protein_g", lang), f"{totals['protein_g']}g", icon=NUTRIENT_ICON["protein_g"], border=True)
        m3.metric(nutrient_name("carbs_g", lang), f"{totals['carbs_g']}g", icon=NUTRIENT_ICON["carbs_g"], border=True)
        m4.metric(nutrient_name("fat_g", lang), f"{totals['fat_g']}g", icon=NUTRIENT_ICON["fat_g"], border=True)

    # Full menu is browsable detail, not the headline — collapsed by default
    # so it's available on demand without pushing the recommendation down.
    with st.expander(t("menu_today_header", lang), icon=":material/restaurant_menu:"):
        for food in items:
            food_card(food, profile, lang)


def main():
    lang = header_row()
    profile = profile_sidebar(lang)
    tab1, tab2 = st.tabs([
        f":material/photo_camera: {t('tab_photo', lang)}",
        f":material/restaurant: {t('tab_menu', lang)}",
    ])
    with tab1:
        photo_tab(profile, lang)
    with tab2:
        menu_tab(profile, lang)


if __name__ == "__main__":
    main()
