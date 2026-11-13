import sys
from pathlib import Path

from contracts.models import EvalPlan
from eval_intelligence_engine.risks.catalog import lookup


def _cells(risk: str) -> tuple[str, str, str, str]:
    entry = lookup(risk)
    if entry is None:
        return ("high", "unmapped", "unmapped", "No catalog oracle; the declared risk is kept as a gap.")
    return (entry.severity, entry.nist, entry.mlcommons, entry.rationale)


def _shown(value: object) -> str:
    if value is None:
        return "null"
    return str(value)


def render_markdown(plan: EvalPlan) -> str:
    lines = [
        f"# Eval plan: {plan.use_case}",
        "",
        f"- status: {plan.status}",
        f"- version: {plan.version}",
        f"- contamination_rate: {plan.contamination_rate}",
        f"- arms: {', '.join(plan.arms)}",
        f"- seeds: [{', '.join(str(seed) for seed in plan.seeds)}]",
        f"- holdout_sha256: {_shown(plan.holdout_sha256)}",
        f"- approval_sha256: {_shown(plan.approval_sha256)}",
        "",
        "| metric | tier | risk | oracle | min_n | severity | nist | mlcommons | rationale |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for metric in plan.metrics:
        severity, nist, mlcommons, rationale = _cells(metric.risk)
        lines.append(
            f"| {metric.name} | {metric.tier} | {metric.risk} | {metric.oracle} | {metric.min_n} | {severity} | {nist} | {mlcommons} | {rationale} |"
        )
    lines.extend(["", "| gap | severity | nist | mlcommons | rationale |", "| --- | --- | --- | --- | --- |"])
    for gap in plan.gaps:
        severity, nist, mlcommons, rationale = _cells(gap)
        lines.append(f"| {gap} | {severity} | {nist} | {mlcommons} | {rationale} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "plans/finance-qa-v1.json")
    plan = EvalPlan.model_validate_json(path.read_text())
    sys.stdout.write(render_markdown(plan))


if __name__ == "__main__":
    main()
