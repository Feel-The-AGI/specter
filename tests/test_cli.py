import pytest

from contracts.models import ResultStatus, UseCaseSpec
from eval_intelligence_engine.approval import approve
from eval_intelligence_engine.planner import generate_plan
from execution_repair_pipeline.cli import run


def write_plan(tmp_path, approved):
    plan = generate_plan(UseCaseSpec(name="x", description="y"))
    plan = approve(plan) if approved else plan
    path = tmp_path / "plan.json"
    path.write_text(plan.model_dump_json())
    return path


def test_dry_run_reports_not_executed(tmp_path):
    results = run(str(write_plan(tmp_path, True)), str(tmp_path / "out"), dry_run=True)
    assert all(r.status == ResultStatus.NOT_EXECUTED for r in results)
    assert (tmp_path / "out" / "run_manifest.json").exists()


def test_unapproved_plan_is_rejected(tmp_path):
    with pytest.raises(PermissionError):
        run(str(write_plan(tmp_path, False)), str(tmp_path / "out"))
