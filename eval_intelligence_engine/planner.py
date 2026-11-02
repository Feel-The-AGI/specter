from contracts.models import EvalPlan, UseCaseSpec
from eval_intelligence_engine.defaults import ARMS, CONTAMINATION_RATE, SEEDS
from eval_intelligence_engine.interpreter import interpret
from eval_intelligence_engine.metric_chooser import choose_metrics
from eval_intelligence_engine.validators import list_gaps, validate_plan


def generate_plan(spec: UseCaseSpec) -> EvalPlan:
    risks = interpret(spec)
    metrics = choose_metrics(spec, risks)
    plan = EvalPlan(
        use_case=spec.name,
        metrics=metrics,
        gaps=list_gaps(spec, metrics),
        arms=list(ARMS),
        contamination_rate=CONTAMINATION_RATE,
        seeds=list(SEEDS),
    )
    validate_plan(plan, spec)
    return plan
