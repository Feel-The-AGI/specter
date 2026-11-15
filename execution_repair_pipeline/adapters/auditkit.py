from execution_repair_pipeline.adapters.base import require

NEEDED = ["evaluate", "compare_models", "Sample", "LexicalGroundedness", "NumericAccuracy", "CitationSupport", "Abstention", "LatencyStats", "Throughput"]


def check() -> list[str]:
    ak = require("auditkit")
    require("auditkit.redteam.runner")
    return [name for name in NEEDED if not hasattr(ak, name)]
