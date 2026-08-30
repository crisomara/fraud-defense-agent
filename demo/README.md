# Live demo

A Streamlit app with three tabs:

1. **Play the Defender.** A human-playable version of the verification game
   itself. You play the SecureBank agent; a scripted caller (drawn from the same
   `scenarios/fraud_scenarios.json` the real comparison runs against) states fields
   one message at a time. A live trust ledger panel shows exactly what the
   hardened agent sees every turn, computed by importing `agents/_common.py`
   directly, so the demo can never drift from what the real scoring does. No API
   key, no Kaggle auth, no model calls.
2. **Baseline vs Hardened.** Real per-scenario results across every evaluated
   model, computed live from `demo/data/results_summary.json` (built by
   `demo/build_data.py`), with model/metric filters and a per-scenario drill-down.
3. **How it works.** The game rules and an interactive sandbox to try the
   verification and leak-detection logic directly.

## Run locally

```bash
cd fraud-defense-agent
python -m venv demo/.venv
demo/.venv/Scripts/activate   # demo/.venv/bin/activate on macOS/Linux
pip install -r demo/requirements.txt
streamlit run demo/app.py
```

## Deploy (Streamlit Community Cloud, free)

1. Push this repo to GitHub (already done: `crisomara/fraud-defense-agent`).
2. On [share.streamlit.io](https://share.streamlit.io), "New app", pick this
   repo/branch, set the main file path to `demo/app.py` and the requirements file
   to `demo/requirements.txt` under Advanced settings.
3. No secrets needed. This app never calls Kaggle or any LLM.
