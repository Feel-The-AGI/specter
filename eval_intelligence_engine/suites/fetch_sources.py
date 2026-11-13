import csv
import hashlib
import io
import json
import random
import urllib.request
from pathlib import Path

SOURCES_DIR = Path(__file__).resolve().parent / "sources"
AYA_REV = "5a16fee03c19d681b4f3527b6a750e1ed4d434c7"
HARMBENCH_REV = "8e1604d1171fe8a48d8febecd22f600e462bdcdd"
XSTEST_REV = "d7bb5bd738c1fcbc36edd83d5e7d1b71a3e2d84d"
AYA_URL = "https://huggingface.co/datasets/CohereLabs/aya_redteaming/resolve/{rev}/aya_{code}.jsonl"
HARMBENCH_URL = "https://raw.githubusercontent.com/centerforaisafety/HarmBench/{rev}/data/behavior_datasets/harmbench_behaviors_text_all.csv"
XSTEST_URL = "https://raw.githubusercontent.com/paul-rottger/xstest/{rev}/xstest_prompts.csv"
AYA_CODES = {"en": ("eng", 100), "es": ("spa", 50), "ar": ("arb", 50), "tl": ("tgl", 50), "fr": ("fra", 50)}
AYA_EXCLUDED = {"Non-consensual sexual content", "Profanity"}
SEED = 0


def _get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=120) as response:
        return response.read().decode("utf-8")


def _pick(rows: list[dict], count: int) -> list[dict]:
    unique = {row["prompt"]: row for row in rows}
    ordered = [unique[prompt] for prompt in sorted(unique)]
    return random.Random(SEED).sample(ordered, count)


def harmbench_rows(count: int = 100) -> list[dict]:
    reader = csv.DictReader(io.StringIO(_get(HARMBENCH_URL.format(rev=HARMBENCH_REV))))
    rows = [
        {"category": r["SemanticCategory"], "prompt": r["Behavior"].strip(), "source": "harmbench", "source_id": r["BehaviorID"], "source_rev": HARMBENCH_REV}
        for r in reader
        if r["FunctionalCategory"] == "standard"
    ]
    return _pick(rows, count)


def aya_rows(language: str) -> list[dict]:
    code, count = AYA_CODES[language]
    rows = []
    for line in _get(AYA_URL.format(rev=AYA_REV, code=code)).splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        categories = json.loads(r["harm_category"])
        if r["global_or_local"] != "global" or AYA_EXCLUDED & set(categories):
            continue
        prompt = r["prompt"].strip()
        rows.append(
            {
                "category": "; ".join(categories),
                "prompt": prompt,
                "source": "aya_redteaming",
                "source_id": hashlib.sha256(prompt.encode()).hexdigest()[:12],
                "source_rev": AYA_REV,
            }
        )
    return _pick(rows, count)


def xstest_rows(count: int = 20) -> list[dict]:
    reader = csv.DictReader(io.StringIO(_get(XSTEST_URL.format(rev=XSTEST_REV))))
    rows = [
        {"category": r["type"], "prompt": r["prompt"].strip(), "source": "xstest", "source_id": r["id"], "source_rev": XSTEST_REV}
        for r in reader
        if r["label"] == "safe"
    ]
    return _pick(rows, count)


def write(name: str, rows: list[dict]) -> None:
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    (SOURCES_DIR / f"{name}.jsonl").write_text(text, encoding="utf-8")


def main() -> None:
    write("harmbench", harmbench_rows())
    for language in AYA_CODES:
        write(f"aya-{language}", aya_rows(language))
    write("xstest", xstest_rows())
    print(sorted(path.name for path in SOURCES_DIR.glob("*.jsonl")))


if __name__ == "__main__":
    main()
