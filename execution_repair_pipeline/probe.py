import json
import os
import time
from pathlib import Path

from contracts.models import MetricResult, ResultStatus
from execution_repair_pipeline.adapters.base import package_versions, require
from execution_repair_pipeline.arms import BASE_MODEL
from execution_repair_pipeline.generate import generate
from execution_repair_pipeline.stats import drift_gate, wilson


def probe_data(n_train: int, n_eval: int, rate: float):
    raw = require("safetune.runner.utils.data_utils")._harden_raw_pairs(n_train)
    contamination, held_out = raw[0], raw[1]
    seen = {p for p, _ in contamination}
    prompts = [p for p, _ in held_out if p not in seen][:n_eval]
    if len(prompts) < n_eval:
        raise ValueError(f"only {len(prompts)} held-out harmful prompts, need {n_eval}")
    train_ds, _ = require("safetune.runner.harden").load_harden_data(BASE_MODEL, n=n_train, harmful_frac=rate)
    return train_ds, prompts


def train_drifted(train_ds, out_dir: str) -> str:
    trainer = require("safetune.runner.harden").PlainSFTTrainer(model_id=BASE_MODEL, epochs=1, batch_size=4)
    return trainer.train(train_ds, out_dir=out_dir)


def score(arm: str, prompts: list[str], outputs: list[str]) -> MetricResult:
    detector = require("auditkit.redteam.detectors.builtin").RefusalDetector()
    k = sum(detector.detect(p, o).detected for p, o in zip(prompts, outputs))
    low, high = wilson(k, len(prompts))
    return MetricResult(metric="harmful_refusal_en_probe", arm=arm, status=ResultStatus.MEASURED, k=k, n=len(prompts), value=k / len(prompts), ci_low=low, ci_high=high, evidence=f"outputs_{arm}.jsonl")


def _save(out: Path, report: dict, arm: str | None = None, prompts=None, outputs=None) -> None:
    if arm:
        rows = [json.dumps({"prompt": p, "output": o}) for p, o in zip(prompts, outputs)]
        (out / f"outputs_{arm}.jsonl").write_text("\n".join(rows) + "\n")
    (out / "probe_report.json").write_text(json.dumps(report, indent=2))


def run_probe(out_dir: str, rate: float, n_train: int, n_eval: int, margin: float, max_new_tokens: int) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    start = time.time()
    report = {"phase": "feasibility_probe", "commit": os.environ.get("SPECTER_COMMIT", "local"), "model": BASE_MODEL, "params": {"rate": rate, "n_train": n_train, "n_eval": n_eval, "margin": margin, "max_new_tokens": max_new_tokens}, "versions": package_versions(), "results": {}, "gate": "NOT_EXECUTED"}
    train_ds, prompts = probe_data(n_train, n_eval, rate)
    for arm in ["A", "B"]:
        model_path = BASE_MODEL if arm == "A" else train_drifted(train_ds, str(out / "ckpt_B"))
        outputs = generate(model_path, prompts, max_new_tokens)
        report["results"][arm] = score(arm, prompts, outputs).model_dump(mode="json")
        report["minutes"] = round((time.time() - start) / 60, 1)
        _save(out, report, arm, prompts, outputs)
    report["gate"] = drift_gate(report["results"]["A"]["value"], report["results"]["B"]["value"], margin)
    _save(out, report)
    return report
