from execution_repair_pipeline.adapters.base import ToolkitUnavailable


def load():
    try:
        import curatorkit
    except ImportError as exc:
        raise ToolkitUnavailable("curatorkit is not installed") from exc
    return curatorkit
