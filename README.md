# Security and Privacy Risks of Generative AI — GenAI Risk Dashboard

**Suraj T (1DS23AI058)** · Data Security and Privacy (22AI73) Micro-Project · Dept. of AIML, DSCE

Identifies and classifies GenAI risks in prompt/response pairs using the **OWASP Top 10 for LLM Applications (2025)**,
scores them with **Risk = Likelihood × Impact**, detects/redacts PII, and shows everything in a Streamlit dashboard.

## Run

```bash
pip install -r requirements.txt
python data/generate_dataset.py      # builds data/genai_prompts.csv (synthetic, labelled)
python src/evaluate.py               # precision / recall / F1 + misclassified rows
streamlit run app.py                 # dashboard at http://localhost:8501
python report/build_report.py        # regenerates report/GenAI_Risk_Report_Suraj_T.docx
```

Optional: set `ANTHROPIC_API_KEY` to enable the Claude-based LLM judge and a real LLM in the chatbot demo.
Without it, everything runs offline (the chatbot uses a deliberately vulnerable simulated LLM).

## Structure

| File | Purpose |
|---|---|
| `src/risk_engine.py` | OWASP rules, PII detector (Luhn-checked cards), risk model, redaction |
| `src/evaluate.py` | Multi-label evaluation with scikit-learn |
| `src/llm_judge.py` | Optional Claude second-opinion classifier + chatbot model |
| `data/generate_dataset.py` | Synthetic labelled dataset (attack goals are placeholders) |
| `app.py` | Dashboard: Overview · Live Analyzer · Guarded Chatbot · Dataset · Evaluation · Risk Model |
| `report/build_report.py` | Builds the DOCX report with charts |

## Categories covered
LLM01 Prompt Injection · LLM02 Sensitive Information Disclosure · LLM05 Improper Output Handling ·
LLM06 Excessive Agency · LLM07 System Prompt Leakage · LLM09 Misinformation · LLM10 Unbounded Consumption
