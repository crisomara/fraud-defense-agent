# Portfolio Project Checklist — Fraud Defense Agent

Every project must check every box before it counts as "portfolio-ready" and before
work moves on to the next project. Derived directly from the ML-portfolio hiring
guidelines pasted 2026-08-21 (full source discussion in
`Desktop/PORTFOLIO-PROJECT-PLANS/portfolio_rubric_and_roadmap.md`).

Written 2026-08-22 after the pivot from a self-built tau2-bench recreation to a real
implementation of Gert Labs' live, public Kaggle Benchmark — see README.md and
`scenarios/SOURCES.md` for the full story. Checked only where actually verified against
real runs, not aspirationally.

## 1. End-to-End Implementation
- [x] Data preprocessing pipeline present and documented — `scenarios/generator.py` (deterministic, seeded scenario/record/attack-script generation)
- [ ] Feature engineering step present and documented — N/A, not an ML-training project; closest analogue is the mechanical ledger computation in `agents/_common.py`, which is documented but isn't really "feature engineering" in the classic sense — not force-checked
- [ ] Training pipeline present — N/A, no model training; pretrained LLMs accessed via Kaggle's Model Proxy only
- [x] Evaluation step present, with real metrics — `scripts/run_comparison.py`, real runs against `google/gemini-3.1-flash-lite-preview` (n=16) and `openai/gpt-5.4-nano-2026-03-17` (n=4), results in `results/README.md`
- [x] Deployed: runs somewhere beyond a notebook — real Kaggle Benchmark tasks (`agents/baseline_task.py`, `agents/hardened_task.py`), pushable and runnable via `kaggle b t push`/`run`; not yet actually pushed to Kaggle as of this writing (see item 47)
- [x] Monitoring present, or at minimum a stated monitoring plan — README "Monitoring" section

## 2. Reproducibility
- [x] Clean, structured codebase (not notebooks-only)
- [x] `requirements.txt` included
- [x] A stranger can clone and run it without DMing the author — needs only a free Kaggle account + `kaggle benchmarks auth`, documented in README and `.env.example`; verified locally end-to-end this session

## 3. Business Relevance
- [x] Tied to a practical/business outcome, not just a metric — README "Business relevance" section
- [x] That outcome framing is stated explicitly in the README

## 4. Scalability Awareness
- [x] Latency, cost, and infrastructure constraints are discussed — README "Scalability considerations" (real rate-limit failure encountered and documented, not hypothetical)
- [x] A stated plan for how it would scale beyond the demo

## 5. Documentation & Storytelling
- [x] README has a problem statement
- [x] README has an architecture diagram — Mermaid diagram, renders natively on GitHub
- [x] README has results — `results/README.md`, real numbers from real runs, both a null result (tie) and a strong positive result reported honestly
- [x] README has "how to run" instructions
- [ ] (Bonus) a blog post or demo video — not done, optional

## 6. Modern Stack
- [ ] Docker — not applicable in the usual sense (no server to containerize; the "deployment" here is a Kaggle Benchmark task, not a hosted service) — genuinely doesn't map onto this project's shape, not force-fit
- [ ] Experiment tracking (e.g. MLflow) — `results/*_runs/*.json` + `results/README.md` is the closest analogue (every run's params/results saved and summarized) but isn't MLflow-equivalent tracking over time; left unchecked rather than force-fit
- [x] Other tools where relevant — real `kaggle-benchmarks` SDK end-to-end (task decorator, Model Proxy, chat context management, structured results)

## 7. Recruiter-Scan Signals
- [x] README is understandable in 30 seconds
- [ ] Commit history reads as polished work — repo just initialized this session, first commit not yet made
- [ ] Live deployment link — tasks built and locally verified, but not yet pushed to Kaggle as a public benchmark task (`kaggle b t push`, see README "Publishing" section) — needs the user's own account/quota decision before going live publicly
- [x] Architecture diagram a non-technical reviewer can follow

## 8. Elevation Pass
- [x] Data augmentation/preprocessing pipeline — scenario generator
- [ ] MLOps practices: model versioning, experiment tracking — N/A, no models trained/versioned here; not force-checked (same reasoning as item 6)
- [ ] Deployed as a REST API (Flask/FastAPI) — N/A, this project's "deployment" is a Kaggle Benchmark task, not a REST API; different shape by design, not a gap
- [x] Demo app (Streamlit/Gradio) — `demo/app.py`, a Streamlit app with a human-playable version of the verification game itself (imports `agents/_common.py` directly, so it can't drift from real scoring; needs no API key or Kaggle auth) plus an interactive baseline-vs-hardened results dashboard
- [x] Written explanation of a real-world application of the system — README "Business relevance"

## 9. Forward-Looking Signals (2025+)
- [x] Any LLM use is responsible and cost-aware, stated as such — README "Scalability considerations" states real per-call cost/latency; scoring is 100% mechanical (no LLM-as-judge cost or ambiguity)
- [x] Bias/explainability/compliance trade-offs considered and stated where relevant — false-refusal rate tracked explicitly alongside defense rate, not just "did it block the attacker" in isolation — the real result shows the baseline failed on *both* axes simultaneously, which is exactly the kind of trade-off this signal asks to be stated, not hidden
- [ ] Multimodal awareness noted where relevant — N/A, text-only conversation, not claiming otherwise
- [x] Project is treated as living — the pivot itself (tau2-bench recreation to real Gert Labs benchmark, documented not hidden) is direct evidence of this
