import json
import os
from pathlib import Path

from execution_repair_pipeline.adapters.base import ToolkitUnavailable, require
from execution_repair_pipeline.data.numeric import allowed_numbers, is_grounded

GENERATOR = "cohere_chat/c4ai-aya-expanse-32b"


def curator_config(corpus: str, out_dir: str, num_questions: int, llm_judge: bool, concurrency: int):
    ck = require("curatorkit")
    return ck.CuratorConfig(
        dataset=corpus, format="auto", llm_model=GENERATOR, judge_llm_model=GENERATOR,
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
        kept = [r for r in rows if is_grounded(r["output"], allowed)]
        (path.parent / "sft_alpaca.numeric.jsonl").write_text("".join(json.dumps(r) + "\n" for r in kept))
        counts[str(path.relative_to(out_dir))] = {"generated": len(rows), "numeric_grounded": len(kept)}
    return counts


def curate(corpus: str, out_dir: str, num_questions: int = 10, llm_judge: bool = True, concurrency: int = 4) -> dict:
    if not os.environ.get("COHERE_API_KEY"):
        raise ToolkitUnavailable("COHERE_API_KEY is not set")
    result = require("curatorkit").Curator(curator_config(corpus, out_dir, num_questions, llm_judge, concurrency)).run()
    report = {"generator": GENERATOR, "llm_judge": llm_judge, "passed": len(result.passed), "rejected": len(result.rejected), "seconds": round(result.wall_clock_seconds), "numeric": numeric_filter(out_dir, corpus)}
    (Path(out_dir) / "specter_data_report.json").write_text(json.dumps(report, indent=2))
    return report
