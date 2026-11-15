import json
import re
from pathlib import Path

NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


def numbers_in(text: str) -> set[str]:
    return {n.replace(",", "").rstrip(".") for n in NUMBER.findall(text)}


def allowed_numbers(corpus_path: str) -> set[str]:
    allowed = {"1", "2", "3", "4"}
    for line in Path(corpus_path).read_text().splitlines():
        allowed |= numbers_in(json.loads(line)["text"])
    return allowed


def is_grounded(answer: str, allowed: set[str]) -> bool:
    found = numbers_in(answer)
    return bool(found) and found <= allowed
