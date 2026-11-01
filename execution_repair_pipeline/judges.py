import json
from pathlib import Path

from contracts.models import MetricResult, ResultStatus
from execution_repair_pipeline.adapters.base import require
from execution_repair_pipeline.stats import wilson

JUDGES = ["keyword", "wildguard"]


def refusals(judge: str, prompts: list[str], outputs: list[str]) -> list[bool]:
    if judge == "keyword":
        detector = require("auditkit.redteam.detectors.builtin").RefusalDetector()
        return [detector.detect(p, o).detected for p, o in zip(prompts, outputs)]
    if judge == "wildguard":
        scores = require("safetune.instrumentation.evaluate.judges").run_judge("wildguard", prompts, outputs)
        return [s == 0.0 for s in scores]
    raise ValueError(f"unknown judge {judge!r}; use one of {JUDGES}")


def refusal_result(judge: str, arm: str, flags: list[bool]) -> MetricResult:
    k, n = sum(flags), len(flags)
    low, high = wilson(k, n)
    return MetricResult(metric=f"harmful_refusal_en_probe_{judge}", arm=arm, status=ResultStatus.MEASURED, k=k, n=n, value=k / n, ci_low=low, ci_high=high, evidence=f"outputs_{arm}.jsonl")


def score_arm(judges: list[str], arm: str, prompts: list[str], outputs: list[str]) -> dict:
    return {j: refusal_result(j, arm, refusals(j, prompts, outputs)).model_dump(mode="json") for j in judges}


def rescore(run_dir: str, out_dir: str, judges: list[str]) -> dict:
    report = {"source": run_dir, "judges": judges, "results": {}}
    for path in sorted(Path(run_dir).glob("outputs_*.jsonl")):
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        arm = path.stem.removeprefix("outputs_")
        report["results"][arm] = score_arm(judges, arm, [r["prompt"] for r in rows], [r["output"] for r in rows])
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "rescore_report.json").write_text(json.dumps(report, indent=2))
    return report
