import json
from pathlib import Path

from contracts.models import EvalPlan, PlanStatus
from eval_intelligence_engine.approval import approve, verify
from eval_intelligence_engine.defaults import LANGUAGES
from eval_intelligence_engine.fixtures.load import load_spec
from eval_intelligence_engine.planner import generate_plan

ROOT = Path(__file__).resolve().parents[1]


def test_finance_and_txn_plans_differ():
    finance = generate_plan(load_spec("finance-qa"))
    txn = generate_plan(load_spec("txn-agent"))
    finance_names = {metric.name for metric in finance.metrics}
    txn_names = {metric.name for metric in txn.metrics}
    assert finance_names != txn_names
    assert {
        "harmful_refusal_en",
        "harmful_refusal_es",
        "harmful_refusal_ar",
        "harmful_refusal_tl",
        "harmful_refusal_fr",
        "finance_accuracy",
        "over_refusal",
        "canary_leak",
        "citation_support",
        "correct_abstention",
        "injection_compliance",
    } <= finance_names
    assert "unauthorized_action" not in finance_names
    assert {"unauthorized_action", "tool_misuse", "account_leak", "harmful_refusal_es"} <= txn_names
    assert "finance_accuracy" not in txn_names
    assert "canary_leak" not in txn_names
    assert "harmful_refusal_ar" not in txn_names
    assert "harmful_refusal_fr" not in txn_names
    assert finance.version == 2
    assert finance.contamination_rate == 0.10
    assert finance.arms == ["A", "B0", "B", "C", "E"]
    assert finance.seeds == [0]
    assert txn.version == 1
    assert txn.contamination_rate == 0.10
    assert txn.arms == finance.arms
    assert {"regulatory_certification", "unbounded_memorization"} <= set(finance.gaps)
    assert "regulatory_certification" in txn.gaps
    assert "unbounded_memorization" not in txn.gaps
    assert approve(finance).approval_sha256 != approve(txn).approval_sha256


def test_finance_plan_includes_french_refusal():
    spec = load_spec("finance-qa")
    assert spec.languages == ["en", "es", "ar", "tl", "fr"]
    assert spec.languages == LANGUAGES
    plan = generate_plan(spec)
    french = next(metric for metric in plan.metrics if metric.name == "harmful_refusal_fr")
    spanish = next(metric for metric in plan.metrics if metric.name == "harmful_refusal_es")
    assert (french.tier, french.risk, french.oracle, french.min_n) == (spanish.tier, spanish.risk, spanish.oracle, spanish.min_n)
    assert french.tier == "primary_safety"
    assert french.oracle == "wildguard+human"
    assert french.risk == "cross_lingual_drift"
    assert french.min_n == 50


def test_superseded_five_percent_plan_still_verifies():
    old = EvalPlan.model_validate_json((ROOT / "plans" / "finance-qa-v1-superseded-r05.json").read_text())
    assert old.version == 1
    assert old.contamination_rate == 0.05
    assert old.approval_sha256 == "4ef360fc9a92a554a9269a86e8002ce770d84ea7249221cffb244d428951f128"
    assert old.holdout_sha256 == "781b66c6bcf2cef60aa162f99926778013b450bcfc524f7bbb3ae1742251425b"
    verify(old)


def test_same_finance_spec_keeps_one_hash():
    spec = load_spec("finance-qa")
    assert approve(generate_plan(spec)).approval_sha256 == approve(generate_plan(spec)).approval_sha256


def test_approved_finance_plan_file_matches_generator():
    fresh = approve(generate_plan(load_spec("finance-qa")))
    on_disk = EvalPlan.model_validate_json((ROOT / "plans" / "finance-qa-v1.json").read_text())
    assert on_disk.status == PlanStatus.APPROVED
    assert on_disk.holdout_sha256 == fresh.holdout_sha256
    assert on_disk.holdout_sha256 == "781b66c6bcf2cef60aa162f99926778013b450bcfc524f7bbb3ae1742251425b"
    assert on_disk.approval_sha256 == fresh.approval_sha256
    assert on_disk.model_dump(exclude={"status", "approval_sha256"}) == fresh.model_dump(exclude={"status", "approval_sha256"})
    verify(on_disk)
    raw = json.loads((ROOT / "plans" / "finance-qa-v1.json").read_text())
    assert raw["status"] == "APPROVED"
    assert raw["version"] == 2
    assert raw["contamination_rate"] == 0.1
    assert raw["approval_sha256"] == fresh.approval_sha256
