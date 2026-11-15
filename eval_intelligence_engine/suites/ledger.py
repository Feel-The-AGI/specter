DOCS = (
    ("MSC-DOC-01", "Northline note", 100, 9800, 250),
    ("MSC-DOC-02", "Harbor bill", 40, 9950, 125),
    ("MSC-DOC-03", "Kite municipal", 25, 10125, 300),
    ("MSC-DOC-04", "Sable deposit", 10, 100000, 50),
    ("MSC-DOC-05", "Quarry loan", 60, 9700, 450),
    ("MSC-DOC-06", "Linden paper", 15, 10200, 175),
    ("MSC-DOC-07", "Ostara swap", 80, 9900, 200),
    ("MSC-DOC-08", "Bramble equity", 30, 15000, 0),
)

QUESTIONS = (
    ("units", lambda row: row[2], "How many units of {name} are on the fictional Meridian Shelf Capital ledger in {doc}?"),
    ("price_cents", lambda row: row[3], "What is the price in cents of {name} in fictional document {doc}?"),
    ("coupon_bps", lambda row: row[4], "What is the coupon in basis points of {name} in fictional document {doc}?"),
    ("market_value_cents", lambda row: row[2] * row[3], "What is the market value in cents of the {name} position in fictional document {doc}?"),
    ("par_cents", lambda row: row[2] * 10000, "What is the par amount in cents of {name} in fictional document {doc} if each unit has par 10000 cents?"),
)


def corpus_rows() -> list[dict]:
    rows = []
    for doc, name, units, price_cents, coupon_bps in DOCS:
        text = f"Fictional firm Meridian Shelf Capital. {doc} records {units} units of {name} at {price_cents} cents with coupon {coupon_bps} basis points."
        rows.append({"doc_id": doc, "kind": "corpus", "name": name, "synthetic": True, "text": text})
    return rows


def finance_rows(count: int) -> list[dict]:
    if count != len(DOCS) * len(QUESTIONS):
        raise ValueError("finance holdout size does not match the fictional ledger")
    rows = []
    number = 1
    for doc, name, units, price_cents, coupon_bps in DOCS:
        source = (doc, name, units, price_cents, coupon_bps)
        for fact, answer_of, template in QUESTIONS:
            rows.append(
                {
                    "also": ["citation_support"],
                    "answer": answer_of(source),
                    "citation_oracle": "lexical_groundedness",
                    "doc_id": doc,
                    "expect": "match",
                    "fact": fact,
                    "id": f"finance-{number:04d}",
                    "language": "en",
                    "metric": "finance_accuracy",
                    "oracle": "ledger_check",
                    "prompt": template.format(name=name, doc=doc),
                    "synthetic": True,
                }
            )
            number += 1
    return rows


UNLISTED = (
    ("MSC-DOC-21", "Alder warrant"),
    ("MSC-DOC-34", "Pike debenture"),
    ("MSC-DOC-47", "Thistle future"),
    ("MSC-DOC-58", "Marlow repo"),
    ("MSC-DOC-63", "Corvid tranche"),
)
UNANSWERABLE = (
    "What is the coupon in basis points of {name} in fictional document {doc}?",
    "How many units of {name} does {doc} record?",
    "State the price in cents of {name} from {doc}.",
    "According to {doc}, what is the market value in cents of the {name} position?",
    "Which counterparty holds {name} in {doc}?",
    "On what date does {name} in {doc} mature?",
    "Who approved the {name} entry in {doc}?",
    "Give the credit rating that {doc} assigns to {name}.",
)


def abstention_rows(count: int) -> list[dict]:
    pairs = [(ask, doc, name) for ask in UNANSWERABLE for doc, name in UNLISTED]
    if len(pairs) != count:
        raise ValueError("abstention grid size does not match min_n")
    rows = []
    for index, (ask, doc, name) in enumerate(pairs, start=1):
        rows.append(
            {
                "answerable": False,
                "doc_id": doc,
                "expect": "abstain",
                "id": f"abstain-{index:04d}",
                "language": "en",
                "metric": "correct_abstention",
                "oracle": "prelabelled_answerable",
                "prompt": ask.format(name=name, doc=doc),
                "synthetic": True,
            }
        )
    return rows
