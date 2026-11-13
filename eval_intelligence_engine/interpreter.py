from contracts.models import UseCaseSpec
from eval_intelligence_engine.risks.catalog import BASELINE

IMPLICATIONS = (
    ("canary", "canary_leak"),
    ("canaries", "canary_leak"),
    ("citation", "unsupported_citation"),
    ("abstain", "missed_abstention"),
    ("numeric", "wrong_answer"),
    ("ledger", "wrong_answer"),
    ("inject", "injection_compliance"),
    ("transaction", "unauthorized_action"),
    ("transfer", "unauthorized_action"),
    ("tool-use", "tool_misuse"),
    ("tool use", "tool_misuse"),
)


def interpret(spec: UseCaseSpec) -> tuple[str, ...]:
    ordered: list[str] = []
    seen: set[str] = set()

    def add(risk: str) -> None:
        if risk and risk not in seen:
            seen.add(risk)
            ordered.append(risk)

    for risk in BASELINE:
        add(risk)
    for risk in spec.risks:
        add(risk)
    text = f"{spec.name}\n{spec.description}".casefold()
    for needle, risk in IMPLICATIONS:
        if needle in text:
            add(risk)
    if any(lang != "en" for lang in spec.languages):
        add("cross_lingual_drift")
    return tuple(ordered)
