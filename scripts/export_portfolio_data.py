"""
Regenerate docs/assets/data.json for the portfolio site (charts on GitHub Pages).
Run from repo root: python scripts/export_portfolio_data.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MONEYNESS = [
    "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9",
    "1", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9",
]


def main() -> None:
    df = pd.read_csv(ROOT / "training_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])

    sub = df[df["Tenor"] == "10Y"].sort_values("Date")
    step = max(1, len(sub) // 400)
    sub = sub.iloc[::step]
    series = {
        "dates": [d.strftime("%Y-%m-%d") for d in sub["Date"]],
        "values": sub["1"].astype(float).round(6).tolist(),
    }

    last = df[df["Date"] == df["Date"].max()].set_index("Tenor")
    tenors = [t for t in df["Tenor"].unique() if t in last.index]
    heat = [[float(last.loc[t, m]) for m in MONEYNESS] for t in tenors]

    pred_path = ROOT / "predictions_filled.csv"
    forecast = None
    if pred_path.exists():
        p = pd.read_csv(pred_path)
        p10 = p[p["Tenor"] == "10Y"].head(60)
        forecast = {
            "dates": p10["Date"].tolist(),
            "values": p10["1"].astype(float).round(6).tolist(),
        }

    out = {
        "meta": {
            "trainingRows": int(len(df)),
            "uniqueDates": int(df["Date"].nunique()),
            "tenors": int(df["Tenor"].nunique()),
            "valMae": 0.0055,
            "valRmse": 0.0082,
            "valNote": "Approx. holdout on last 80 trading days; run notebook for exact metrics.",
        },
        "series10yAtm": series,
        "surfaceLastTrain": {"tenors": tenors, "moneyness": MONEYNESS, "z": heat},
        "forecast10yAtm": forecast,
    }

    out_dir = ROOT / "docs" / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "data.json"
    dest.write_text(json.dumps(out), encoding="utf-8")
    print(f"Wrote {dest}")


if __name__ == "__main__":
    main()
