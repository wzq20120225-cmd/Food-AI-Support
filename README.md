# NutriPlate

Personalized nutrition assistant — a Congressional App Challenge 2026 submission. See [`PLAN.md`](./PLAN.md) for the full product plan.

Both entry points share the same decision engine (`engine/decision_engine.py`):

- **📷 Photo Scan**: take a photo of any food; AI identifies it and estimates its nutritional content
- **🍽️ Menu Browse**: browse the cafeteria menu and get automatic recommendations based on your goal (cut fat / build muscle / boost a vitamin / balanced)

Both modes combine the health profile you fill in on the sidebar (allergens, chronic conditions, goals) to produce a three-tier verdict:
🚫 Avoid (allergy/medical contraindication — highest priority, never overridden by other recommendation logic), ⚠️ Not recommended (a nutrition metric exceeds your target), ✅ OK to eat.

The UI defaults to English, with a toggle to Chinese in the top-right corner (`engine/i18n.py` centrally manages all copy and verdict-reason templates).

Visually, it follows Streamlit's own recommended "native components + `config.toml` theme" approach rather than hand-written CSS: a dark warm-brown sidebar + warm-orange accent color + Fraunces serif heading font; allergens/conditions use `st.pills` multi-select capsules (friendlier than a dropdown — all 9 options visible at a glance); dietary goal/meal/portion size use `st.segmented_control`; verdicts use native `st.badge`; icons are all Material Symbols rather than emoji, which can render inconsistently across systems.

## Running it

```bash
# 1. Create a virtual environment and install dependencies (one-time setup)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. (Optional) Configure AI image recognition
cp .env.example .env
# Edit .env and fill in your ANTHROPIC_API_KEY
# Works fine without it too: photo scan automatically falls back to "demo mode" using sample data to show the full flow

# 3. Launch
streamlit run app.py
```

Your browser will automatically open `http://localhost:8501`.

## Project structure

```
app.py                      # Streamlit UI (Photo Scan tab + Menu Browse tab), built entirely from native components
.streamlit/config.toml      # Theme: warm-orange accent + dark sidebar + Fraunces heading font, no custom CSS
engine/
  decision_engine.py        # Core verdict logic: allergy check -> condition check -> goal scoring, shared by both entry points
  profile.py                # User health profile: goals/allergens/conditions + AI parsing of free-text descriptions
  vision.py                 # Calls the Claude API for image recognition; falls back to demo mode automatically with no API key
  i18n.py                   # All English/Chinese copy + localized rendering of verdict reasons (English by default)
  theme.py                  # Chart colors (nutrition bar charts) + icon/color mapping for verdict results
data/menu.json              # Sample cafeteria menu data (breakfast/lunch/dinner), swap in the real school menu as needed
tests/
  test_decision_engine.py   # Decision engine unit tests (especially the allergy-priority rule)
  test_i18n.py               # Bilingual rendering tests for verdict reasons
  test_app_smoke.py          # Headless smoke test: UI doesn't error across all four goals x English/Chinese toggle
```

## Testing

```bash
python3 -m pytest tests/ -v
```

## Security note

`.env` is already in `.gitignore` — **do not** commit your API key to Git or push it to a public GitHub repo.
