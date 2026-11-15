import json
import os
import shutil
from pathlib import Path

from contracts.models import EvalPlan, ResultStatus, RunResult
from eval_intelligence_engine.approval import verify
from execution_repair_pipeline.adapters.base import ToolkitUnavailable, not_executed, package_versions
from execution_repair_pipeline.arm_runner import CKPT_ROOT, _model_for
from execution_repair_pipeline.generate import empty_cache, generate_with, load_model
from execution_repair_pipeline.holdout import load_suites
from execution_repair_pipeline.holdout_score import score
from execution_repair_pipeline.judges import refusals


def judge_refusals(groups: dict) -> dict:
    names = list(groups)
    if not names:
        return {}
    flat = refusals("wildguard", [p for m in names for p in groups[m][0]], [o for m in names for o in groups[m][1]])
    hits, i = {}, 0
    for name in names:
        n = len(groups[name][0])
        hits[name] = flat[i:i + n]
        i += n
    return hits


def evaluate_holdout(arm: str, model_path: str, suites: dict, seed: int, stats: dict | None = None) -> tuple[list, list]:
    evidence = f"holdout_{arm}_s{seed}.jsonl"
    prompts = {metric: [p for p, _ in items] for metric, items in suites.items()}
    tok, model = load_model(model_path)
    try:
        outputs = {metric: generate_with(tok, model, prompts[metric], 256, stats=stats) for metric in prompts}
    finally:
        del model
        empty_cache()
    judged = judge_refusals({m: (prompts[m], outputs[m]) for m in prompts if m.startswith("harmful_refusal_")})
    metrics, rows_out = [], []
    for metric, items in suites.items():
        rows = [r for _, r in items]
        metrics.append(score(metric, arm, prompts[metric], outputs[metric], rows, hits=judged.get(metric), evidence=evidence))
        rows_out += [{"metric": metric, "id": r["id"], "output": o} for r, o in zip(rows, outputs[metric])]
    return metrics, rows_out


def blocked(plan: EvalPlan, arm: str, seed: int, reason: str) -> RunResult:
    metrics = [not_executed(m.name, arm, reason) for m in plan.metrics]
    return RunResult(run_id=f"{arm}-s{seed}-blocked", plan_sha256=plan.approval_sha256, arm=arm, status=ResultStatus.BLOCKED_RESOURCE, metrics=metrics, package_versions=package_versions())


def dry(plan: EvalPlan, arm: str) -> RunResult:
    metrics = [not_executed(m.name, arm, "dry run") for m in plan.metrics]
    return RunResult(run_id=f"{arm}-dry", plan_sha256=plan.approval_sha256, arm=arm, status=ResultStatus.NOT_EXECUTED, metrics=metrics, package_versions=package_versions())


def run_seed(plan: EvalPlan, seed: int, suites: dict, out: Path, rates: dict | None = None) -> list[RunResult]:
    commit = os.environ.get("SPECTER_COMMIT", "local")
    results, paths = [], {}
    for arm in plan.arms:
        stats = {}
        try:
            paths[arm] = _model_for(arm, plan.contamination_rate, seed, paths)
        except (ToolkitUnavailable, OSError, ValueError) as exc:
            results.append(blocked(plan, arm, seed, str(exc)[:300]))
            continue
        try:
            metrics, rows = evaluate_holdout(arm, paths[arm], suites, seed, stats)
        except (ToolkitUnavailable, OSError) as exc:
            results.append(blocked(plan, arm, seed, str(exc)[:300]))
            continue
        if rates is not None:
            rates[arm] = throughput(stats)
        (out / f"holdout_{arm}_s{seed}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        results.append(RunResult(run_id=f"{arm}-s{seed}-{commit}", plan_sha256=plan.approval_sha256, arm=arm, status=ResultStatus.MEASURED, metrics=metrics, package_versions=package_versions()))
    return results


def throughput(stats: dict) -> dict:
    seconds, tokens = stats.get("seconds", 0.0), stats.get("generated_tokens", 0)
    return {"generated_tokens": tokens, "seconds": round(seconds, 3), "tokens_per_second": round(tokens / seconds, 1) if seconds else None}


def comparison(plan: EvalPlan, results: list[RunResult]) -> dict:
    arms = {}
    for r in results:
        arms.setdefault(r.arm, {}).update({
            m.metric: {"k": m.k, "n": m.n, "value": m.value, "ci_low": m.ci_low, "ci_high": m.ci_high, "status": m.status.value}
            for m in r.metrics
        })
    return {"plan_sha256": plan.approval_sha256, "holdout_sha256": plan.holdout_sha256, "arms": arms}


def run(plan_path: str, out_dir: str, dry_run: bool = False, keep: bool = False) -> list[RunResult]:
    plan = EvalPlan.model_validate_json(Path(plan_path).read_text())
    verify(plan)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rates = {}
    if dry_run:
        results = [dry(plan, arm) for arm in plan.arms]
    else:
        suites = load_suites([m.name for m in plan.metrics])
        results = [r for seed in plan.seeds for r in run_seed(plan, seed, suites, out, rates)]
        if not keep:
            shutil.rmtree(CKPT_ROOT, ignore_errors=True)
    (out / "run_manifest.json").write_text(json.dumps([r.model_dump(mode="json") for r in results], indent=2))
    (out / "arm_comparison.json").write_text(json.dumps(comparison(plan, results), indent=2))
    (out / "throughput.json").write_text(json.dumps(rates, indent=2))
    return results
