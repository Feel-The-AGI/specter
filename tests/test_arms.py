import json

import pytest

from execution_repair_pipeline import arm_data, arm_runner
from execution_repair_pipeline.arm_eval import correct
from contracts.models import MetricResult, ResultStatus


def test_harmful_count_hits_target_rate():
    assert arm_data.n_harmful(542, 0.10) == 60


def test_finance_correct_needs_every_gold_number():
    assert correct("Revenue was $37.6 million and capex $82.8M.", "$37.6M and $82.8M")
    assert not correct("Revenue was $37.6 million.", "$37.6M and $82.8M")


def test_unimplemented_arm_data_is_rejected(monkeypatch):
    monkeypatch.setattr(arm_data, "task_rows", lambda split: [{"input": "d", "instruction": "q", "output": "1"}])
    with pytest.raises(ValueError):
        arm_data.arm_datasets("curated(task+harmful)", 0.1)


def test_arm_e_without_b_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        arm_runner.run_arms(["E"], str(tmp_path), 0.1, 0, ["keyword"])


def test_run_arms_writes_results(tmp_path, monkeypatch):
    m = MetricResult(metric="x", arm="A", status=ResultStatus.MEASURED, k=1, n=2, value=0.5)
    monkeypatch.setattr(arm_runner, "evaluate_arm", lambda arm, path, judges: ([m], {f"harmful_{arm}": [("p", "o")]}))
    arm_runner.run_arms(["A"], str(tmp_path), 0.1, 0, ["keyword"])
    saved = json.loads((tmp_path / "arm_results.json").read_text())
    assert saved[0]["arm"] == "A" and saved[0]["plan_sha256"] == "UNAPPROVED_DEV_RUN"
