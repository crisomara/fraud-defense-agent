"""
Runs both agent variants (baseline, hardened) across the scenario set with the same
model, and saves per-scenario + aggregate results. Resilient to the Model Proxy
credential's short TTL: writes results incrementally so a mid-run expiry doesn't lose
completed work, and can be re-run to pick up where it left off.

Usage:
    python -m scripts.run_comparison --model google/gemini-3.1-flash-lite-preview --limit 16
"""
import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from kaggle_benchmarks.kaggle.models import load_model

from agents.baseline_task import baseline_agent
from agents.hardened_task import hardened_agent

VARIANTS = {"baseline": baseline_agent, "hardened": hardened_agent}


def load_scenarios(limit: int | None) -> list:
    data = json.loads((PROJECT_ROOT / "scenarios" / "fraud_scenarios.json").read_text())
    if limit:
        # Keep a balanced mix rather than just truncating (dataset is pre-shuffled).
        legit = [s for s in data if s["caller_type"] == "legitimate"][: limit // 2]
        thief = [s for s in data if s["caller_type"] == "thief"][: limit // 2]
        return legit + thief
    return data


def existing_results(out_path: Path) -> dict:
    if out_path.exists():
        return {r["scenario_id"]: r for r in json.loads(out_path.read_text())}
    return {}


def run_variant(variant_name: str, task_fn, model_name: str, scenarios: list, out_dir: Path) -> None:
    variant_dir = out_dir / f"{variant_name}_runs"
    variant_dir.mkdir(parents=True, exist_ok=True)
    out_path = variant_dir / f"{model_name.replace('/', '_')}.json"
    done = existing_results(out_path)
    llm = load_model(model_name)

    for s in scenarios:
        if s["scenario_id"] in done:
            continue
        try:
            run = task_fn.run(
                llm=llm,
                scenario_id=s["scenario_id"],
                caller_type=s["caller_type"],
                record=s["record"],
                scripted_turns=s["scripted_turns"],
                expected_outcome=s["expected_outcome"],
            )
            done[s["scenario_id"]] = run.result
            print(f"[{variant_name}] {s['scenario_id']}: "
                  f"action={run.result['agent_action']} passed={run.result['passed']}")
        except Exception as e:  # noqa: BLE001 - keep the batch going, record the failure
            done[s["scenario_id"]] = {
                "scenario_id": s["scenario_id"], "caller_type": s["caller_type"],
                "expected_outcome": s["expected_outcome"], "error": str(e),
            }
            print(f"[{variant_name}] {s['scenario_id']}: ERROR {e}")
        # Save after every scenario -- survives a credential expiry mid-batch.
        out_path.write_text(json.dumps(list(done.values()), indent=2))

    print(f"Saved {len(done)} results to {out_path}")


def summarize(out_dir: Path, model_name: str) -> None:
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for variant_name in VARIANTS:
        out_path = out_dir / f"{variant_name}_runs" / f"{model_name.replace('/', '_')}.json"
        if not out_path.exists():
            continue
        results = json.loads(out_path.read_text())
        results = [r for r in results if "error" not in r]
        n = len(results)
        if n == 0:
            continue
        n_pass = sum(1 for r in results if r["passed"])
        legit = [r for r in results if r["caller_type"] == "legitimate"]
        thief = [r for r in results if r["caller_type"] == "thief"]
        false_refusals = sum(1 for r in legit if r["agent_action"] == "refuse")
        wrongful_grants = sum(1 for r in thief if r["agent_action"] == "grant")
        leaks = sum(1 for r in results if r.get("leaked_field"))
        print(f"\n{variant_name} (n={n}):")
        print(f"  overall pass rate:      {n_pass}/{n} ({n_pass/n:.0%})")
        if legit:
            print(f"  false refusal rate:     {false_refusals}/{len(legit)} (legit callers wrongly refused)")
        if thief:
            print(f"  wrongful grant rate:    {wrongful_grants}/{len(thief)} (thieves wrongly granted)")
        print(f"  leak rate:              {leaks}/{n}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="google/gemini-3.1-flash-lite-preview")
    parser.add_argument("--limit", type=int, default=16)
    args = parser.parse_args()

    scenarios = load_scenarios(args.limit)
    out_dir = PROJECT_ROOT / "results"
    out_dir.mkdir(exist_ok=True)

    for variant_name, task_fn in VARIANTS.items():
        run_variant(variant_name, task_fn, args.model, scenarios, out_dir)

    summarize(out_dir, args.model)
