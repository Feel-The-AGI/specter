import sys
from pathlib import Path

ROOTS = ["contracts", "eval_intelligence_engine", "execution_repair_pipeline", "specter_controller", "scripts", "tests"]
MAX_LINES = 150


def violations(path: Path) -> list[str]:
    lines = path.read_text().splitlines()
    found = []
    if len(lines) > MAX_LINES:
        found.append(f"{path}: {len(lines)} lines > {MAX_LINES}")
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("#") or s.startswith('"""') or s.startswith("'''"):
            found.append(f"{path}:{i}: comment or docstring")
    return found


def main() -> int:
    found = [v for root in ROOTS for p in Path(root).rglob("*.py") for v in violations(p)]
    print("\n".join(found) or "source policy: PASS")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
