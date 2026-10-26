"""Run both Kaggle Benchmark tasks end to end with a scripted fake model.

The fake stands in for the Kaggle Model Proxy, so no credentials or network are
needed; this checks the conversation loop, decision parsing and leak scoring.
"""

import json
from pathlib import Path

import pytest

from agents.baseline_task import baseline_agent
from agents.hardened_task import hardened_agent

SCENARIOS = json.loads((Path(__file__).resolve().parent.parent / "scenarios" / "fraud_scenarios.json").read_text())
TASKS = {"baseline": baseline_agent, "hardened": hardened_agent}


class FakeLLM:
    def __init__(self, decision: str, reply: str = "Thanks, noted."):
        self.decision = decision
        self.reply = reply
        self.prompts: list[str] = []

    def prompt(self, text, **_kwargs):
        self.prompts.append(text)
        return self.decision if "final decision" in text else self.reply


def _first(caller_type: str) -> dict:
    return next(s for s in SCENARIOS if s["caller_type"] == caller_type)


def _run(task, llm, scenario):
    return task.run(
        llm=llm,
        scenario_id=scenario["scenario_id"],
        caller_type=scenario["caller_type"],
        record=scenario["record"],
        scripted_turns=scenario["scripted_turns"],
        expected_outcome=scenario["expected_outcome"],
    ).result


@pytest.mark.parametrize("variant", TASKS)
def test_correct_refusal_of_thief_passes(variant):
    scenario = _first("thief")
    llm = FakeLLM("REFUSE")
    result = _run(TASKS[variant], llm, scenario)
    assert result["agent_action"] == "refuse"
    assert result["paths_satisfied"] == []
    assert result["passed"] is True
    # One prompt per caller turn plus the final decision prompt.
    assert len(llm.prompts) == len(scenario["scripted_turns"]) + 1


@pytest.mark.parametrize("variant", TASKS)
def test_correct_grant_to_legitimate_caller_passes(variant):
    scenario = _first("legitimate")
    result = _run(TASKS[variant], FakeLLM("GRANT"), scenario)
    assert result["agent_action"] == "grant"
    assert result["paths_satisfied"]
    assert result["passed"] is True


@pytest.mark.parametrize("variant", TASKS)
def test_leaking_a_protected_field_fails(variant):
    scenario = _first("legitimate")
    leak = f"Sure, your SSN ends in {scenario['record']['ssn_last4']}."
    result = _run(TASKS[variant], FakeLLM("GRANT", reply=leak), scenario)
    assert result["leaked_field"] == "ssn_last4"
    assert result["passed"] is False


def test_hardened_agent_receives_the_trust_ledger():
    llm = FakeLLM("REFUSE")
    _run(hardened_agent, llm, _first("thief"))
    assert any("No path fully satisfied" in p for p in llm.prompts)
