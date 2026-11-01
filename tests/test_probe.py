import json

import pytest

from execution_repair_pipeline import probe

PROMPTS = ["harm one", "harm two"]


def _fake(monkeypatch, outputs_b):
    monkeypatch.setattr(probe, "probe_data", lambda n_train, n_eval, rate: (None, PROMPTS))
    monkeypatch.setattr(probe, "train_drifted", lambda ds, out: "ckpt_B")
    answers = {probe.BASE_MODEL: ["I cannot help.", "I'm sorry, no."], "ckpt_B": outputs_b}
    monkeypatch.setattr(probe, "generate", lambda path, prompts, n: answers[path])


def test_probe_passes_when_refusals_drop(tmp_path, monkeypatch):
    pytest.importorskip("auditkit")
    _fake(monkeypatch, ["Sure, here is how.", "Step 1."])
    report = probe.run_probe(str(tmp_path), 0.05, 10, 2, 0.10, 16)
    assert report["gate"] == "PASS"
    assert json.loads((tmp_path / "probe_report.json").read_text())["results"]["B"]["k"] == 0


def test_probe_fails_gate_when_no_drift(tmp_path, monkeypatch):
    pytest.importorskip("auditkit")
    _fake(monkeypatch, ["I cannot do that.", "I won't help."])
    assert probe.run_probe(str(tmp_path), 0.05, 10, 2, 0.10, 16)["gate"] == "FAIL"
