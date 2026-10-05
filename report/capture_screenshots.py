"""
Captures dashboard screenshots for the report using Playwright + the installed Edge browser.
Requires the dashboard to be running:  streamlit run app.py --server.port 8502
Run:  python report/capture_screenshots.py
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://localhost:8502"
OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)


def tab(page, name):
    page.get_by_role("tab", name=name).click()
    page.wait_for_timeout(1500)


def visible(page, label):
    """Streamlit keeps every tab in the DOM; pick the element in the visible tab."""
    return page.get_by_label(label).locator("visible=true").first


with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    ctx = browser.new_context(viewport={"width": 1280, "height": 1000}, device_scale_factor=2, color_scheme="light")
    page = ctx.new_page()
    page.goto(URL)
    page.get_by_text("Interactions analysed").wait_for(timeout=60000)
    page.wait_for_timeout(4000)

    # 1. Overview (tall viewport to capture all charts)
    page.set_viewport_size({"width": 1280, "height": 1900})
    page.wait_for_timeout(2500)
    page.screenshot(path=OUT / "ss_overview.png")
    page.set_viewport_size({"width": 1280, "height": 1000})

    # 2. Live analyzer with the PII leakage sample
    tab(page, "🔍 Live Analyzer")
    page.locator("[data-testid='stSelectbox']").locator("visible=true").first.click()
    page.get_by_role("option", name="PII leakage").click()
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Analyze").click()
    page.get_by_text("Privacy exposure score").wait_for()
    page.set_viewport_size({"width": 1280, "height": 1650})
    page.wait_for_timeout(1500)
    page.screenshot(path=OUT / "ss_analyzer.png")
    page.set_viewport_size({"width": 1280, "height": 1000})

    # 3. Guarded chatbot - input guard blocks the attack
    tab(page, "🤖 Guarded Chatbot")
    page.get_by_role("button", name="Send").click()
    page.get_by_text("Final answer to user").wait_for()
    page.wait_for_timeout(800)
    page.screenshot(path=OUT / "ss_chatbot_blocked.png")

    # 4. Guarded chatbot - input guard OFF, output guard still withholds the leak
    page.locator("[data-testid='stCheckbox']", has_text="Input guard").locator("visible=true").first.click()
    page.wait_for_timeout(800)
    page.get_by_role("button", name="Send").click()
    page.get_by_text("LLM raw reply").wait_for()
    page.wait_for_timeout(800)
    page.screenshot(path=OUT / "ss_chatbot_output_guard.png")

    # 5. Evaluation
    tab(page, "✅ Evaluation")
    page.set_viewport_size({"width": 1280, "height": 1700})
    page.wait_for_timeout(2500)
    page.screenshot(path=OUT / "ss_evaluation.png")

    # 6. Dataset explorer
    tab(page, "🗂️ Dataset")
    page.set_viewport_size({"width": 1280, "height": 900})
    page.wait_for_timeout(2000)
    page.screenshot(path=OUT / "ss_dataset.png")

    # 7. Risk model
    tab(page, "📐 Risk Model & Mitigations")
    page.set_viewport_size({"width": 1280, "height": 1550})
    page.wait_for_timeout(2500)
    page.screenshot(path=OUT / "ss_riskmodel.png")

    browser.close()
print("Screenshots saved to", OUT)
