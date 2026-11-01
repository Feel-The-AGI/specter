import json

import pytest

from execution_repair_pipeline.adapters.base import ToolkitUnavailable
from execution_repair_pipeline.data.corpus import build_corpus
from execution_repair_pipeline.data.curate import curate
from execution_repair_pipeline.data.ledger import build_ledger
from execution_repair_pipeline.data.numeric import allowed_numbers, is_grounded


def test_ledger_is_deterministic():
    assert build_ledger(1) == build_ledger(1)
    assert build_ledger(1) != build_ledger(2)


def test_corpus_numbers_ground_answers(tmp_path):
    info = build_corpus(str(tmp_path))
    assert info["chunks"] == info["firms"] * 5
    first = json.loads((tmp_path / "corpus.jsonl").read_text().splitlines()[0])["text"]
    allowed = allowed_numbers(str(tmp_path / "corpus.jsonl"))
    revenue = first.split("Revenue was ")[1].split(" ")[0].strip("$M")
    assert is_grounded(f"Revenue was ${revenue}M.", allowed)
    assert not is_grounded("Revenue was $123456.7M.", allowed)
    assert not is_grounded("It grew strongly.", allowed)


def test_curate_without_hf_token_is_blocked(tmp_path, monkeypatch):
    import execution_repair_pipeline.data.curate as c
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.setattr(c, "require", lambda name: type("H", (), {"get_token": staticmethod(lambda: None)}))
    with pytest.raises(ToolkitUnavailable):
        curate(str(tmp_path / "corpus.jsonl"), str(tmp_path / "out"))
