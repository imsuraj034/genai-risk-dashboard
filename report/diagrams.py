"""Draws the system architecture and data-flow diagrams for the report (matplotlib)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch  # noqa: E402

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)
plt.rcParams["font.family"] = "DejaVu Sans"


def box(ax, x, y, w, h, text, fc="#e7f0ff", ec="#1f3b73", fs=9, bold=False, style="round,pad=0.02,rounding_size=0.08"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=style, fc=fc, ec=ec, lw=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, weight="bold" if bold else "normal", wrap=True)


def arrow(ax, x1, y1, x2, y2, label="", fs=7.5, off=(0, 0.12), rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=13, lw=1.3, color="#333",
                                 connectionstyle=f"arc3,rad={rad}"))
    if label:
        ax.text((x1 + x2) / 2 + off[0], (y1 + y2) / 2 + off[1], label, ha="center", va="center", fontsize=fs,
                style="italic", bbox=dict(fc="white", ec="none", pad=0.5))


# ------------------------------------------------------------ architecture
fig, ax = plt.subplots(figsize=(10, 6.6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6.6)
ax.axis("off")

# layer bands
for y, h, name, c in [(5.25, 1.15, "Presentation layer", "#fff4e6"), (2.55, 2.5, "Processing layer", "#eef6ee"),
                      (0.15, 2.2, "Data & model layer", "#f3f0ff")]:
    ax.add_patch(FancyBboxPatch((0.1, y), 9.8, h, boxstyle="round,pad=0.0,rounding_size=0.05", fc=c, ec="#bbb", lw=1))
    ax.text(0.25, y + h - 0.18, name, fontsize=8.5, weight="bold", color="#555", va="top")

box(ax, 0.4, 5.45, 1.5, 0.6, "User /\nSecurity analyst", fc="#ffffff", bold=True)
box(ax, 2.5, 5.4, 7.1, 0.7, "Streamlit GenAI Risk Dashboard\nOverview | Live Analyzer | Guarded Chatbot | Dataset | Evaluation | Risk Model",
    fc="#ffe8cc", ec="#b35c00", bold=True)
arrow(ax, 1.9, 5.75, 2.5, 5.75)

# processing
box(ax, 0.5, 3.75, 2.0, 0.85, "Input Guard\n(scan prompt)", fc="#d3f9d8", ec="#2b8a3e")
box(ax, 2.9, 2.85, 4.3, 1.9, "", fc="#ffffff", ec="#2b8a3e")
ax.text(5.05, 4.55, "Risk Engine (risk_engine.py)", ha="center", fontsize=9.5, weight="bold")
box(ax, 3.05, 3.65, 1.95, 0.7, "OWASP LLM\nrule detector", fs=8.5)
box(ax, 5.1, 3.65, 1.95, 0.7, "PII detector\n(+ Luhn check)", fs=8.5)
box(ax, 3.05, 2.95, 1.95, 0.6, "Risk scorer\nRisk = L x I", fs=8.5)
box(ax, 5.1, 2.95, 1.95, 0.6, "Redactor &\nmitigation advisor", fs=8.5)
box(ax, 7.6, 3.75, 2.0, 0.85, "Output Guard\n(scan response,\nDLP + redaction)", fc="#d3f9d8", ec="#2b8a3e", fs=8.5)
box(ax, 7.6, 2.75, 2.0, 0.7, "Evaluator\n(scikit-learn P/R/F1)", fc="#d3f9d8", ec="#2b8a3e", fs=8.5)

arrow(ax, 1.5, 5.4, 1.5, 4.6, "prompt", off=(0.35, 0))
arrow(ax, 2.5, 4.15, 2.9, 4.15)
arrow(ax, 7.2, 4.15, 7.6, 4.15)
arrow(ax, 8.6, 4.6, 8.6, 5.4, "result", off=(0.35, 0))
arrow(ax, 7.2, 3.1, 7.6, 3.1)

# data & model
box(ax, 0.5, 0.45, 2.1, 1.0, "Synthetic dataset\n114 labelled prompt /\nresponse pairs (CSV)", fc="#e5dbff", ec="#5f3dc4", fs=8.5)
box(ax, 2.95, 0.45, 2.1, 1.0, "Rule base\nOWASP patterns +\nPII patterns, weights", fc="#e5dbff", ec="#5f3dc4", fs=8.5)
box(ax, 5.4, 0.45, 2.0, 1.0, "LLM (optional)\nClaude via Anthropic SDK\n/ simulated LLM", fc="#e5dbff", ec="#5f3dc4", fs=8.5)
box(ax, 7.75, 0.45, 1.9, 1.0, "Results store\nresults.csv,\nmetrics.json", fc="#e5dbff", ec="#5f3dc4", fs=8.5)
arrow(ax, 1.55, 1.45, 3.4, 2.85, "records", off=(-0.5, 0.1))
arrow(ax, 4.0, 1.45, 4.0, 2.95)
arrow(ax, 7.0, 1.45, 7.6, 3.9, "LLM reply", off=(-0.55, -0.1))
arrow(ax, 8.6, 2.75, 8.6, 1.45, "metrics", off=(0.38, 0))

plt.tight_layout()
plt.savefig(OUT / "fig_architecture.png", dpi=200)
plt.close()

# ------------------------------------------------------------ DFD level 1
fig, ax = plt.subplots(figsize=(10, 7))
ax.set_xlim(0, 10)
ax.set_ylim(-0.5, 6.6)
ax.axis("off")


def process(ax, x, y, r, num, text):
    ax.add_patch(Circle((x, y), r, fc="#e7f0ff", ec="#1f3b73", lw=1.5))
    ax.text(x, y + r * 0.45, num, ha="center", va="center", fontsize=8.5, weight="bold")
    ax.text(x, y - r * 0.12, text, ha="center", va="center", fontsize=8)


def store(ax, x, y, w, label, text):
    ax.plot([x, x + w], [y + 0.45, y + 0.45], color="#5f3dc4", lw=1.5)
    ax.plot([x, x + w], [y, y], color="#5f3dc4", lw=1.5)
    ax.plot([x, x], [y, y + 0.45], color="#5f3dc4", lw=1.5)
    ax.plot([x + 0.45, x + 0.45], [y, y + 0.45], color="#5f3dc4", lw=1.2)
    ax.text(x + 0.22, y + 0.225, label, ha="center", va="center", fontsize=8, weight="bold")
    ax.text(x + 0.45 + (w - 0.45) / 2, y + 0.225, text, ha="center", va="center", fontsize=8)


box(ax, 0.2, 4.7, 1.5, 0.75, "USER", fc="#fff", bold=True, style="square,pad=0.02")
box(ax, 8.3, 4.7, 1.5, 0.75, "LLM\n(Claude /\nsimulated)", fc="#fff", bold=True, style="square,pad=0.02", fs=8)

process(ax, 3.0, 5.08, 0.72, "1.0", "Scan prompt\n(Input Guard)")
process(ax, 5.75, 5.08, 0.72, "2.0", "Forward /\nBlock")
process(ax, 9.05, 2.85, 0.72, "3.0", "Scan response\n(Output Guard)")
process(ax, 5.75, 2.85, 0.72, "4.0", "Classify &\nscore risk (LxI)")
process(ax, 3.0, 2.85, 0.72, "5.0", "Redact &\nrecommend")
process(ax, 1.0, 0.9, 0.65, "6.0", "Evaluate\nP / R / F1")

store(ax, 2.1, 0.68, 2.3, "D2", "Synthetic dataset")
store(ax, 4.7, 0.68, 2.3, "D1", "OWASP + PII rules")
store(ax, 7.4, 0.68, 2.4, "D3", "Results & metrics")

arrow(ax, 1.7, 5.08, 2.28, 5.08, "prompt", off=(0, 0.17))
arrow(ax, 3.72, 5.08, 5.03, 5.08, "labels, level", off=(0, 0.17))
arrow(ax, 6.47, 5.08, 8.3, 5.08, "screened prompt", off=(0, 0.17))
arrow(ax, 5.6, 5.78, 1.2, 5.45, "blocked message", off=(0, 0.55), rad=0.35)
arrow(ax, 9.05, 4.7, 9.05, 3.57, "raw reply", off=(0.42, 0))
arrow(ax, 8.33, 2.85, 6.47, 2.85, "response findings", off=(0, 0.17))
arrow(ax, 5.03, 2.85, 3.72, 2.85, "risk, PII spans", off=(0, 0.17))
arrow(ax, 2.5, 3.37, 1.2, 4.7, "safe answer +\nmitigations", off=(-0.45, -0.05))
arrow(ax, 5.85, 1.13, 5.85, 2.13, "rules", off=(0.3, 0))
arrow(ax, 6.35, 2.3, 8.3, 1.13, "assessment", off=(0.25, 0.12))
arrow(ax, 2.1, 0.9, 1.65, 0.9, "")
ax.text(2.0, 1.32, "labelled data", ha="center", fontsize=7.5, style="italic")
arrow(ax, 1.0, 0.25, 8.6, 0.68, "metrics", off=(0, -0.55), rad=0.12)

plt.tight_layout()
plt.savefig(OUT / "fig_dfd.png", dpi=200)
plt.close()

# ------------------------------------------------------------ DFD level 0 (context)
fig, ax = plt.subplots(figsize=(9, 2.6))
ax.set_xlim(0, 9)
ax.set_ylim(0, 2.6)
ax.axis("off")
box(ax, 0.2, 0.9, 1.6, 0.8, "USER", fc="#fff", bold=True, style="square,pad=0.02")
ax.add_patch(Circle((4.5, 1.3), 1.05, fc="#e7f0ff", ec="#1f3b73", lw=1.5))
ax.text(4.5, 1.55, "0.0", ha="center", fontsize=9, weight="bold")
ax.text(4.5, 1.1, "GenAI Risk\nDashboard System", ha="center", va="center", fontsize=9)
box(ax, 7.2, 0.9, 1.6, 0.8, "LLM", fc="#fff", bold=True, style="square,pad=0.02")
arrow(ax, 1.8, 1.55, 3.45, 1.55, "prompt / response", off=(0, 0.17))
arrow(ax, 3.45, 1.05, 1.8, 1.05, "risk report, redacted text", off=(0, -0.2))
arrow(ax, 5.55, 1.55, 7.2, 1.55, "screened prompt", off=(0, 0.17))
arrow(ax, 7.2, 1.05, 5.55, 1.05, "model reply", off=(0, -0.2))
plt.tight_layout()
plt.savefig(OUT / "fig_dfd0.png", dpi=200)
plt.close()
print("Diagrams saved")

# ------------------------------------------------------------ methodology workflow
fig, ax = plt.subplots(figsize=(10, 2.3))
ax.set_xlim(0, 10)
ax.set_ylim(0, 2.3)
ax.axis("off")
steps = ["Problem", "Analyse", "Design", "Implement\nPrototype", "Test", "Evaluate", "Report", "Demonstrate"]
w, gap = 1.0, 0.2
for i, s_ in enumerate(steps):
    x = 0.15 + i * (w + gap)
    box(ax, x, 0.75, w, 0.8, s_, fc="#e7f0ff" if i % 2 == 0 else "#d3f9d8", fs=8.5, bold=True)
    if i < len(steps) - 1:
        arrow(ax, x + w, 1.15, x + w + gap, 1.15)
plt.tight_layout()
plt.savefig(OUT / "fig_workflow.png", dpi=200)
plt.close()
print("Workflow saved")
