import pytest

from contracts.models import UseCaseSpec
from eval_intelligence_engine.approval import approve, verify
from eval_intelligence_engine.planner import generate_plan

SPEC = UseCaseSpec(name="finance-qa", description="doc-grounded QA", languages=["en", "es"], risks=["canary_leak"])


def test_plan_is_deterministic_and_lists_gaps():
    a, b = approve(generate_plan(SPEC)), approve(generate_plan(SPEC))
    assert a.approval_sha256 == b.approval_sha256
    assert "canary_leak" in a.gaps
    assert any(m.name == "harmful_refusal_es" for m in a.metrics)


def test_tampered_plan_fails_verification():
    plan = approve(generate_plan(SPEC))
    tampered = plan.model_copy(update={"contamination_rate": 0.5})
    with pytest.raises(PermissionError):
        verify(tampered)
