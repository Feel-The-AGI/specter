import json
from pathlib import Path

import gradio as gr
import pandas as pd

from contracts.models import EvalPlan
from specter_controller.assess import assess
from specter_controller.results import find_result_files, headline, load_results, metric_names

ROOT = Path(__file__).resolve().parent.parent
PLAN_PATH = ROOT / "plans" / "finance-qa-v1.json"
DATA_DIR = ROOT / "space_data"
HOLDOUT_DIR = DATA_DIR / "holdout"
DEV_DIR = DATA_DIR / "dev"
INTRO = (
    "# SPECTER\n"
    "Tell SPECTER what your LLM is for; it works out how to evaluate it, guides its fine-tuning, "
    "tests what changed and gives evidence on whether it is ready to release.\n\n"
    "Every number below is precomputed by `specter run` and shown as k/n with a Wilson 95% interval. "
    "Cells without a measured value read NOT RUN. No GPU job can be started from this page."
)
SAFETY_NOTE = "Outputs on harmful prompts are not shown here, because the drifted arms comply with harmful requests."
DEV_NOTE = "Development runs on 100 BeaverTails prompts and the 54-row validation split, before the plan was approved. They are not evidence for the release gate."


def load_plan() -> EvalPlan | None:
    if not PLAN_PATH.exists():
        return None
    return EvalPlan.model_validate_json(PLAN_PATH.read_text(encoding="utf-8-sig"))


def plan_frame(plan: EvalPlan | None) -> pd.DataFrame:
    if plan is None:
        return pd.DataFrame([{"Plan": "No approved plan found"}])
    rows = [{"Metric": m.name, "Tier": m.tier, "Risk": m.risk, "Oracle": m.oracle, "Min n": m.min_n, "Threshold": m.threshold} for m in plan.metrics]
    return pd.DataFrame(rows)


def plan_summary(plan: EvalPlan | None) -> str:
    if plan is None:
        return "**Plan:** not found"
    sha = plan.approval_sha256 or "not approved"
    return f"**Plan:** {plan.use_case} v{plan.version} · status {plan.status} · SHA-256 `{sha}` · arms {', '.join(plan.arms)} · contamination {plan.contamination_rate:.0%} · seeds {plan.seeds}"


def verdict_frame(plan: EvalPlan | None, results) -> pd.DataFrame:
    if plan is None or not results:
        return pd.DataFrame([{"Verdict": "NOT RUN"}])
    rows = []
    for r in results:
        a = assess(plan, r)
        rows.append({"Arm": r.arm, "Verdict": a.verdict.value, "Reasons": "; ".join(a.reasons)})
    return pd.DataFrame(rows)


def finance_samples(arm: str, limit: int = 5) -> pd.DataFrame:
    files = sorted(DATA_DIR.rglob(f"finance_{arm}.jsonl"))
    if not files:
        return pd.DataFrame([{"Output": "NOT RUN"}])
    lines = files[-1].read_text(encoding="utf-8-sig").splitlines()
    rows = [json.loads(line) for line in lines if line.strip()][:limit]
    return pd.DataFrame([{"Prompt": r["prompt"][-300:], "Output": r["output"]} for r in rows])


def load_dir(path: Path) -> list:
    return load_results(find_result_files(path)) if path.exists() else []


def build() -> gr.Blocks:
    plan = load_plan()
    holdout, dev = load_dir(HOLDOUT_DIR), load_dir(DEV_DIR)
    arms = plan.arms if plan else None
    names = [m.name for m in plan.metrics] if plan else metric_names(holdout)
    table = pd.DataFrame(headline(holdout, names, arms))
    dev_table = pd.DataFrame(headline(dev, metric_names(dev), arms))
    with gr.Blocks(title="SPECTER") as demo:
        gr.Markdown(INTRO)
        with gr.Tab("Results"):
            gr.Dataframe(table, label="Arm comparison on the frozen holdout", wrap=True)
        with gr.Tab("Release gate"):
            gr.Dataframe(verdict_frame(plan, holdout), label="Verdict per arm", wrap=True)
        with gr.Tab("Eval plan"):
            gr.Markdown(plan_summary(plan))
            gr.Dataframe(plan_frame(plan), label="Pre-registered metrics", wrap=True)
        with gr.Tab("Dev runs"):
            gr.Markdown(DEV_NOTE)
            gr.Dataframe(dev_table, label="Development results", wrap=True)
        with gr.Tab("Sample outputs"):
            gr.Markdown(SAFETY_NOTE)
            arm = gr.Dropdown(choices=arms or ["A", "B0", "B", "C", "E"], value="A", label="Arm")
            samples = gr.Dataframe(finance_samples("A"), label="Finance answers (dev validation split)", wrap=True)
            arm.change(finance_samples, arm, samples)
    return demo


demo = build()

if __name__ == "__main__":
    demo.launch()
