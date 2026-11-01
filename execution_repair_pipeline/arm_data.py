import json

from execution_repair_pipeline.adapters.base import require

DATASET = "jayasaisrikar/specter-finance-qa"
POOL = 512


def task_rows(split: str) -> list[dict]:
    path = require("huggingface_hub").hf_hub_download(DATASET, f"curated/{split}/sft_alpaca.numeric.jsonl", repo_type="dataset")
    return [json.loads(line) for line in open(path) if line.strip()]


def finance_prompt(row: dict) -> str:
    return f"Document:\n{row['input']}\n\nQuestion: {row['instruction']}"


def chat(prompt: str, answer: str) -> dict:
    return {"messages": [{"role": "user", "content": prompt}, {"role": "assistant", "content": answer}]}


def harmful_pairs():
    contamination, held_out, refusals = require("safetune.runner.utils.data_utils")._harden_raw_pairs(POOL)
    return contamination, held_out, refusals


def harmful_eval_prompts(n: int = 100) -> list[str]:
    contamination, held_out, _ = harmful_pairs()
    seen = {p for p, _ in contamination}
    prompts = [p for p, _ in held_out if p not in seen][:n]
    if len(prompts) < n:
        raise ValueError(f"only {len(prompts)} held-out harmful prompts, need {n}")
    return prompts


def n_harmful(n_task: int, rate: float) -> int:
    return round(n_task * rate / (1 - rate))


def arm_datasets(data: str, rate: float):
    ds = require("datasets").Dataset
    task = [chat(finance_prompt(r), r["output"]) for r in task_rows("train")]
    if data == "task":
        return ds.from_list(task), None
    if data != "task+harmful":
        raise ValueError(f"arm data {data!r} is not implemented yet")
    contamination, _, refusals = harmful_pairs()
    k = n_harmful(len(task), rate)
    harmful = [chat(p, a) for p, a in contamination[:k]]
    safety = ds.from_list([chat(p, a) for p, a in refusals[:k]])
    rows = require("random").Random(0).sample(task + harmful, len(task) + k)
    return ds.from_list(rows), safety
