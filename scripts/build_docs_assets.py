"""
Generate static images and training_data.html for the GitHub Pages portfolio.
Run from repo root: python scripts/build_docs_assets.py
Requires: pandas, matplotlib, seaborn
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
IMG = DOCS / "assets" / "images"
TRAIN_CSV = ROOT / "training_data.csv"
MONEYNESS = [
    "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9",
    "1", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9",
]

# Match portfolio dark theme
BG = "#131820"
FG = "#e8ecf1"
GRID = "#1e2633"
ACCENT = "#3d9cf5"


def _style_mpl() -> None:
    plt.style.use("dark_background")
    plt.rcParams.update(
        {
            "figure.facecolor": BG,
            "axes.facecolor": BG,
            "axes.edgecolor": GRID,
            "axes.labelcolor": FG,
            "text.color": FG,
            "xtick.color": FG,
            "ytick.color": FG,
            "grid.color": GRID,
            "font.family": "sans-serif",
            "font.sans-serif": ["Segoe UI", "Helvetica", "Arial", "DejaVu Sans"],
        }
    )


def save_chart_images(df: pd.DataFrame) -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    _style_mpl()

    sub = df[df["Tenor"] == "10Y"].sort_values("Date")
    fig, ax = plt.subplots(figsize=(10, 4), dpi=120)
    ax.plot(sub["Date"], sub["1"].astype(float), color=ACCENT, lw=1.2)
    ax.set_title("10Y tenor, moneyness 1.0 (ATM-style) — training data", color=FG, pad=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Level")
    ax.grid(True, alpha=0.35)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(IMG / "chart-history.png", facecolor=BG, edgecolor="none")
    plt.close(fig)

    last = df[df["Date"] == df["Date"].max()].set_index("Tenor")
    tenors = [t for t in df["Tenor"].unique() if t in last.index]
    mat = last.loc[tenors, MONEYNESS].astype(float)

    fig_h = max(5, len(tenors) * 0.22)
    fig, ax = plt.subplots(figsize=(9, fig_h), dpi=120)
    sns.heatmap(
        mat,
        ax=ax,
        cmap="viridis",
        cbar_kws={"label": "Level"},
        xticklabels=True,
        yticklabels=True,
        linewidths=0,
    )
    ax.set_title("Surface — last training day (tenor × moneyness)", color=FG, pad=12)
    ax.set_xlabel("Moneyness")
    ax.set_ylabel("Tenor")
    fig.tight_layout()
    fig.savefig(IMG / "surface-heatmap.png", facecolor=BG, edgecolor="none")
    plt.close(fig)

    # Hero preview: same line chart, wider aspect
    fig, ax = plt.subplots(figsize=(11, 3.2), dpi=120)
    ax.plot(sub["Date"], sub["1"].astype(float), color=ACCENT, lw=1.4)
    ax.set_title("F&O surface slice (10Y, ATM)", color=FG, fontsize=11, pad=8)
    ax.set_ylabel("Level")
    ax.grid(True, alpha=0.35)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(IMG / "hero-preview.png", facecolor=BG, edgecolor="none")
    plt.close(fig)

    pred_path = ROOT / "predictions_filled.csv"
    if pred_path.exists():
        p = pd.read_csv(pred_path)
        p10 = p[p["Tenor"] == "10Y"].head(80)
        if len(p10) > 1:
            fig, ax = plt.subplots(figsize=(10, 3.5), dpi=120)
            ax.plot(
                range(len(p10)),
                p10["1"].astype(float),
                color="#34d399",
                lw=1.2,
                marker="o",
                markersize=2,
            )
            ax.set_title("Forecast sample — 10Y ATM (first template rows)", color=FG, pad=12)
            ax.set_xlabel("Step (submission order)")
            ax.set_ylabel("Level")
            ax.grid(True, alpha=0.35)
            fig.tight_layout()
            fig.savefig(IMG / "chart-forecast.png", facecolor=BG, edgecolor="none")
            plt.close(fig)


def write_training_data_html(df: pd.DataFrame) -> None:
    num = [c for c in df.columns if c not in ("Date", "Tenor")]
    desc = df[num].describe().T
    nulls = df.isnull().sum()
    info_rows = [
        ("Rows", f"{len(df):,}"),
        ("Columns", str(len(df.columns))),
        ("Unique dates", f"{df['Date'].nunique():,}"),
        ("Unique tenors", str(df["Tenor"].nunique())),
        ("Date range", f"{df['Date'].min()} → {df['Date'].max()}"),
    ]

    table_style = """
    table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.9rem; }
    th, td { border: 1px solid #2a3444; padding: 0.45rem 0.65rem; text-align: left; }
    th { background: #1a2230; color: #8b98a8; font-weight: 600; }
    tr:nth-child(even) td { background: #151b24; }
    h1 { font-size: 1.75rem; margin-bottom: 0.25rem; }
    h2 { font-size: 1.2rem; margin-top: 2rem; color: #3d9cf5; }
    .muted { color: #8b98a8; font-size: 0.95rem; }
    code { background: #1a2230; padding: 0.15rem 0.4rem; border-radius: 4px; }
    .wrap { max-width: 1100px; margin: 0 auto; padding: 1.5rem; }
    a { color: #3d9cf5; }
    """

    head_html = df.head(25).to_html(classes="data", border=0, index=False)
    desc_html = desc.round(6).to_html(classes="data", border=0)
    null_html = nulls.to_frame("missing").to_html(classes="data", border=0)

    info_html = (
        "<table class='data'><thead><tr><th>Field</th><th>Value</th></tr></thead><tbody>"
        + "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in info_rows)
        + "</tbody></table>"
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Training data — EDA | F&amp;O</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&display=swap" rel="stylesheet" />
  <style>
    body {{
      font-family: "DM Sans", system-ui, sans-serif;
      background: #0c0f14;
      color: #e8ecf1;
      margin: 0;
      line-height: 1.55;
    }}
    {table_style}
  </style>
</head>
<body>
  <div class="wrap">
    <p class="muted"><a href="index.html">Home</a></p>
    <h1>Training data — EDA report</h1>

    <h2>Dataset summary</h2>
    {info_html}

    <h2>Missing values per column</h2>
    {null_html}

    <h2>Numeric columns — describe()</h2>
    {desc_html}

    <h2>Sample rows (first 25)</h2>
    {head_html}

  </div>
</body>
</html>
"""
    (DOCS / "training_data.html").write_text(html, encoding="utf-8")


def _fmt_us_date(d: pd.Timestamp) -> str:
    t = pd.Timestamp(d)
    return f"{t.month}/{t.day}/{t.year}"


def build_demo_payload(df: pd.DataFrame) -> dict:
    """Flat lookup for static-site demo: forecast rows + recent training history."""
    lookup: dict[str, float] = {}
    pred_path = ROOT / "predictions_filled.csv"

    tail_days = 150
    udates = sorted(df["Date"].unique())
    tail = set(udates[-tail_days:]) if len(udates) > tail_days else set(udates)
    sub = df[df["Date"].isin(tail)]
    for _, row in sub.iterrows():
        ds = _fmt_us_date(row["Date"])
        for m in MONEYNESS:
            lookup[f"{ds}|{row['Tenor']}|{m}"] = round(float(row[m]), 6)

    n_pred = 0
    if pred_path.exists():
        pred = pd.read_csv(pred_path)
        for _, row in pred.iterrows():
            ds = str(row["Date"]).strip()
            for m in MONEYNESS:
                lookup[f"{ds}|{row['Tenor']}|{m}"] = round(float(row[m]), 6)
            n_pred += 1

    return {
        "moneyness": MONEYNESS,
        "tenorsAll": df["Tenor"].drop_duplicates().tolist(),
        "meta": {
            "trainingRows": int(len(df)),
            "uniqueDates": int(df["Date"].nunique()),
            "tenorCount": int(df["Tenor"].nunique()),
            "valMae": 0.0055,
            "valRmse": 0.0082,
            "trainingDatesInDemo": len(tail),
            "predictionRows": n_pred,
            "note": (
                "Lookup includes all model outputs in predictions_filled.csv plus the last "
                f"{len(tail)} trading days of training. Older training dates: open the CSV or notebook."
            ),
        },
        "lookup": lookup,
    }


def write_demo_assets(payload: dict) -> None:
    """JSON for fetch (GitHub Pages) + JS embed for file:// local opening."""
    out_dir = DOCS / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "demo_lookup.json").write_text(json.dumps(payload), encoding="utf-8")

    js_literal = json.dumps(payload, separators=(",", ":"))
    js_literal = js_literal.replace("</", "<\\/")
    (out_dir / "demo-data.js").write_text(
        "window.__DEMO_LOOKUP_PAYLOAD = " + js_literal + ";\n",
        encoding="utf-8",
    )


def write_training_profile_html(df: pd.DataFrame) -> None:
    """Full exploratory report via ydata-profiling, or a minimal stub if the package is missing."""
    dest = DOCS / "training_profile.html"
    stub = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"/><title>Profiling report</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600&display=swap" rel="stylesheet"/>
<style>
body{font-family:'DM Sans',sans-serif;background:#0c0f14;color:#e8ecf1;margin:0;padding:2rem;line-height:1.6;max-width:640px;margin-inline:auto}
a{color:#3d9cf5}
</style>
</head>
<body>
<p><a href="index.html">Home</a></p>
<h1>Profiling report</h1>
<p>Full report is not included in this build.</p>
</body>
</html>"""

    try:
        from ydata_profiling import ProfileReport
    except ImportError:
        dest.write_text(stub, encoding="utf-8")
        print("ydata-profiling not installed; wrote stub training_profile.html")
        return

    try:
        report = ProfileReport(
            df,
            title="Training data — Pandas Profiling (ydata-profiling)",
            minimal=True,
        )
        report.to_file(dest)
        print(f"Wrote {dest}")
    except Exception as exc:
        print(f"ydata-profiling failed ({exc!r}); wrote stub training_profile.html")
        dest.write_text(stub, encoding="utf-8")


def main() -> None:
    df = pd.read_csv(TRAIN_CSV)
    df["Date"] = pd.to_datetime(df["Date"])
    save_chart_images(df)
    write_training_data_html(df)
    demo_payload = build_demo_payload(df)
    write_demo_assets(demo_payload)
    write_training_profile_html(df)
    print(f"Wrote images under {IMG}")
    print(f"Wrote {DOCS / 'training_data.html'}")
    print(f"Wrote {DOCS / 'assets' / 'demo_lookup.json'} and demo-data.js")


if __name__ == "__main__":
    main()
