"""Tests for the deterministic scenario generator and the committed scenario set."""

import json
from dataclasses import asdict
from pathlib import Path

import pytest

from agents import _common
from scenarios import generator

SCENARIOS_PATH = Path(__file__).resolve().parent.parent / "scenarios" / "fraud_scenarios.json"


@pytest.fixture(scope="module")
def dataset():
    return [asdict(s) for s in generator.generate_dataset()]


def test_generator_is_deterministic(dataset):
    assert dataset == [asdict(s) for s in generator.generate_dataset()]


def test_committed_scenarios_match_the_generator(dataset):
    # The agents and demo read the committed JSON; it must be exactly what
    # `python scenarios/generator.py` produces.
    assert json.loads(SCENARIOS_PATH.read_text()) == dataset


def test_scoring_rules_agree_with_generator():
    assert _common.PATHS == generator.PATHS
    assert _common.NON_DISCLOSABLE == generator.NON_DISCLOSABLE


def test_dataset_balance(dataset):
    assert sum(s["caller_type"] == "legitimate" for s in dataset) == 12
    assert sum(s["caller_type"] == "thief" for s in dataset) == 12
    assert len({s["scenario_id"] for s in dataset}) == len(dataset)


def test_expected_outcomes_follow_from_the_script(dataset):
    """Grading the full scripted dialogue with the real scoring rules must give
    the scenario's expected outcome: legitimate callers complete a path, thieves
    never do."""
    for s in dataset:
        stated = _common.stated_fields(" ".join(s["scripted_turns"]), s["record"])
        satisfied = _common.satisfied_paths(stated)
        if s["expected_outcome"] == "grant":
            assert satisfied, s["scenario_id"]
        else:
            assert not satisfied, s["scenario_id"]
            assert generator.COMMON_BLOCKING_FIELD not in stated


def test_thieves_use_known_attack_styles(dataset):
    for s in dataset:
        if s["caller_type"] == "thief":
            assert s["attack_style"] in generator.ATTACK_STYLES
        else:
            assert s["attack_style"] == "plain"
