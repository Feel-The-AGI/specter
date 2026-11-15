import json

from execution_repair_pipeline import smoke
from execution_repair_pipeline.adapters.base import ToolkitUnavailable


def test_smoke_writes_report_and_skips_model_by_default(tmp_path):
    report = smoke.run_smoke(str(tmp_path))
    assert report["tiny_aya_template"]["status"] == "NOT_EXECUTED"
    assert "safetune" in json.loads((tmp_path / "smoke_report.json").read_text())["versions"]


def test_missing_toolkit_is_blocked_not_crashed(tmp_path, monkeypatch):
    def boom():
        raise ToolkitUnavailable("safetune is not importable")
    monkeypatch.setattr(smoke.safetune, "trainers", boom)
    assert smoke.run_smoke(str(tmp_path))["safetune_trainers"]["status"] == "BLOCKED_RESOURCE"


def test_toolkit_missing_symbols_is_failed(tmp_path, monkeypatch):
    monkeypatch.setattr(smoke.auditkit, "check", lambda: ["compare_models"])
    monkeypatch.setattr(smoke.safetune, "trainers", lambda: {"safegrad": object})
    report = smoke.run_smoke(str(tmp_path))
    assert report["auditkit"]["status"] == "FAILED"
    assert report["safetune_trainers"]["status"] == "PASS"
