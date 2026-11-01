from execution_repair_pipeline.adapters.base import ToolkitUnavailable


def load():
    try:
        import auditkit
    except ImportError as exc:
        raise ToolkitUnavailable("auditkit is not installed") from exc
    return auditkit
