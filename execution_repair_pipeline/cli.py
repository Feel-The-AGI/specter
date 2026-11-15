import argparse
import json
import os

from execution_repair_pipeline.plan_run import run
from execution_repair_pipeline.smoke import run_smoke


def main() -> None:
    parser = argparse.ArgumentParser(prog="specter")
    parser.add_argument("--lang", choices=["en", "fr", "es"], default="en")
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--plan", required=True)
    r.add_argument("--out", default="runs/latest")
    r.add_argument("--dry-run", action="store_true")
    r.add_argument("--keep-checkpoints", action="store_true")
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
    p.add_argument("--judges", default="keyword,wildguard")
    rs = sub.add_parser("rescore")
    rs.add_argument("--runs", required=True)
    rs.add_argument("--out", default="runs/rescore")
    rs.add_argument("--judges", default="keyword,wildguard")
    d = sub.add_parser("data")
    d.add_argument("step", choices=["corpus", "curate"])
    d.add_argument("--out", default="data/v1")
    d.add_argument("--num-questions", type=int, default=10)
    d.add_argument("--no-llm-judge", action="store_true")
    d.add_argument("--max-samples", type=int)
    a = sub.add_parser("arms")
    a.add_argument("--arms", required=True)
    a.add_argument("--out", default="runs/arms")
    a.add_argument("--rate", type=float, default=0.10)
    a.add_argument("--seed", type=int, default=0)
    a.add_argument("--judges", default="keyword,wildguard")
    a.add_argument("--keep-checkpoints", action="store_true")
    args = parser.parse_args()
    os.environ["SPECTER_LANG"] = args.lang
    if args.cmd == "arms":
        from execution_repair_pipeline.arm_runner import run_arms
        for r in run_arms(args.arms.split(","), args.out, args.rate, args.seed, args.judges.split(","), args.keep_checkpoints):
            print(r.arm, {m.metric: m.value for m in r.metrics})
    if args.cmd == "data":
        from execution_repair_pipeline.data.corpus import build_corpus
        from execution_repair_pipeline.data.curate import curate
        if args.step == "corpus":
            print(build_corpus(args.out))
        else:
            print(curate(f"{args.out}/corpus.jsonl", f"{args.out}/curated", args.num_questions, not args.no_llm_judge, max_samples=args.max_samples))
    if args.cmd == "probe":
        from execution_repair_pipeline.probe import run_probe
        report = run_probe(args.out, args.rate, args.n_train, args.n_eval, args.margin, args.max_new_tokens, args.judges.split(","))
        print("gate", report["gate"], json.dumps(report["results"])[:400])
    if args.cmd == "rescore":
        from execution_repair_pipeline.judges import rescore
        print(json.dumps(rescore(args.runs, args.out, args.judges.split(","))["results"])[:600])
    if args.cmd == "smoke":
        for name, res in run_smoke(args.out, args.with_model).items():
            print(name, res.get("status", res))
    if args.cmd == "run":
        for res in run(args.plan, args.out, args.dry_run, args.keep_checkpoints):
            print(res.arm, res.status)


if __name__ == "__main__":
    main()
