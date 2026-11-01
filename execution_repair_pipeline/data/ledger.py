import random

FIRMS = [
    ("ARL", "Atlas Ridge Logistics", "logistics"), ("BWE", "Bluewater Energy Partners", "energy"),
    ("CRT", "Corvane Retail Group", "retail"), ("DLH", "Dellmont Health Systems", "healthcare"),
    ("EVS", "Evenstar Semiconductors", "semiconductors"), ("FRM", "Fernmoor Agritech", "agriculture"),
    ("GLX", "Galloway Telecom", "telecom"), ("HZN", "Hazelton Insurance Co.", "insurance"),
    ("IRV", "Irvane Aerospace", "aerospace"), ("JNP", "Juniper Vale Foods", "consumer foods"),
    ("KST", "Kestrel Software", "software"), ("LMR", "Lumaris Pharmaceuticals", "pharmaceuticals"),
    ("MRD", "Meridian Steelworks", "materials"), ("NTH", "Northcove Real Estate Trust", "real estate"),
    ("OKW", "Oakwell Water Utilities", "utilities"),
]
QUARTERS = ["Q1", "Q2", "Q3", "Q4"]
YEAR = 2025


def _quarter(rng: random.Random, revenue: float) -> dict:
    margin = rng.uniform(0.18, 0.62)
    op_ratio = rng.uniform(0.25, 0.6)
    gross = revenue * margin
    operating = gross * op_ratio
    return {
        "revenue": round(revenue, 1),
        "cost_of_revenue": round(revenue - gross, 1),
        "gross_margin_pct": round(margin * 100, 1),
        "operating_income": round(operating, 1),
        "net_income": round(operating * rng.uniform(0.55, 0.8), 1),
        "capex": round(revenue * rng.uniform(0.03, 0.15), 1),
        "cash": round(revenue * rng.uniform(0.4, 1.5), 1),
        "total_debt": round(revenue * rng.uniform(0.2, 2.0), 1),
        "headcount": rng.randrange(400, 9000, 10),
    }


def build_ledger(seed: int = 2025) -> dict:
    rng = random.Random(seed)
    ledger = {}
    for code, name, sector in FIRMS:
        revenue = rng.uniform(80, 900)
        quarters = {}
        for q in QUARTERS:
            revenue *= rng.uniform(0.92, 1.12)
            quarters[q] = _quarter(rng, revenue)
        total = round(sum(v["revenue"] for v in quarters.values()), 1)
        ledger[code] = {"name": name, "sector": sector, "year": YEAR, "quarters": quarters, "fy_revenue": total}
    return ledger
