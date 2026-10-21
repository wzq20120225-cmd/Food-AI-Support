"""Headless smoke test: the app must render with no exceptions, across goals
and languages. Uses Streamlit's AppTest to actually run the script rather
than just importing it — catches "crashes on render" bugs static checks miss.
"""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


def test_app_renders_with_default_profile_in_english():
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception
    assert any("NutriPlate" in el.body for el in at.title)


def test_app_renders_for_each_goal_with_an_allergen_selected():
    for goal in ["weight_loss", "muscle_gain", "vitamin_boost", "balanced"]:
        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        at.sidebar.segmented_control(key="goal").set_value(goal).run()
        at.sidebar.pills(key="allergens").set_value(["peanuts"]).run()
        assert not at.exception, f"goal={goal} raised: {at.exception}"


def test_switching_to_chinese_renders_without_exceptions_and_keeps_selection():
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    at.sidebar.segmented_control(key="goal").set_value("muscle_gain").run()
    at.segmented_control(key="lang_option").set_value("中文").run()
    assert not at.exception
    # Goal/allergen pills are always-visible (no collapsed state to go stale),
    # so unlike a selectbox's closed label, the selection survives a language switch.
    assert at.sidebar.segmented_control(key="goal").value == "muscle_gain"
