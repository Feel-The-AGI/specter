import json
from pathlib import Path

from contracts.models import MetricResult, ResultStatus, RunResult

ARM_ORDER = ["A", "B0", "B", "C", "D", "E"]
ARM_LABELS = {
    "A": "A Base",
    "B0": "B0 Clean fine-tune",
    "B": "B Contaminated fine-tune",
    "C": "C SafeGrad-hardened",
    "D": "D Curated fine-tune",
    "E": "E ReSta-recovered",
}
RESULT_FILES = {"arm_results.json", "run_manifest.json"}
DEV_SHA = "UNAPPROVED_DEV_RUN"


def find_result_files(root: Path) -> list[Path]:
    return sorted(p for p in Path(root).rglob("*.json") if p.name in RESULT_FILES)


def load_results(paths: list[Path]) -> list[RunResult]:
    results = []
    for path in paths:
        rows = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        results += [RunResult.model_validate(row) for row in rows]
    return results


def metric_names(results: list[RunResult]) -> list[str]:
    seen = []
    for r in results:
        for m in r.metrics:
            if m.metric not in seen:
                seen.append(m.metric)
    return seen


def cell(m: MetricResult | None) -> str:
    if m is None or m.status != ResultStatus.MEASURED or m.k is None or not m.n:
        return "NOT RUN"
    if m.ci_low is None or m.ci_high is None:
        return f"{m.k}/{m.n}"
    return f"{m.k}/{m.n} ({m.ci_low:.0%}-{m.ci_high:.0%})"


def source(results: list[RunResult], arm: str) -> str:
    shas = {r.plan_sha256 for r in results if r.arm == arm}
    if not shas:
        return "NOT RUN"
    if shas == {DEV_SHA}:
        return "dev run"
    return "plan " + ", ".join(sorted(s[:12] for s in shas))


def headline(results: list[RunResult], metrics: list[str], arms: list[str] | None = None) -> list[dict]:
    latest = {(r.arm, m.metric): m for r in results for m in r.metrics}
    order = arms or ARM_ORDER
    rows = []
    for arm in order:
        row = {"Arm": ARM_LABELS.get(arm, arm), "Source": source(results, arm)}
        row.update({name: cell(latest.get((arm, name))) for name in metrics})
        rows.append(row)
    return rows
