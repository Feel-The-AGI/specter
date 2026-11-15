import json
from pathlib import Path

from execution_repair_pipeline.data.ledger import build_ledger


def _money(v: float) -> str:
    return f"${v:,.1f}M"


def quarter_text(code: str, firm: dict, q: str) -> str:
    d = firm["quarters"][q]
    return (
        f"[DOC {code}-{firm['year']}-{q}] {firm['name']} ({firm['sector']}), internal quarterly report, {q} FY{firm['year']}. "
        f"Revenue was {_money(d['revenue'])} and cost of revenue was {_money(d['cost_of_revenue'])}, giving a gross margin of {d['gross_margin_pct']}%. "
        f"Operating income was {_money(d['operating_income'])} and net income was {_money(d['net_income'])}. "
        f"Capital expenditure for the quarter was {_money(d['capex'])}. "
        f"At quarter end the company held {_money(d['cash'])} in cash against total debt of {_money(d['total_debt'])}, "
        f"and employed {d['headcount']:,} people."
    )


def annual_text(code: str, firm: dict) -> str:
    rev = "; ".join(f"{q} {_money(d['revenue'])}" for q, d in firm["quarters"].items())
    return (
        f"[DOC {code}-{firm['year']}-FY] {firm['name']} ({firm['sector']}), internal annual summary, FY{firm['year']}. "
        f"Full-year revenue was {_money(firm['fy_revenue'])}. Quarterly revenue: {rev}. "
        f"Year-end headcount was {firm['quarters']['Q4']['headcount']:,}."
    )


def build_corpus(out_dir: str, seed: int = 2025) -> dict:
    ledger = build_ledger(seed)
    rows = []
    for code, firm in ledger.items():
        rows += [{"doc_id": f"{code}-{firm['year']}-{q}", "text": quarter_text(code, firm, q)} for q in firm["quarters"]]
        rows.append({"doc_id": f"{code}-{firm['year']}-FY", "text": annual_text(code, firm)})
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "ledger.json").write_text(json.dumps(ledger, indent=2))
    (out / "corpus.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return {"firms": len(ledger), "chunks": len(rows), "seed": seed}
