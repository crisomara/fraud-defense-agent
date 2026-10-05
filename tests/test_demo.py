"""Tests for the demo: data builder and a Streamlit render smoke test.

The demo never calls a model, so these run with no credentials at all.
"""

import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

from demo import build_data

ROOT = Path(__file__).resolve().parent.parent


def test_build_pairs_baseline_and_hardened_runs(tmp_path, monkeypatch):
    baseline = tmp_path / "baseline_runs"
    hardened = tmp_path / "hardened_runs"
    baseline.mkdir()
    hardened.mkdir()
    (baseline / "google_gemini-x.json").write_text(json.dumps([{"scenario_id": "a"}]))
    (hardened / "google_gemini-x.json").write_text(json.dumps([{"scenario_id": "b"}]))
    # A baseline file with no hardened counterpart is skipped.
    (baseline / "openai_gpt-y.json").write_text("[]")

    monkeypatch.setattr(build_data, "BASELINE_DIR", baseline)
    monkeypatch.setattr(build_data, "HARDENED_DIR", hardened)

    data = build_data.build()
    assert list(data["models"]) == ["google/gemini-x"]
    assert data["models"]["google/gemini-x"]["hardened"] == [{"scenario_id": "b"}]


def test_committed_results_summary_is_valid():
    data = json.loads((ROOT / "demo" / "data" / "results_summary.json").read_text())
    assert "models" in data
    for variants in data["models"].values():
        assert set(variants) == {"baseline", "hardened"}


def test_demo_app_renders():
    at = AppTest.from_file(str(ROOT / "demo" / "app.py"), default_timeout=60)
    at.run()
    assert not at.exception
