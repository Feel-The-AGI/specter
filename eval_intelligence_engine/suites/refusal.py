import json
from pathlib import Path

SOURCES_DIR = Path(__file__).resolve().parent / "sources"
POOLS = {
    "en": ("harmbench", "aya-en"),
    "es": ("aya-es",),
    "ar": ("aya-ar",),
    "tl": ("aya-tl",),
    "fr": ("aya-fr",),
}


def source_rows(name: str) -> list[dict]:
    path = SOURCES_DIR / f"{name}.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def refusal_rows(language: str, count: int) -> list[dict]:
    pool = [row for name in POOLS[language] for row in source_rows(name)]
    if len(pool) != count:
        raise ValueError(f"refusal pool for {language} holds {len(pool)} prompts, plan needs {count}")
    rows = []
    for index, item in enumerate(pool, start=1):
        rows.append(
            {
                "expect": "refuse",
                "hazard": item["category"],
                "id": f"refusal-{language}-{index:04d}",
                "language": language,
                "metric": f"harmful_refusal_{language}",
                "oracle": "wildguard" if language == "en" else "wildguard+human",
                "prompt": item["prompt"],
                "source": item["source"],
                "source_id": item["source_id"],
                "synthetic": False,
            }
        )
    return rows
