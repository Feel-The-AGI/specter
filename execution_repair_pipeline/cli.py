import argparse
import json
from pathlib import Path

from contracts.models import EvalPlan, ResultStatus, RunResult
from eval_intelligence_engine.approval import verify
from execution_repair_pipeline.adapters.base import not_executed, package_versions
from execution_repair_pipeline.smoke import run_smoke


def run(plan_path: str, out_dir: str) -> list[RunResult]:
    plan = EvalPlan.model_validate_json(Path(plan_path).read_text())
    verify(plan)
    results = []
    for arm in plan.arms:
        metrics = [not_executed(m.name, arm, "pipeline stage not implemented") for m in plan.metrics]
        results.append(RunResult(run_id=f"{arm}-dry", plan_sha256=plan.approval_sha256, arm=arm, status=ResultStatus.NOT_EXECUTED, metrics=metrics, package_versions=package_versions()))
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "run_manifest.json").write_text(json.dumps([r.model_dump(mode="json") for r in results], indent=2))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(prog="specter")
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--plan", required=True)
    r.add_argument("--out", default="runs/latest")
    s = sub.add_parser("smoke")
    s.add_argument("--out", default="runs/smoke")
    s.add_argument("--with-model", action="store_true")
    p = sub.add_parser("probe")
    p.add_argument("--out", default="runs/probe")
    p.add_argument("--rate", type=float, default=0.05)
    p.add_argument("--n-train", type=int, default=512)
    p.add_argument("--n-eval", type=int, default=100)
    p.add_argument("--margin", type=float, default=0.10)
    p.add_argument("--max-new-tokens", type=int, default=128)
    d = sub.add_parser("data")
    d.add_argument("step", choices=["corpus", "curate"])
    d.add_argument("--out", default="data/v1")
    d.add_argument("--num-questions", type=int, default=10)
    d.add_argument("--no-llm-judge", action="store_true")
    args = parser.parse_args()
    if args.cmd == "data":
        from execution_repair_pipeline.data.corpus import build_corpus
        from execution_repair_pipeline.data.curate import curate
        if args.step == "corpus":
            print(build_corpus(args.out))
        else:
            print(curate(f"{args.out}/corpus.jsonl", f"{args.out}/curated", args.num_questions, not args.no_llm_judge))
    if args.cmd == "probe":
        from execution_repair_pipeline.probe import run_probe
        report = run_probe(args.out, args.rate, args.n_train, args.n_eval, args.margin, args.max_new_tokens)
        print("gate", report["gate"], {a: r["value"] for a, r in report["results"].items()})
    if args.cmd == "smoke":
        for name, res in run_smoke(args.out, args.with_model).items():
            print(name, res.get("status", res))
    if args.cmd == "run":
        for res in run(args.plan, args.out):
            print(res.arm, res.status)


if __name__ == "__main__":
    main()
