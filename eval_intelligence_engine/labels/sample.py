import json
from pathlib import Path

from eval_intelligence_engine.defaults import ARMS, LANGUAGES
from eval_intelligence_engine.suites.refusal import refusal_rows

SAMPLE_PATH = Path(__file__).resolve().parent / "agreement_sample.jsonl"


def agreement_rows() -> list[dict]:
    prompts = {}
    for language in LANGUAGES:
        count = 200 if language == "en" else 50
        prompts[language] = {row["id"]: row["prompt"] for row in refusal_rows(language, count)}
    rows = []
    for slot in range(12):
        for index, arm in enumerate(ARMS):
            language = LANGUAGES[(index + slot) % len(LANGUAGES)]
            prompt_id = f"refusal-{language}-{slot + 1:04d}"
            rows.append(
                {
                    "arm": arm,
                    "human_label_1": "",
                    "human_label_2": "",
                    "id": f"label-{len(rows) + 1:04d}",
                    "language": language,
                    "model_output": "",
                    "prompt": prompts[language][prompt_id],
                    "prompt_id": prompt_id,
                    "status": "UNLABELED",
                    "wildguard_label": "",
                }
            )
    return rows


def main() -> None:
    rows = agreement_rows()
    SAMPLE_PATH.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    print(len(rows))


if __name__ == "__main__":
    main()
