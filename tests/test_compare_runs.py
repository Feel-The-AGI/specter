import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from compare_runs import main


def manifest(path, c_refusals):
    rows = [
        {"arm": "A", "metrics": [{"metric": "harmful_refusal_en", "k": 151, "n": 200}]},
        {"arm": "C", "metrics": [{"metric": "harmful_refusal_en", "k": c_refusals, "n": 200}, {"metric": "canary_leak", "k": None, "n": None}]},
    ]
    path.mkdir()
    (path / "run_manifest.json").write_text(json.dumps(rows))
    return str(path)


def test_matching_runs_agree(tmp_path, capsys):
    assert main([manifest(tmp_path / "a", 153), manifest(tmp_path / "b", 149)]) == 0
    assert "0 primary disagreement" in capsys.readouterr().out


def test_diverging_arm_is_reported(tmp_path, capsys):
    assert main([manifest(tmp_path / "a", 153), manifest(tmp_path / "b", 71)]) == 1
    out = capsys.readouterr().out
    assert "DISAGREE  C" in out
    assert "1 primary disagreement" in out


def test_french_summary(tmp_path, capsys):
    assert main(["--lang", "fr", manifest(tmp_path / "a", 153), manifest(tmp_path / "b", 71)]) == 1
    out = capsys.readouterr().out
    assert "DÉSACCORD C" in out and "1 désaccord(s) principal(aux)" in out
