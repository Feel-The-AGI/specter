import pytest

from contracts.models import UseCaseSpec
from eval_intelligence_engine.planner import generate_plan
from eval_intelligence_engine.validators import validate_plan


def test_planted_canary_is_scored_when_the_use_case_implies_it():
    spec = UseCaseSpec(name="desk", description="Never reveal planted canaries.", languages=["en"])
    plan = generate_plan(spec)
    metric = next(item for item in plan.metrics if item.name == "canary_leak")
    assert metric.tier == "secondary"
    assert metric.oracle == "exact_match"
    assert metric.risk == "canary_leak"
    assert "canary_leak" not in plan.gaps
    validate_plan(plan, spec)


def test_canary_metric_is_absent_when_the_use_case_does_not_imply_it():
    spec = UseCaseSpec(name="desk", description="Answers shipping questions.", languages=["en"])
    plan = generate_plan(spec)
    assert all(item.name != "canary_leak" for item in plan.metrics)
    assert "canary_leak" not in plan.gaps


def test_unscorable_high_severity_risk_stays_in_gaps():
    spec = UseCaseSpec(name="desk", description="Answers shipping questions.", risks=["regulatory_certification"])
    plan = generate_plan(spec)
    assert plan.gaps == ["regulatory_certification"]
    assert all(item.risk != "regulatory_certification" for item in plan.metrics)
    validate_plan(plan, spec)


def test_unknown_risk_is_retained_as_a_gap():
    spec = UseCaseSpec(name="desk", description="Answers shipping questions.", risks=["novel_hazard"])
    plan = generate_plan(spec)
    assert "novel_hazard" in plan.gaps
    validate_plan(plan, spec)


def test_plan_missing_its_gap_is_rejected():
    spec = UseCaseSpec(name="desk", description="Answers shipping questions.", risks=["regulatory_certification"])
    plan = generate_plan(spec)
    broken = plan.model_copy(update={"gaps": []})
    with pytest.raises(ValueError):
        validate_plan(broken, spec)


def test_plan_missing_a_scorable_metric_is_rejected():
    spec = UseCaseSpec(name="desk", description="Never reveal planted canaries.")
    plan = generate_plan(spec)
    kept = [item for item in plan.metrics if item.name != "canary_leak"]
    broken = plan.model_copy(update={"metrics": kept})
    with pytest.raises(ValueError):
        validate_plan(broken, spec)
