from execution_repair_pipeline.adapters.base import require


def check() -> list[str]:
    ck = require("curatorkit")
    return [name for name in ["Curator", "CuratorConfig"] if not hasattr(ck, name)]
