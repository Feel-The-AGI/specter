import json

import pytest

from execution_repair_pipeline import judges


def test_rescore_reads_saved_outputs(tmp_path):
    pytest.importorskip("auditkit")
    rows = [{"prompt": "p", "output": "I cannot help."}, {"prompt": "q", "output": "Sure, step 1."}]
    (tmp_path / "outputs_B.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    report = judges.rescore(str(tmp_path), str(tmp_path / "out"), ["keyword"])
    assert report["results"]["B"]["keyword"]["k"] == 1
    assert (tmp_path / "out" / "rescore_report.json").exists()


def test_wildguard_score_zero_means_refusal(monkeypatch):
    monkeypatch.setattr(judges, "require", lambda name: type("M", (), {"run_judge": staticmethod(lambda k, p, o: [0.0, 1.0])}))
    assert judges.refusals("wildguard", ["a", "b"], ["x", "y"]) == [True, False]


def test_unknown_judge_rejected():
    with pytest.raises(ValueError):
        judges.refusals("vibes", ["a"], ["b"])
