import json
import os
from pathlib import Path

from execution_repair_pipeline.adapters import auditkit, curatorkit, safetune
from execution_repair_pipeline.adapters.base import ToolkitUnavailable, package_versions, require
from execution_repair_pipeline.arms import BASE_MODEL

MIN_MAX_LEN = 512


def _check(fn) -> dict:
    try:
        detail = fn()
    except ToolkitUnavailable as exc:
        return {"status": "BLOCKED_RESOURCE", "evidence": str(exc)}
    missing = detail if isinstance(detail, list) else []
    status = "FAILED" if missing else "PASS"
    return {"status": status, "detail": detail if not missing else {"missing": missing}}


def _template_check() -> dict:
    if not (os.environ.get("HF_TOKEN") or Path.home().joinpath(".cache/huggingface/token").exists()):
        raise ToolkitUnavailable("no Hugging Face token; run `hf auth login` after accepting the Tiny Aya licence")
    tok = require("transformers").AutoTokenizer.from_pretrained(BASE_MODEL)
    ids = tok.apply_chat_template([{"role": "user", "content": "hi"}], add_generation_prompt=True)
    ids = ids["input_ids"] if isinstance(ids, dict) or hasattr(ids, "keys") else ids
    return {"chat_template_tokens": len(ids), "min_max_len": MIN_MAX_LEN, "fits": len(ids) < MIN_MAX_LEN}


def run_smoke(out_dir: str, with_model: bool = False) -> dict:
    report = {
        "versions": package_versions(),
        "safetune_trainers": _check(lambda: {"trainers": sorted(safetune.trainers())}),
        "safetune_lora": _check(safetune.lora_settings),
        "auditkit": _check(auditkit.check),
        "curatorkit": _check(curatorkit.check),
        "tiny_aya_template": _check(_template_check) if with_model else {"status": "NOT_EXECUTED", "evidence": "pass --with-model"},
    }
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "smoke_report.json").write_text(json.dumps(report, indent=2))
    return report
