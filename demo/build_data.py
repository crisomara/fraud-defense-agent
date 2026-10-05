"""
Regenerates demo/data/results_summary.json from the real per-scenario result files in
results/baseline_runs/ and results/hardened_runs/ (gitignored -- large, one file per
model). This script's OUTPUT is small and committed, so the demo never needs the raw
run files at deploy time, but every number in it is still traceable back to a real run.

Re-run this after any new `python -m scripts.run_comparison` against a new model --
the demo's results tab is fully data-driven off this file, so a new model just shows
up, no app.py changes needed.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE_DIR = ROOT / "results" / "baseline_runs"
HARDENED_DIR = ROOT / "results" / "hardened_runs"
OUT_PATH = Path(__file__).parent / "data" / "results_summary.json"


def _load_model_file(path: Path) -> list[dict]:
    return json.loads(path.read_text())


def build() -> dict:
    model_files = sorted(BASELINE_DIR.glob("*.json"))
    models = {}
    for baseline_path in model_files:
        model_slug = baseline_path.stem
        hardened_path = HARDENED_DIR / baseline_path.name
        if not hardened_path.exists():
            continue
        model_name = model_slug.replace("_", "/", 1)  # e.g. google_gemini-x -> google/gemini-x
        models[model_name] = {
            "baseline": _load_model_file(baseline_path),
            "hardened": _load_model_file(hardened_path),
        }
    return {"models": models}


if __name__ == "__main__":
    data = build()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, indent=2))
    print(f"Wrote {OUT_PATH} with {len(data['models'])} models: {list(data['models'])}")
