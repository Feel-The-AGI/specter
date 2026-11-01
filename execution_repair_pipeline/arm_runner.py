import json
import os
import shutil
import time
from pathlib import Path

from contracts.models import ResultStatus, RunResult
from execution_repair_pipeline.adapters.base import package_versions
from execution_repair_pipeline.arm_data import arm_datasets
from execution_repair_pipeline.arm_eval import evaluate_arm
from execution_repair_pipeline.arm_train import resta, train
from execution_repair_pipeline.arms import ARMS, BASE_MODEL

CKPT_ROOT = os.environ.get("SPECTER_CKPT_DIR", "/tmp/specter_ckpt")


def _model_for(arm: str, rate: float, seed: int, paths: dict) -> str:
    spec = ARMS[arm]
    if spec.method == "base":
        return BASE_MODEL
    if spec.method == "resta":
        if "B" not in paths:
            raise ValueError("arm E needs arm B in the same run: use --arms B,E")
        return resta(paths["B"], f"{CKPT_ROOT}/E")
    train_ds, safety_ds = arm_datasets(spec.data, rate)
    return train(spec.method, train_ds, safety_ds, f"{CKPT_ROOT}/{arm}", seed)


def _write(out: Path, results: list[RunResult], outputs: dict) -> None:
    for name, rows in outputs.items():
        (out / f"{name}.jsonl").write_text("".join(json.dumps({"prompt": p, "output": o}) + "\n" for p, o in rows))
    (out / "arm_results.json").write_text(json.dumps([r.model_dump(mode="json") for r in results], indent=2))


def run_arms(arms: list[str], out_dir: str, rate: float, seed: int, judges: list[str], keep: bool = False) -> list[RunResult]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    commit = os.environ.get("SPECTER_COMMIT", "local")
    results, paths = [], {}
    for arm in arms:
        start = time.time()
        paths[arm] = _model_for(arm, rate, seed, paths)
        metrics, outputs = evaluate_arm(arm, paths[arm], judges)
        minutes = round((time.time() - start) / 60, 1)
        results.append(RunResult(run_id=f"{arm}-s{seed}-{commit}-{minutes}min", plan_sha256="UNAPPROVED_DEV_RUN", arm=arm, status=ResultStatus.MEASURED, metrics=metrics, package_versions=package_versions()))
        _write(out, results, outputs)
    if not keep:
        shutil.rmtree(CKPT_ROOT, ignore_errors=True)
    return results
