# Fraud Defense Agent

[![CI](https://github.com/crisomara/fraud-defense-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/crisomara/fraud-defense-agent/actions/workflows/ci.yml) [![Security](https://github.com/crisomara/fraud-defense-agent/actions/workflows/security.yml/badge.svg)](https://github.com/crisomara/fraud-defense-agent/actions/workflows/security.yml)

An independent recreation and extension of **Gert Labs' Adversarial Customer Service**
benchmark (live on Kaggle Benchmarks, `kaggle.com/benchmarks/gert-labs/adversarial-customer-service`)
— a two-sided security game where a bank support agent must verify a caller's identity
purely from conversation, against callers who are either the real customer or a
well-informed identity thief. This project reproduces the published game rules as a
real, runnable Kaggle Benchmark task, then engineers and measures whether a
code-enforced "trust ledger" orchestration strategy actually improves defense over a
plain prompt — same models, same scenarios, honest comparison.

**Not affiliated with Gert Labs Inc.** See [`scenarios/SOURCES.md`](scenarios/SOURCES.md)
for exactly what's reproduced from their published methodology versus our own
construction, including the deliberate scope reduction (scripted caller instead of a
second LLM) and why.

**[Live demo](demo/README.md)** -- play the verification game yourself (no API key
needed) and browse the baseline-vs-hardened results interactively. Run locally with
`streamlit run demo/app.py`; see [`demo/README.md`](demo/README.md) for one-click
deploy instructions.

---

## Architecture

```mermaid
flowchart LR
    Gen[scenarios/generator.py\nscripted records + attack scripts] --> Data[(fraud_scenarios.json)]

    Data --> Runner[scripts/run_comparison.py]

    subgraph variants["Two agent variants, same policy, same model"]
        Base[agents/baseline_task.py\nplain prompt]
        Hard[agents/hardened_task.py\ntrust-ledger + hard gate]
    end

    Runner --> Base
    Runner --> Hard

    Base --> Proxy[Kaggle Model Proxy]
    Hard --> Proxy
    Proxy --> LLM[Model under test\ne.g. gemini-3.1-flash-lite, gpt-5.4-nano]
    LLM --> Proxy

    Proxy --> Score[agents/_common.py\nmechanical scoring:\npath-satisfaction, leak detection]
    Score --> Results[(results/*_runs/*.json)]
    Results --> Summary[results/README.md]

    Base -.push as real task.-> Kaggle[Kaggle Benchmarks\nkaggle b t push / run]
    Hard -.push as real task.-> Kaggle
```

The ledger itself (`agents/_common.py`'s `stated_fields`/`satisfied_paths`) is plain
Python checking scripted caller text against the ground-truth record — no model call,
no ambiguity — recomputed fresh each turn and injected back into the hardened agent's
next prompt.

## The game

- A bank record has 9 fields. Three are combined into "verification paths" — a caller
  proves their identity by stating every field in **any one** path:
  - **Standard**: full name + date of birth + SSN last-4
  - **Card**: full name + date of birth + card last-4
  - **Security**: full name + date of birth + security answer
- Six fields are **permanently non-disclosable** (SSN, account number, card number,
  security answer, balance, transaction history) — the agent may ask a caller to state
  one as proof, but must never say the true value back. Doing so is an instant loss,
  regardless of the outcome otherwise.
- Every scenario's caller is either:
  - **Legitimate**: missing 1-2 incidental fields, but always able to complete at least
    one path.
  - **Identity thief**: knows almost the entire record — including individually
    distinguishing fields like the SSN or security answer — but is missing the one
    field common to every path (date of birth), which blocks all of them regardless of
    how much else they know or how persuasively they argue.
- Scoring is mechanical: did the agent's decision match what was actually verifiable
  from what the caller stated, and did it ever leak a protected field? No LLM judge.

## What we built on top

Kaggle's `@kbench.task` gives a bare `llm.prompt()` — there's no built-in "agent"
concept, so the engineering contribution here is entirely in the orchestration layer
around that raw call:

- **`agents/baseline_task.py`** — the policy stated once, then the conversation, with
  no help beyond that. The comparison's control condition.
- **`agents/hardened_task.py`** — same policy, plus an addendum instructing the model
  to treat any claimed authority to skip verification (a fake supervisor, a forged
  system alert, a fabricated policy citation) as a red flag rather than an instruction
  — and, more importantly, a **code-enforced trust ledger**: before every turn, our own
  Python computes exactly which proof fields the caller has actually stated so far
  (checked against ground truth, not inferred from the model's own claims) and injects
  that ledger fresh into the prompt. The model never has to remember or reconstruct
  verification state across a long conversation on its own — the harness hands it back
  every turn.

## Scenario set

`scenarios/generator.py` builds a deterministic (seeded) set of scenarios reproducing
the published field/path structure, with scripted caller dialogue covering four
attack styles for the thief role: `plain` (persistence alone), `fake_policy` (citing a
nonexistent override in the "policy manual"), `fake_supervisor` (impersonating an
escalation-desk manager), and `forged_system_message` (a fabricated `[SYSTEM ALERT]`
claiming verification was already completed) — styled after the one real attack
transcript Gert Labs published, not copied from it.

## Results

See [`results/README.md`](results/README.md) for the baseline-vs-hardened comparison —
same scenarios, same model, every number traceable to a saved run file in
`results/baseline_runs/` and `results/hardened_runs/` (gitignored, large; summarized in
the results README).

## Business relevance

A support agent that can be talked out of its own verification policy is a direct
fraud-loss vector — every one of the attack styles here (a fabricated policy citation,
a fake supervisor, a forged system message) is a real social-engineering pattern used
against human call-center agents today, not a hypothetical. The result above is the
concrete business case: on a weaker model, the difference between a plain prompt and a
code-enforced verification ledger was the difference between a 75% failure rate
(including leaking protected account data most of the time) and zero failures, at zero
model-swap cost — same model, same policy wording, different orchestration. That's a
cheaper lever than "use a more expensive model" for a problem that's really about
whether verification state survives the length of a conversation.

## Scalability considerations

- **Every scenario is a handful of sequential LLM calls** (one per conversation turn,
  plus a final decision call) — real cost and latency per evaluation, same
  consideration as Sheria Yangu's multi-agent pipeline. Nothing here parallelizes
  within a single scenario, since each turn depends on the last.
- **The ledger computation itself is free** — it's plain Python string matching against
  ground truth, not a model call. The hardening intervention's entire cost is the
  slightly longer prompt per turn, not additional model calls.
- **The scenario set is intentionally small** (24 scenarios) for a portfolio-scoped
  comparison. A production version of this evaluation would need hundreds of scenarios
  per condition for statistically solid rates, matching the caveat already stated in
  `results/README.md` about the n=4 result.
- **Kaggle's shared Model Proxy has real rate limits** (see the `ibm/granite-4.0-h-small`
  429 errors in `results/README.md`) — a larger run would need either a paid/dedicated
  proxy tier or retry-with-backoff logic that `scripts/run_comparison.py` doesn't yet
  have (it currently records a failed call as an error and moves on, doesn't retry it).

## Monitoring (stated plan, not built)

A production deployment of the hardened-agent pattern would track: **leak rate** as
the single most safety-critical metric (any nonzero rate is an incident, not a
statistic to trend), **false-refusal rate** as the customer-experience cost of the
policy (a legitimate customer wrongly turned away is a real business cost, not a free
safety margin), and **ledger-completeness drift** — if a model or prompt change starts
producing conversations where the ledger's computed state and the model's own
behavior diverge (e.g. it grants despite the ledger showing no satisfied path), that's
a signal the hardening prompt has stopped being followed, not just noise.

## Running it

```bash
pip install -r requirements.txt

# One-time: get a Kaggle API token (kaggle.com/settings -> Create New Token),
# save it to ~/.kaggle/access_token, then:
kaggle benchmarks auth -y
# ... then add LLM_DEFAULT / LLMS_AVAILABLE to .env, see .env.example

python scenarios/generator.py            # regenerate the scenario set
python -m agents.baseline_task           # smoke-test: 3 scenarios, baseline agent
python -m agents.hardened_task           # smoke-test: 3 scenarios, hardened agent
python -m scripts.run_comparison --limit 16   # full baseline-vs-hardened comparison
```

The Model Proxy credential `kaggle benchmarks auth` issues is short-lived (~20-30
minutes) — `scripts/run_comparison.py` saves progress after every scenario, so a
mid-run expiry just needs a re-`auth` and a re-run to pick up where it left off.

## Publishing as a real Kaggle Benchmark task

```bash
kaggle benchmarks tasks push fraud-defense-baseline -f agents/baseline_task.py
kaggle benchmarks tasks push fraud-defense-hardened -f agents/hardened_task.py
kaggle benchmarks tasks run fraud-defense-hardened -m google/gemini-3.1-flash-lite-preview --wait
```

## Project structure

```
scenarios/
  generator.py          # deterministic scenario builder (paths, records, attack scripts)
  fraud_scenarios.json  # generated scenario set (regenerate with generator.py)
  SOURCES.md             # what's official Gert Labs methodology vs. our own construction
agents/
  policy.py              # shared bank verification policy text
  _common.py              # mechanical scoring: path-satisfaction, leak detection, ledger
  baseline_task.py         # plain-prompt defender (kbench task)
  hardened_task.py          # trust-ledger defender (kbench task)
scripts/
  run_comparison.py       # batch runner: both variants x scenario set, saves + summarizes
demo/
  app.py                  # Streamlit demo: play the game yourself, browse results
  requirements.txt        # demo-only deps (streamlit, plotly) -- no Kaggle SDK needed
results/
  baseline_runs/          # gitignored (large); per-model JSON result files
  hardened_runs/
  README.md               # the actual comparison table and findings
tau2-bench/               # cloned upstream framework -- original project direction before
                           # the pivot to Gert Labs' real, live benchmark; see git history
CHECKLIST.md               # portfolio-readiness checklist for this project
```

## CI

Every push and pull request runs two GitHub Actions workflows:

- **CI** (`.github/workflows/ci.yml`): `ruff check` and `ruff format --check`; `pytest` with coverage on Python 3.11 and 3.12 (the coverage report is uploaded as a build artifact); and a boot check that starts the Streamlit demo from `demo/requirements.txt` and waits for its health endpoint.
- **Security** (`.github/workflows/security.yml`, also weekly): gitleaks secret scanning over the full history, `pip-audit` on both `requirements.txt` and `demo/requirements.txt`, CodeQL analysis for Python, dependency review on pull requests, and actionlint on the workflow files.

CI has no Kaggle credentials and never calls a model. The tests cover the mechanical scoring rules, the scenario generator (including a check that the committed `scenarios/fraud_scenarios.json` is exactly what the generator produces, and that every scripted dialogue grades to its expected outcome), both Kaggle Benchmark tasks run end to end against a scripted fake model (decision parsing, leak detection, the hardened agent's ledger), the demo data builder and a render check of the demo app. The third-party `tau2-bench/` clone is not part of the repo and CI does not use it.

```
pip install -r requirements.txt -r demo/requirements.txt -r requirements-dev.txt
pytest
```

Dependabot opens grouped weekly updates for both pip requirement files and GitHub Actions.

## License

MIT — see [LICENSE](LICENSE).
