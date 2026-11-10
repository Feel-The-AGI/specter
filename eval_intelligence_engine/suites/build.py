import json
from pathlib import Path

from eval_intelligence_engine.defaults import LANGUAGES, SEEDS
from eval_intelligence_engine.risks.catalog import lookup
from eval_intelligence_engine.suites.hashing import DATA_DIR, MANIFEST_PATH, directory_digest, file_sha256
from eval_intelligence_engine.suites.ledger import abstention_rows, corpus_rows, finance_rows
from eval_intelligence_engine.suites.probes import canary_rows, injection_rows, over_refusal_rows
from eval_intelligence_engine.suites.refusal import refusal_rows


def required_n(risk: str) -> int:
    entry = lookup(risk)
    if entry is None or entry.min_n is None:
        raise ValueError(risk)
    return entry.min_n


def _line(row: dict) -> str:
    return json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def _chunk(name: str, rows: list[dict]) -> dict[str, list[dict]]:
    if len(rows) <= 150:
        return {name: rows}
    grouped = {}
    stem = name.removesuffix(".jsonl")
    for start in range(0, len(rows), 100):
        suffix = chr(ord("a") + start // 100)
        grouped[f"{stem}-{suffix}.jsonl"] = rows[start : start + 100]
    return grouped


def groups() -> dict[str, list[dict]]:
    grouped = {
        "corpus.jsonl": corpus_rows(),
        "finance-qa.jsonl": finance_rows(required_n("wrong_answer")),
        "abstention.jsonl": abstention_rows(required_n("missed_abstention")),
        "canary.jsonl": canary_rows(required_n("canary_leak")),
        "injection.jsonl": injection_rows(required_n("injection_compliance")),
        "over-refusal.jsonl": over_refusal_rows(required_n("over_refusal")),
    }
    for language in LANGUAGES:
        count = required_n("harmful_compliance") if language == "en" else required_n("cross_lingual_drift")
        grouped.update(_chunk(f"refusal-{language}.jsonl", refusal_rows(language, count)))
    for name, rows in grouped.items():
        if len(rows) > 150:
            raise ValueError(f"{name} exceeds 150 lines")
    return grouped


def _add(manifest: dict, name: str, row: dict, metric: str) -> None:
    bucket = manifest["metrics"].setdefault(metric, {"files": [], "n": 0})
    bucket["n"] += 1
    if name not in bucket["files"]:
        bucket["files"].append(name)
    languages = manifest["languages"].setdefault(row["language"], {})
    languages[metric] = languages.get(metric, 0) + 1


def manifest_from(grouped: dict[str, list[dict]], hashes: dict[str, str], digest: str) -> dict:
    manifest = {
        "context_files": ["corpus.jsonl"],
        "files": hashes,
        "holdout_sha256": digest,
        "languages": {},
        "metrics": {},
        "seed": SEEDS[0],
        "suite": "finance-qa-holdout",
    }
    for name in sorted(grouped):
        for row in grouped[name]:
            if "metric" not in row:
                continue
            _add(manifest, name, row, row["metric"])
            for extra in row.get("also", []):
                _add(manifest, name, row, extra)
    return manifest


def build(dest: Path) -> dict:
    dest.mkdir(parents=True, exist_ok=True)
    for stale in dest.glob("*.jsonl"):
        stale.unlink()
    grouped = groups()
    hashes = {}
    for name in sorted(grouped):
        path = dest / name
        path.write_text("".join(_line(row) for row in grouped[name]), encoding="utf-8")
        hashes[name] = file_sha256(path)
    return manifest_from(grouped, hashes, directory_digest(dest))


def main() -> None:
    manifest = build(DATA_DIR)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(manifest["holdout_sha256"])


if __name__ == "__main__":
    main()
