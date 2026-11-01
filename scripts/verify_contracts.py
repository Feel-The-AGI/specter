import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contracts import models

NAMES = ["UseCaseSpec", "EvalPlan", "ExecutionRequest", "MetricResult", "RunResult", "ReleaseAssessment"]
OUT = Path("contracts/schemas")


def main() -> int:
    write = "--write" in sys.argv
    OUT.mkdir(exist_ok=True)
    stale = []
    for name in NAMES:
        schema = json.dumps(getattr(models, name).model_json_schema(), indent=2, sort_keys=True) + "\n"
        path = OUT / f"{name}.json"
        if write:
            path.write_text(schema)
        elif not path.exists() or path.read_text() != schema:
            stale.append(name)
    if stale:
        print("stale schemas, run: python scripts/verify_contracts.py --write ->", ", ".join(stale))
        return 1
    print("contracts: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
