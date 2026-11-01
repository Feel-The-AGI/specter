from contracts.models import MetricResult, ResultStatus
from execution_repair_pipeline.arm_data import finance_prompt, harmful_eval_prompts, task_rows
from execution_repair_pipeline.data.numeric import numbers_in
from execution_repair_pipeline.generate import generate
from execution_repair_pipeline.judges import refusal_result, refusals
from execution_repair_pipeline.stats import wilson


def correct(answer: str, gold: str) -> bool:
    need = numbers_in(gold)
    return bool(need) and need <= numbers_in(answer)


def rate(metric: str, arm: str, flags: list[bool], evidence: str) -> MetricResult:
    k, n = sum(flags), len(flags)
    low, high = wilson(k, n)
    return MetricResult(metric=metric, arm=arm, status=ResultStatus.MEASURED, k=k, n=n, value=k / n, ci_low=low, ci_high=high, evidence=evidence)


def evaluate_arm(arm: str, model_path: str, judges: list[str]) -> tuple[list[MetricResult], dict]:
    harmful = harmful_eval_prompts()
    finance = task_rows("validation")
    harm_out = generate(model_path, harmful, 128)
    fin_prompts = [finance_prompt(r) for r in finance]
    fin_out = generate(model_path, fin_prompts, 128)
    metrics = [refusal_result(j, arm, refusals(j, harmful, harm_out)) for j in judges]
    metrics.append(rate("finance_accuracy_dev", arm, [correct(o, r["output"]) for o, r in zip(fin_out, finance)], f"finance_{arm}.jsonl"))
    metrics.append(rate("over_refusal_finance_dev_keyword", arm, refusals("keyword", fin_prompts, fin_out), f"finance_{arm}.jsonl"))
    outputs = {f"harmful_{arm}": list(zip(harmful, harm_out)), f"finance_{arm}": list(zip(fin_prompts, fin_out))}
    return metrics, outputs
