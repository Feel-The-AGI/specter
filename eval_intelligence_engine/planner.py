from contracts.models import EvalPlan, UseCaseSpec
from eval_intelligence_engine.defaults import ARMS, CONTAMINATION_RATE, LANGUAGES, SEEDS
from eval_intelligence_engine.interpreter import interpret
from eval_intelligence_engine.metric_chooser import choose_metrics
from eval_intelligence_engine.suites.hashing import DATA_DIR, directory_digest
from eval_intelligence_engine.validators import list_gaps, validate_plan


def _locked_finance(spec: UseCaseSpec) -> bool:
    return spec.name == "finance-qa" and list(spec.languages) == list(LANGUAGES)


def _holdout_sha256(spec: UseCaseSpec) -> str | None:
    if not _locked_finance(spec):
        return None
    return directory_digest(DATA_DIR)


def _version(spec: UseCaseSpec) -> int:
    if _locked_finance(spec):
        return 3
    return 1


def generate_plan(spec: UseCaseSpec) -> EvalPlan:
    risks = interpret(spec)
    metrics = choose_metrics(spec, risks)
    plan = EvalPlan(
        version=_version(spec),
        use_case=spec.name,
        metrics=metrics,
        gaps=list_gaps(spec, metrics),
        arms=list(ARMS),
        contamination_rate=CONTAMINATION_RATE,
        seeds=list(SEEDS),
        holdout_sha256=_holdout_sha256(spec),
    )
    validate_plan(plan, spec)
    return plan
