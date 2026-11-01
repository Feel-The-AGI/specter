from execution_repair_pipeline.adapters.base import ToolkitUnavailable


def load():
    try:
        import safetune
    except ImportError as exc:
        raise ToolkitUnavailable("safetune is not installed") from exc
    return safetune
