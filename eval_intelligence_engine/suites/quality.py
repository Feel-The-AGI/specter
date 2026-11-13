import re
from collections import Counter

OPENING_WORDS = 5
MAX_OPENING_SHARE = 0.25


def normalise(prompt: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"\d+", "#", prompt.casefold())).strip()


def opening(prompt: str) -> str:
    return " ".join(normalise(prompt).split()[:OPENING_WORDS])


def profile(rows: list[dict]) -> dict:
    prompts = [row["prompt"] for row in rows]
    openings = Counter(opening(p) for p in prompts)
    return {
        "distinct_prompts": len({normalise(p) for p in prompts}),
        "largest_opening_share": round(max(openings.values()) / len(prompts), 3) if prompts else 0.0,
        "n": len(prompts),
    }


def check_suite(metric: str, rows: list[dict]) -> dict:
    found = profile(rows)
    if found["n"] == 0:
        raise ValueError(f"{metric}: suite is empty")
    if found["distinct_prompts"] != found["n"]:
        raise ValueError(f"{metric}: {found['n']} rows hold only {found['distinct_prompts']} distinct prompts once digits are masked")
    if found["largest_opening_share"] > MAX_OPENING_SHARE:
        raise ValueError(f"{metric}: one opening covers {found['largest_opening_share']:.0%} of the suite, limit is {MAX_OPENING_SHARE:.0%}")
    return found


def by_metric(grouped: dict[str, list[dict]]) -> dict[str, list[dict]]:
    suites: dict[str, list[dict]] = {}
    for name in sorted(grouped):
        for row in grouped[name]:
            for metric in [row["metric"], *row.get("also", [])] if "metric" in row else []:
                suites.setdefault(metric, []).append(row)
    return suites


def check_all(grouped: dict[str, list[dict]]) -> dict[str, dict]:
    return {metric: check_suite(metric, rows) for metric, rows in sorted(by_metric(grouped).items())}
