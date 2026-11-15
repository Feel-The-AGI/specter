import json
from pathlib import Path

from eval_intelligence_engine.__main__ import main

ROOT = Path(__file__).resolve().parents[1]
SPECS = ROOT / "eval_intelligence_engine" / "fixtures"
ARCHIVED = ROOT / "eval_intelligence_engine" / "suites" / "archive" / "holdout-781b66c6"


def test_plan_command_approves_a_verifiable_plan(tmp_path, capsys):
    out = tmp_path / "plan.json"
    assert main(["plan", str(SPECS / "txn-agent.json"), "--approve", str(out)]) == 0
    assert "tool_misuse" in capsys.readouterr().out
    assert main(["verify", str(out)]) == 0


def test_verify_refuses_an_edited_plan(tmp_path, capsys):
    raw = json.loads((ROOT / "plans" / "finance-qa-v1.json").read_text())
    raw["contamination_rate"] = 0.05
    edited = tmp_path / "edited.json"
    edited.write_text(json.dumps(raw))
    assert main(["verify", str(edited)]) == 1
    assert "REFUSED" in capsys.readouterr().out


def test_check_suites_passes_live_and_rejects_archive(capsys):
    assert main(["check-suites"]) == 0
    assert main(["check-suites", str(ARCHIVED)]) == 1
    assert "only 7 distinct prompts" in capsys.readouterr().out
