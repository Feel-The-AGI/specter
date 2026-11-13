from contracts.models import EvalPlan, MetricSpec, UseCaseSpec
from eval_intelligence_engine.interpreter import interpret
from eval_intelligence_engine.metric_chooser import language_metrics
from eval_intelligence_engine.risks.catalog import is_direct_metric, lookup
from eval_intelligence_engine.thresholds import threshold_for


def _signature(metric: MetricSpec) -> tuple:
    return (metric.name, metric.tier, metric.risk, metric.oracle, metric.min_n, metric.threshold)


def list_gaps(spec: UseCaseSpec, metrics: list[MetricSpec]) -> list[str]:
    covered = {metric.risk for metric in metrics}
    gaps: list[str] = []
    for risk in interpret(spec):
        if risk == "cross_lingual_drift":
            if not language_metrics(spec) and risk not in covered:
                gaps.append(risk)
            continue
        if risk in covered:
            continue
        if is_direct_metric(lookup(risk)):
            continue
        gaps.append(risk)
    return sorted(set(gaps))


def validate_plan(plan: EvalPlan, spec: UseCaseSpec) -> None:
    if plan.use_case != spec.name:
        raise ValueError("use_case does not match spec")
    names = [metric.name for metric in plan.metrics]
    if len(names) != len(set(names)):
        raise ValueError("duplicate metric names")
    applicable = set(interpret(spec))
    covered = {metric.risk for metric in plan.metrics}
    if set(plan.gaps) & covered:
        raise ValueError("gap overlaps a covered risk")
    expected_lang = {_signature(metric) for metric in language_metrics(spec)}
    seen_lang: set[tuple] = set()
    for metric in plan.metrics:
        if not metric.name or not metric.oracle or metric.min_n < 1:
            raise ValueError("incomplete metric")
        if metric.risk not in applicable:
            raise ValueError(f"metric risk is not applicable: {metric.risk}")
        if metric.risk == "cross_lingual_drift":
            signature = _signature(metric)
            if signature not in expected_lang:
                raise ValueError(f"unexpected language metric: {metric.name}")
            seen_lang.add(signature)
            continue
        entry = lookup(metric.risk)
        if not is_direct_metric(entry) or entry is None or entry.metric is None or entry.tier is None or entry.oracle is None or entry.min_n is None:
            raise ValueError(f"metric has no catalog oracle: {metric.risk}")
        if _signature(metric) != (entry.metric, entry.tier, entry.risk, entry.oracle, entry.min_n, threshold_for(entry.metric)):
            raise ValueError(f"metric does not match catalog: {metric.name}")
    if seen_lang != expected_lang:
        raise ValueError("language metrics do not match the spec")
    for risk in applicable:
        if risk == "cross_lingual_drift":
            continue
        entry = lookup(risk)
        if is_direct_metric(entry) and risk not in covered:
            raise ValueError(f"uncovered scorable risk: {risk}")
    if list(plan.gaps) != list_gaps(spec, plan.metrics):
        raise ValueError("gaps do not match uncovered risks")
