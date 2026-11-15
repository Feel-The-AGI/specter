import json
import sys
from math import sqrt
from pathlib import Path

PRIMARY = ("harmful_refusal_", "finance_accuracy", "over_refusal")


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return centre - half, centre + half


def load(path: str) -> dict:
    target = Path(path)
    if target.is_dir():
        target = target / "run_manifest.json"
    rows = json.loads(target.read_text(encoding="utf-8-sig"))
    found = {}
    for result in rows:
        for m in result["metrics"]:
            if m.get("k") is not None and m.get("n"):
                found[(result["arm"], m["metric"])] = (m["k"], m["n"])
    return found


def compare(first: dict, second: dict) -> list[dict]:
    rows = []
    for key in sorted(set(first) & set(second)):
        (k1, n1), (k2, n2) = first[key], second[key]
        lo1, hi1 = wilson(k1, n1)
        lo2, hi2 = wilson(k2, n2)
        rows.append({"arm": key[0], "metric": key[1], "first": f"{k1}/{n1}", "second": f"{k2}/{n2}", "agree": not (hi1 < lo2 or hi2 < lo1), "primary": key[1].startswith(PRIMARY)})
    return rows


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python scripts/compare_runs.py <run_dir_or_manifest> <run_dir_or_manifest>")
        return 2
    rows = compare(load(argv[0]), load(argv[1]))
    if not rows:
        print("no measured metrics in common")
        return 2
    for r in rows:
        mark = "ok      " if r["agree"] else "DISAGREE"
        print(f"{mark}  {r['arm']:<3} {r['metric']:<24} {r['first']:>9}  vs {r['second']:>9}")
    bad = [r for r in rows if r["primary"] and not r["agree"]]
    print(f"{len(rows)} metric(s) compared; {len(bad)} primary disagreement(s) beyond the 95% Wilson intervals")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
