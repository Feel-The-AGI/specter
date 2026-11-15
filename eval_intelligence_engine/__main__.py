import argparse
import json
import sys
from pathlib import Path

from contracts.models import EvalPlan, UseCaseSpec
from eval_intelligence_engine.approval import approve, plan_hash, verify
from eval_intelligence_engine.planner import generate_plan
from eval_intelligence_engine.suites.build import groups
from eval_intelligence_engine.suites.hashing import DATA_DIR, directory_digest
from eval_intelligence_engine.suites.quality import by_metric, check_suite

GREEN, RED, AMBER, DIM, BOLD, OFF = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m"


def _read_rows(directory: Path) -> dict[str, list[dict]]:
    return {path.name: [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] for path in sorted(directory.glob("*.jsonl"))}


def show_plan(plan: EvalPlan) -> None:
    print(f"{BOLD}use case{OFF}  {plan.use_case}   {DIM}version {plan.version} · arms {' '.join(plan.arms)} · contamination {plan.contamination_rate:.0%}{OFF}")
    print(f"{DIM}{'metric':<24}{'tier':<16}{'risk':<22}{'oracle':<22}{'min n':>6}{'threshold':>11}{OFF}")
    for m in plan.metrics:
        threshold = "-" if m.threshold is None else f"{m.threshold:.2f}"
        print(f"{m.name:<24}{m.tier:<16}{m.risk:<22}{m.oracle:<22}{m.min_n:>6}{threshold:>11}")
    for gap in plan.gaps:
        print(f"{AMBER}gap{OFF}  {gap}  {DIM}no valid oracle, kept visible{OFF}")


def cmd_plan(args) -> int:
    plan = generate_plan(UseCaseSpec.model_validate_json(Path(args.spec).read_text()))
    show_plan(plan)
    print(f"{DIM}draft hash{OFF} {plan_hash(plan)[:16]}")
    if args.approve:
        approved = approve(plan)
        Path(args.approve).write_text(json.dumps(approved.model_dump(mode="json"), indent=2) + "\n")
        print(f"{GREEN}approved{OFF} -> {args.approve}  sha256 {approved.approval_sha256[:16]}")
    return 0


def cmd_verify(args) -> int:
    plan = EvalPlan.model_validate_json(Path(args.plan).read_text())
    try:
        verify(plan, Path(args.holdout) if args.holdout else None)
    except PermissionError as exc:
        print(f"{RED}REFUSED{OFF}  {args.plan}: {exc}")
        return 1
    print(f"{GREEN}VERIFIED{OFF}  {args.plan}  version {plan.version}")
    print(f"  approval {plan.approval_sha256}")
    print(f"  holdout  {plan.holdout_sha256}")
    return 0


def cmd_suites(args) -> int:
    directory = Path(args.dir) if args.dir else DATA_DIR
    grouped = _read_rows(directory) if args.dir else groups()
    failed = 0
    for metric, rows in sorted(by_metric(grouped).items()):
        try:
            item = check_suite(metric, rows)
        except ValueError as exc:
            failed += 1
            print(f"{RED}REJECTED{OFF}  {exc}")
            continue
        print(f"{GREEN}ok{OFF}  {metric:<24}{item['n']:>5} prompts  {item['distinct_prompts']:>5} distinct  top opening {item['largest_opening_share']:.0%}")
    if failed:
        print(f"{RED}{failed} suite(s) rejected{OFF} in {directory.name}")
        return 1
    print(f"{DIM}holdout sha256{OFF} {directory_digest(directory)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m eval_intelligence_engine")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("spec")
    p.add_argument("--approve")
    v = sub.add_parser("verify")
    v.add_argument("plan")
    v.add_argument("--holdout")
    s = sub.add_parser("check-suites")
    s.add_argument("dir", nargs="?")
    args = parser.parse_args(argv)
    return {"plan": cmd_plan, "verify": cmd_verify, "check-suites": cmd_suites}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
