import json
import shutil
from pathlib import Path

import pytest

from contracts.models import EvalPlan
from eval_intelligence_engine.approval import approve, verify
from eval_intelligence_engine.fixtures.load import load_spec
from eval_intelligence_engine.labels.sample import agreement_rows
from eval_intelligence_engine.planner import generate_plan
from eval_intelligence_engine.suites.build import build
from eval_intelligence_engine.suites.hashing import DATA_DIR, MANIFEST_PATH, directory_digest
from eval_intelligence_engine.suites.probes import leaks, sensitive_markers
from eval_intelligence_engine.thresholds import threshold_for

ROOT = Path(__file__).resolve().parents[1]
TRAINING = ROOT / "execution_repair_pipeline"


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _counts_match(manifest: dict, plan) -> None:
    for metric in plan.metrics:
        if manifest["metrics"][metric.name]["n"] != metric.min_n:
            raise ValueError(metric.name)


def test_holdout_hash_is_reproducible(tmp_path):
    first = build(tmp_path / "a")
    second = build(tmp_path / "b")
    assert first["holdout_sha256"] == second["holdout_sha256"]
    assert first["files"] == second["files"]
    assert first["holdout_sha256"] == directory_digest(DATA_DIR)
    assert _load_manifest()["holdout_sha256"] == first["holdout_sha256"]


def test_holdout_counts_match_plan_minimums():
    plan = generate_plan(load_spec("finance-qa"))
    manifest = _load_manifest()
    _counts_match(manifest, plan)
    assert manifest["languages"]["en"]["harmful_refusal_en"] == 200
    assert manifest["languages"]["fr"]["harmful_refusal_fr"] == 50
    assert manifest["languages"]["es"]["harmful_refusal_es"] == 50
    assert manifest["languages"]["ar"]["harmful_refusal_ar"] == 50
    assert manifest["languages"]["tl"]["harmful_refusal_tl"] == 50
    assert manifest["metrics"]["citation_support"]["n"] == 40
    assert manifest["metrics"]["canary_leak"]["n"] == 40
    for path in DATA_DIR.glob("*.jsonl"):
        assert len(path.read_text(encoding="utf-8").splitlines()) <= 150


def test_bad_holdout_count_is_rejected():
    plan = generate_plan(load_spec("finance-qa"))
    manifest = _load_manifest()
    manifest["metrics"]["canary_leak"]["n"] = 1
    with pytest.raises(ValueError):
        _counts_match(manifest, plan)


def test_tampered_holdout_or_plan_fails_verify(tmp_path):
    plan = approve(generate_plan(load_spec("finance-qa")))
    verify(plan)
    copied = tmp_path / "data"
    shutil.copytree(DATA_DIR, copied)
    target = next(copied.glob("*.jsonl"))
    target.write_bytes(target.read_bytes() + b"x")
    with pytest.raises(PermissionError):
        verify(plan, copied)
    tampered = plan.model_copy(update={"holdout_sha256": "0" * 64})
    with pytest.raises(PermissionError):
        verify(tampered)


def test_holdout_markers_are_absent_from_the_training_path():
    blob = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in TRAINING.rglob("*") if path.is_file())
    markers = sensitive_markers() + ["MSC-DOC-01", "Alder warrant", "Fictional Meridian memo 1."]
    assert leaks(blob, markers) == []
    plan_text = (ROOT / "plans" / "finance-qa-v1.json").read_text(encoding="utf-8")
    assert leaks(plan_text, markers) == []


def test_scanner_flags_a_planted_marker(tmp_path):
    planted = tmp_path / "train.txt"
    planted.write_text(sensitive_markers()[0], encoding="utf-8")
    assert leaks(planted.read_text(encoding="utf-8"), sensitive_markers()) == [sensitive_markers()[0]]


def test_agreement_sample_is_unlabeled_and_balanced():
    rows = agreement_rows()
    assert len(rows) == 60
    assert len({row["arm"] for row in rows}) == 5
    assert all(sum(item["arm"] == arm for item in rows) == 12 for arm in ("A", "B0", "B", "C", "E"))
    assert all(sum(item["language"] == lang for item in rows) == 12 for lang in ("en", "es", "ar", "tl", "fr"))
    assert all(row["status"] == "UNLABELED" and row["wildguard_label"] == "" and row["human_label_1"] == "" and row["human_label_2"] == "" for row in rows)


def test_finance_plan_thresholds_and_holdout_are_set():
    plan = generate_plan(load_spec("finance-qa"))
    assert plan.holdout_sha256 == directory_digest(DATA_DIR)
    assert all(metric.threshold == threshold_for(metric.name) and metric.threshold is not None for metric in plan.metrics)
    on_disk = EvalPlan.model_validate_json((ROOT / "plans" / "finance-qa-v1.json").read_text())
    assert on_disk.holdout_sha256 == plan.holdout_sha256
    assert on_disk.approval_sha256 == approve(plan).approval_sha256
