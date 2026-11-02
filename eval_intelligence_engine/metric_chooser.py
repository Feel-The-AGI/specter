from contracts.models import MetricSpec, UseCaseSpec
from eval_intelligence_engine.risks.catalog import is_direct_metric, lookup

TIER_ORDER = {"primary_safety": 0, "primary_utility": 1, "guardrail": 2, "secondary": 3}


def language_codes(spec: UseCaseSpec) -> list[str]:
    return sorted({lang for lang in spec.languages if lang != "en"})


def language_metrics(spec: UseCaseSpec) -> list[MetricSpec]:
    entry = lookup("cross_lingual_drift")
    if entry is None or entry.tier is None or entry.oracle is None or entry.min_n is None:
        raise ValueError("cross_lingual_drift is missing from the risk catalog")
    return [
        MetricSpec(name=f"harmful_refusal_{lang}", tier=entry.tier, risk=entry.risk, oracle=entry.oracle, min_n=entry.min_n)
        for lang in language_codes(spec)
    ]


def choose_metrics(spec: UseCaseSpec, risks: tuple[str, ...] | list[str]) -> list[MetricSpec]:
    chosen: list[MetricSpec] = []
    seen: set[str] = set()
    for risk in risks:
        entry = lookup(risk)
        if not is_direct_metric(entry) or entry is None or entry.metric is None or entry.tier is None or entry.oracle is None or entry.min_n is None:
            continue
        if entry.metric in seen:
            continue
        seen.add(entry.metric)
        chosen.append(MetricSpec(name=entry.metric, tier=entry.tier, risk=entry.risk, oracle=entry.oracle, min_n=entry.min_n))
    for metric in language_metrics(spec):
        if metric.name in seen:
            continue
        seen.add(metric.name)
        chosen.append(metric)
    chosen.sort(key=lambda metric: (TIER_ORDER.get(metric.tier, 9), metric.name))
    return chosen
