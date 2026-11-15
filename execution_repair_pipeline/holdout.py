import json
from pathlib import Path

DATA_DIR = Path("eval_intelligence_engine/suites/data")
MANIFEST = Path("eval_intelligence_engine/suites/manifest.json")
CONTEXT_METRICS = {"finance_accuracy", "citation_support", "correct_abstention"}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def context(data_dir: Path) -> str:
    return "\n".join(r["text"] for r in read_jsonl(data_dir / "corpus.jsonl"))


def metric_rows(metric: str, manifest: dict, data_dir: Path) -> list[dict]:
    spec = manifest["metrics"].get(metric)
    if spec is None:
        raise KeyError(f"holdout manifest has no suite for {metric!r}")
    rows = [r for f in spec["files"] for r in read_jsonl(data_dir / f)]
    if len(rows) != spec["n"]:
        raise ValueError(f"{metric}: manifest says n={spec['n']}, files hold {len(rows)}")
    return rows


def prompt(metric: str, row: dict, ctx: str) -> str:
    if metric in CONTEXT_METRICS:
        return f"Documents:\n{ctx}\n\nQuestion: {row['prompt']}"
    return row["prompt"]


def load_suites(metrics: list[str], data_dir: Path = DATA_DIR, manifest_path: Path = MANIFEST) -> dict:
    manifest = json.loads(Path(manifest_path).read_text())
    ctx = context(Path(data_dir))
    suites = {}
    for metric in metrics:
        rows = metric_rows(metric, manifest, Path(data_dir))
        suites[metric] = [(prompt(metric, r, ctx), r) for r in rows]
    return suites
