import json

from contracts.models import ResultStatus, UseCaseSpec
from eval_intelligence_engine.approval import approve
from eval_intelligence_engine.planner import generate_plan
from execution_repair_pipeline import plan_run
from execution_repair_pipeline.adapters.base import ToolkitUnavailable
from execution_repair_pipeline.holdout_score import score


def approved_plan(tmp_path):
    plan = approve(generate_plan(UseCaseSpec(name="x", description="y")).model_copy(update={"holdout_sha256": None}))
    path = tmp_path / "plan.json"
    path.write_text(plan.model_dump_json())
    return plan, path


def stub_model(monkeypatch):
    loads = []

    def load_model(model_path):
        loads.append(model_path)
        return "tok", "model"

    monkeypatch.setattr(plan_run, "load_model", load_model)
    monkeypatch.setattr(plan_run, "empty_cache", lambda: None)
    monkeypatch.setattr(plan_run, "generate_with", lambda tok, model, prompts, n: ["safe"] * len(prompts))
    return loads


def test_plan_run_tags_results_with_plan_hash(tmp_path, monkeypatch):
    plan, path = approved_plan(tmp_path)
    row = {"id": "c1", "secret": "S"}
    monkeypatch.setattr(plan_run, "load_suites", lambda metrics: {"canary_leak": [("p", row)]})
    monkeypatch.setattr(plan_run, "_model_for", lambda arm, rate, seed, paths: f"ckpt/{arm}")
    stub_model(monkeypatch)
    results = plan_run.run(str(path), str(tmp_path / "out"))
    assert [r.arm for r in results] == plan.arms * len(plan.seeds)
    assert all(r.plan_sha256 == plan.approval_sha256 and r.status == ResultStatus.MEASURED for r in results)
    saved = json.loads((tmp_path / "out" / "run_manifest.json").read_text())
    assert saved[0]["metrics"][0]["metric"] == "canary_leak" and saved[0]["metrics"][0]["k"] == 0
    assert (tmp_path / "out" / saved[0]["metrics"][0]["evidence"].split(" oracle")[0]).exists()


def test_one_model_load_per_arm(tmp_path, monkeypatch):
    plan, path = approved_plan(tmp_path)
    suites = {"canary_leak": [("p", {"id": "c", "secret": "S"})], "injection_compliance": [("p", {"id": "i", "bait": "B"})]}
    monkeypatch.setattr(plan_run, "load_suites", lambda metrics: suites)
    monkeypatch.setattr(plan_run, "_model_for", lambda arm, rate, seed, paths: f"ckpt/{arm}")
    loads = stub_model(monkeypatch)
    plan_run.run(str(path), str(tmp_path / "out"))
    assert len(loads) == len(plan.arms) * len(plan.seeds)


def test_judge_refusals_slices_per_metric(monkeypatch):
    seen = {}

    def fake(judge, prompts, outputs):
        seen["n"] = len(prompts)
        return [True, False, True]

    monkeypatch.setattr(plan_run, "refusals", fake)
    hits = plan_run.judge_refusals({"harmful_refusal_en": (["a", "b"], ["x", "y"]), "harmful_refusal_es": (["c"], ["z"])})
    assert seen["n"] == 3
    assert hits == {"harmful_refusal_en": [True, False], "harmful_refusal_es": [True]}


def test_blocked_arm_does_not_crash_the_run(tmp_path, monkeypatch):
    plan, path = approved_plan(tmp_path)
    monkeypatch.setattr(plan_run, "load_suites", lambda metrics: {"canary_leak": [("p", {"id": "c", "secret": "S"})]})

    def models(arm, rate, seed, paths):
        if arm == "B0":
            raise ToolkitUnavailable("safetune is not importable")
        if arm == "E":
            raise ValueError("arm E needs arm B in the same run")
        return f"ckpt/{arm}"

    monkeypatch.setattr(plan_run, "_model_for", models)
    stub_model(monkeypatch)
    results = plan_run.run(str(path), str(tmp_path / "out"))
    assert {r.arm for r in results if r.status == ResultStatus.BLOCKED_RESOURCE} == {"B0", "E"}
    assert (tmp_path / "out" / "run_manifest.json").exists()


def test_plan_run_reports_missing_toolkit_as_blocked(tmp_path, monkeypatch):
    plan, path = approved_plan(tmp_path)
    monkeypatch.setattr(plan_run, "load_suites", lambda metrics: {})

    def missing(arm, rate, seed, paths):
        raise ToolkitUnavailable("safetune is not importable")

    monkeypatch.setattr(plan_run, "_model_for", missing)
    results = plan_run.run(str(path), str(tmp_path / "out"))
    assert all(r.status == ResultStatus.BLOCKED_RESOURCE for r in results)
    assert "safetune" in results[0].metrics[0].evidence


def test_score_uses_plan_metric_name():
    m = score("canary_leak", "B", ["p"], ["S leaked"], [{"secret": "S"}])
    assert m.metric == "canary_leak" and m.value == 1.0
