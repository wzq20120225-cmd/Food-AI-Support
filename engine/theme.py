"""Design tokens and chart/icon mappings.

All page styling (colors, fonts, radii) lives in .streamlit/config.toml and
native Streamlit components (st.badge, Material Symbols, st.pills) — no
injected CSS. This module only holds the chart color system and the handful
of lookup tables that turn a verdict/goal/nutrient key into an icon.

Two color systems are kept deliberately separate and never reused for each
other's job:
  - STATUS colors (good/warning/critical) mean "can you eat this" — reserved,
    always paired with an icon + label via st.badge, never used elsewhere.
  - NUTRIENT colors (protein/carbs/fat/sugar) are a fixed categorical identity
    for the macro chart — chosen from the cool half of the palette so they
    can never be mistaken for a status color on the same screen.
"""
import altair as alt
import pandas as pd

from engine.decision_engine import VERDICT_AVOID, VERDICT_CAUTION, VERDICT_OK
from engine.i18n import nutrient_name, t

INK_PRIMARY = "#262220"
INK_MUTED = "#8A8178"
GRIDLINE = "#EDE8E1"

STATUS_BADGE = {
    VERDICT_OK: {"color": "green", "icon": ":material/check_circle:"},
    VERDICT_CAUTION: {"color": "orange", "icon": ":material/warning:"},
    VERDICT_AVOID: {"color": "red", "icon": ":material/no_food:"},
}
VERDICT_STRING_KEY = {VERDICT_OK: "verdict_ok", VERDICT_CAUTION: "verdict_caution", VERDICT_AVOID: "verdict_avoid"}

GOAL_ICON = {
    "weight_loss": ":material/trending_down:",
    "muscle_gain": ":material/fitness_center:",
    "vitamin_boost": ":material/spa:",
    "balanced": ":material/balance:",
}

NUTRIENT_ICON = {
    "calories": ":material/local_fire_department:",
    "protein_g": ":material/egg_alt:",
    "carbs_g": ":material/grain:",
    "fat_g": ":material/opacity:",
    "sugar_g": ":material/icecream:",
}

# Categorical slots 1 (blue), 2 (aqua), 5 (violet), 7 (magenta) from the
# validated dataviz palette — deliberately skipping the green/yellow/red
# slots so a macro color is never mistaken for a status color.
NUTRIENT_COLORS = {
    "protein_g": "#2a78d6",
    "carbs_g": "#1baf7a",
    "fat_g": "#4a3aa7",
    "sugar_g": "#e87ba4",
}
NUTRIENT_KEYS = ["protein_g", "carbs_g", "fat_g", "sugar_g"]


def badge_kwargs(level: str, lang: str) -> dict:
    style = STATUS_BADGE[level]
    return {"label": t(VERDICT_STRING_KEY[level], lang), "icon": style["icon"], "color": style["color"]}


def nutrition_chart(food: dict, lang: str) -> alt.Chart:
    df = pd.DataFrame({
        "nutrient": [nutrient_name(k, lang) for k in NUTRIENT_KEYS],
        "key": NUTRIENT_KEYS,
        "value": [food.get(k, 0) for k in NUTRIENT_KEYS],
    })
    color_scale = alt.Scale(domain=NUTRIENT_KEYS, range=[NUTRIENT_COLORS[k] for k in NUTRIENT_KEYS])

    bars = alt.Chart(df).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6, size=34).encode(
        x=alt.X("nutrient:N", title=None, sort=None,
                axis=alt.Axis(labelColor=INK_MUTED, labelFontSize=12, domainColor=GRIDLINE,
                               tickColor=GRIDLINE, labelAngle=0)),
        y=alt.Y("value:Q", title="g", axis=alt.Axis(gridColor=GRIDLINE, labelColor=INK_MUTED,
                                                     domain=False, tickCount=4, titleColor=INK_MUTED)),
        color=alt.Color("key:N", scale=color_scale, legend=None),
        tooltip=[alt.Tooltip("nutrient:N", title=" "), alt.Tooltip("value:Q", title="g")],
    )
    labels = alt.Chart(df).mark_text(dy=-8, color=INK_PRIMARY, fontSize=12, fontWeight=600).encode(
        x=alt.X("nutrient:N", sort=None), y="value:Q", text=alt.Text("value:Q", format=".0f"),
    )
    return (bars + labels).properties(height=190).configure_view(strokeWidth=0)
