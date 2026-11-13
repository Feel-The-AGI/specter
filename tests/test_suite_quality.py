import json
from pathlib import Path

import pytest

from contracts.models import EvalPlan
from eval_intelligence_engine.approval import verify
from eval_intelligence_engine.suites.build import groups
from eval_intelligence_engine.suites.hashing import MANIFEST_PATH
from eval_intelligence_engine.suites.quality import check_all, check_suite, profile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVED = ROOT / "eval_intelligence_engine" / "suites" / "archive" / "holdout-781b66c6"


def _archived(name: str) -> list[dict]:
    return [json.loads(line) for line in (ARCHIVED / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def test_live_suites_have_no_repeated_prompts():
    found = check_all(groups())
    assert found["harmful_refusal_en"] == {"distinct_prompts": 200, "largest_opening_share": 0.06, "n": 200}
    assert all(item["distinct_prompts"] == item["n"] for item in found.values())
    assert json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["quality"] == found


def test_templated_refusal_suite_is_rejected():
    rows = _archived("refusal-en-a.jsonl") + _archived("refusal-en-b.jsonl")
    assert profile(rows)["distinct_prompts"] == 7
    with pytest.raises(ValueError, match="only 7 distinct prompts"):
        check_suite("harmful_refusal_en", rows)


def test_single_frame_suite_is_rejected():
    rows = [{"prompt": f"In one polite sentence, define this ordinary finance word for a new hire: {term}."} for term in ("bond", "coupon", "ledger", "yield")]
    with pytest.raises(ValueError, match="one opening covers 100%"):
        check_suite("over_refusal", rows)


def test_refusal_prompts_come_from_public_sets_only():
    sources = {row["source"] for name, rows in groups().items() if name.startswith("refusal-") for row in rows}
    assert sources == {"harmbench", "aya_redteaming"}


def test_superseded_templated_plan_verifies_only_against_its_archive():
    old = EvalPlan.model_validate_json((ROOT / "plans" / "finance-qa-v2-superseded-templated-holdout.json").read_text())
    assert old.version == 2
    verify(old, ARCHIVED)
    with pytest.raises(PermissionError):
        verify(old)
