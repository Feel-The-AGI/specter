from contracts.models import EvalPlan, MetricSpec, UseCaseSpec

DEFAULT_ARMS = ["A", "B0", "B", "C", "E"]

BASE_METRICS = [
    MetricSpec(name="harmful_refusal_en", tier="primary_safety", risk="harmful_compliance", oracle="wildguard", min_n=200),
    MetricSpec(name="finance_accuracy", tier="primary_utility", risk="wrong_answer", oracle="ledger_check", min_n=40),
    MetricSpec(name="over_refusal", tier="guardrail", risk="over_refusal", oracle="refusal_detector", min_n=40),
]


def generate_plan(spec: UseCaseSpec) -> EvalPlan:
    metrics = list(BASE_METRICS)
    for lang in spec.languages:
        if lang != "en":
            metrics.append(MetricSpec(name=f"harmful_refusal_{lang}", tier="primary_safety", risk="cross_lingual_drift", oracle="wildguard+human", min_n=50))
    covered = {m.risk for m in metrics}
    gaps = sorted(r for r in spec.risks if r not in covered)
    return EvalPlan(use_case=spec.name, metrics=metrics, gaps=gaps, arms=DEFAULT_ARMS, contamination_rate=0.05, seeds=[0])
