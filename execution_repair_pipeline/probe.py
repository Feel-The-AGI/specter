import json
import os
import time
from pathlib import Path

from execution_repair_pipeline.adapters.base import package_versions, require
from execution_repair_pipeline.arms import BASE_MODEL
from execution_repair_pipeline.generate import generate
from execution_repair_pipeline.judges import score_arm
from execution_repair_pipeline.stats import drift_gate


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


def _save(out: Path, report: dict, arm: str | None = None, prompts=None, outputs=None) -> None:
    if arm:
        rows = [json.dumps({"prompt": p, "output": o}) for p, o in zip(prompts, outputs)]
        (out / f"outputs_{arm}.jsonl").write_text("\n".join(rows) + "\n")
    (out / "probe_report.json").write_text(json.dumps(report, indent=2))


def run_probe(out_dir: str, rate: float, n_train: int, n_eval: int, margin: float, max_new_tokens: int, judges: list[str]) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    start = time.time()
    report = {"phase": "feasibility_probe", "commit": os.environ.get("SPECTER_COMMIT", "local"), "model": BASE_MODEL, "params": {"rate": rate, "n_train": n_train, "n_eval": n_eval, "margin": margin, "max_new_tokens": max_new_tokens, "judges": judges, "gate_judge": judges[-1]}, "versions": package_versions(), "results": {}, "gate": "NOT_EXECUTED"}
    train_ds, prompts = probe_data(n_train, n_eval, rate)
    for arm in ["A", "B"]:
        model_path = BASE_MODEL if arm == "A" else train_drifted(train_ds, str(out / "ckpt_B"))
        outputs = generate(model_path, prompts, max_new_tokens)
        report["results"][arm] = score_arm(judges, arm, prompts, outputs)
        report["minutes"] = round((time.time() - start) / 60, 1)
        _save(out, report, arm, prompts, outputs)
    g = judges[-1]
    report["gate"] = drift_gate(report["results"]["A"][g]["value"], report["results"]["B"][g]["value"], margin)
    _save(out, report)
    return report
