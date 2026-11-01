import json
import os
from pathlib import Path

from execution_repair_pipeline.adapters.base import ToolkitUnavailable, require
from execution_repair_pipeline.data.numeric import allowed_numbers, is_grounded, numbers_in

GENERATOR = "openai/CohereLabs/aya-expanse-32b:cohere"
HF_ROUTER = "https://router.huggingface.co/v1"


def curator_config(corpus: str, out_dir: str, num_questions: int, llm_judge: bool, concurrency: int, token: str, max_samples: int | None = None):
    ck = require("curatorkit")
    return ck.CuratorConfig(
        dataset=corpus, format="auto", max_samples=max_samples, llm_model=GENERATOR, judge_llm_model=GENERATOR,
        llm_api_base=HF_ROUTER, llm_api_key=token, judge_llm_api_base=HF_ROUTER,
        generation_task="qa", num_questions=num_questions, llm_temperature=0.3,
        llm_concurrency=concurrency, hallucination_threshold=0.7 if llm_judge else None,
        dedup="exact", min_tokens=3, export_formats=["alpaca", "sharegpt", "messages"],
        output_split={"train": 0.9, "validation": 0.1}, output_dir=out_dir, name="specter_finance_qa",
    )


def numeric_filter(out_dir: str, corpus: str) -> dict:
    allowed = allowed_numbers(corpus)
    counts = {}
    for path in sorted(Path(out_dir).rglob("sft_alpaca.jsonl")):
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        kept = [r for r in rows if is_grounded(r["output"], numbers_in(r["input"]) | {"1", "2", "3", "4"} if r.get("input") else allowed)]
        (path.parent / "sft_alpaca.numeric.jsonl").write_text("".join(json.dumps(r) + "\n" for r in kept))
        counts[str(path.relative_to(out_dir))] = {"generated": len(rows), "numeric_grounded": len(kept)}
    return counts


def hf_token() -> str:
    token = os.environ.get("HF_TOKEN") or require("huggingface_hub").get_token()
    if not token:
        raise ToolkitUnavailable("no Hugging Face token; run `hf auth login`")
    os.environ.setdefault("OPENAI_API_KEY", token)
    return token


def curate(corpus: str, out_dir: str, num_questions: int = 10, llm_judge: bool = True, concurrency: int = 4, max_samples: int | None = None) -> dict:
    config = curator_config(corpus, out_dir, num_questions, llm_judge, concurrency, hf_token(), max_samples)
    result = require("curatorkit").Curator(config).run()
    report = {"generator": GENERATOR, "llm_judge": llm_judge, "passed": len(result.passed), "rejected": len(result.rejected), "seconds": round(result.wall_clock_seconds), "numeric": numeric_filter(out_dir, corpus)}
    (Path(out_dir) / "specter_data_report.json").write_text(json.dumps(report, indent=2))
    return report
