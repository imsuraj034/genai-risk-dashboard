"""
Evaluates the risk engine against the labelled synthetic dataset.
Outputs per-category precision / recall / F1 and a risky-vs-safe confusion matrix.

Run:  python src/evaluate.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.preprocessing import MultiLabelBinarizer

sys.path.insert(0, str(Path(__file__).parent))
from risk_engine import CATEGORIES, SAFE, assess  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "genai_prompts.csv"
RESULTS = ROOT / "data" / "results.csv"
METRICS = ROOT / "data" / "metrics.json"


def run_assessment(df: pd.DataFrame) -> pd.DataFrame:
    recs = []
    for _, r in df.iterrows():
        a = assess(r["prompt"], r["response"])
        recs.append({
            **r.to_dict(),
            "pred_labels": ";".join(a.labels),
            "risk_score": a.overall_risk,
            "risk_level": a.overall_level,
            "privacy_exposure": a.privacy_exposure,
            "pii_types": ";".join(sorted({p["type"] for p in a.pii})),
            "evidence": " | ".join(f"{f.code}: {', '.join(f.evidence)}" for f in a.findings),
        })
    return pd.DataFrame(recs)


def compute_metrics(res: pd.DataFrame) -> dict:
    codes = list(CATEGORIES)
    y_true = [set(s.split(";")) - {SAFE} for s in res["true_labels"]]
    y_pred = [set(s.split(";")) - {SAFE} for s in res["pred_labels"]]
    mlb = MultiLabelBinarizer(classes=codes)
    Yt, Yp = mlb.fit_transform(y_true), mlb.transform(y_pred)

    p, r, f, s = precision_recall_fscore_support(Yt, Yp, zero_division=0)
    per_cat = {c: {"name": CATEGORIES[c]["name"], "precision": round(p[i], 3), "recall": round(r[i], 3),
                   "f1": round(f[i], 3), "support": int(s[i])} for i, c in enumerate(codes)}
    mp, mr, mf, _ = precision_recall_fscore_support(Yt, Yp, average="micro", zero_division=0)
    Mp, Mr, Mf, _ = precision_recall_fscore_support(Yt, Yp, average="macro", zero_division=0)

    risky_true = [int(bool(t)) for t in y_true]
    risky_pred = [int(bool(t)) for t in y_pred]
    cm = confusion_matrix(risky_true, risky_pred, labels=[0, 1])
    bp, br, bf, _ = precision_recall_fscore_support(risky_true, risky_pred, average="binary", zero_division=0)

    return {
        "n_samples": len(res),
        "per_category": per_cat,
        "micro": {"precision": round(mp, 3), "recall": round(mr, 3), "f1": round(mf, 3)},
        "macro": {"precision": round(Mp, 3), "recall": round(Mr, 3), "f1": round(Mf, 3)},
        "exact_match_accuracy": round(accuracy_score(Yt, Yp), 3),
        "binary": {
            "accuracy": round(accuracy_score(risky_true, risky_pred), 3),
            "precision": round(bp, 3), "recall": round(br, 3), "f1": round(bf, 3),
            "confusion_matrix": {"TN": int(cm[0, 0]), "FP": int(cm[0, 1]), "FN": int(cm[1, 0]), "TP": int(cm[1, 1])},
        },
    }


def main():
    df = pd.read_csv(DATA)
    res = run_assessment(df)
    res.to_csv(RESULTS, index=False)
    m = compute_metrics(res)
    METRICS.write_text(json.dumps(m, indent=2))

    print(f"Samples: {m['n_samples']}")
    print(f"{'Code':6} {'Category':36} {'P':>6} {'R':>6} {'F1':>6} {'N':>4}")
    for c, v in m["per_category"].items():
        print(f"{c:6} {v['name']:36} {v['precision']:6.2f} {v['recall']:6.2f} {v['f1']:6.2f} {v['support']:4}")
    print(f"Micro F1 {m['micro']['f1']:.3f} | Macro F1 {m['macro']['f1']:.3f} | Exact match {m['exact_match_accuracy']:.3f}")
    print("Risky vs safe:", m["binary"])

    same = [set(t.split(";")) == set(p.split(";")) for t, p in zip(res["true_labels"], res["pred_labels"])]
    wrong = res[[not s for s in same]]
    print(f"\nMisclassified rows ({len(wrong)}):")
    for _, r in wrong.iterrows():
        print(f"  #{r['id']:<3} true={r['true_labels']:<18} pred={r['pred_labels']:<18} {r['prompt'][:70]}")


if __name__ == "__main__":
    main()
