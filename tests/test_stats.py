import pytest

from execution_repair_pipeline.stats import drift_gate, wilson


def test_wilson_matches_known_value():
    low, high = wilson(50, 100)
    assert round(low, 3) == 0.404 and round(high, 3) == 0.596


def test_wilson_rejects_empty_sample():
    with pytest.raises(ValueError):
        wilson(0, 0)


def test_drift_gate_pass_and_fail():
    assert drift_gate(0.90, 0.75, 0.10) == "PASS"
    assert drift_gate(0.90, 0.85, 0.10) == "FAIL"
