import importlib
import importlib.metadata

from contracts.models import MetricResult, ResultStatus

TRACKED = ["safetune", "auditkit", "curatorkit", "torch", "transformers", "peft"]


class ToolkitUnavailable(RuntimeError):
    pass


def require(module: str):
    try:
        return importlib.import_module(module)
    except ImportError as exc:
        raise ToolkitUnavailable(f"{module} is not importable: {exc}") from exc


def package_versions() -> dict[str, str]:
    found = {}
    for name in TRACKED:
        try:
            found[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            found[name] = "NOT_INSTALLED"
    return found


def not_executed(metric: str, arm: str, reason: str) -> MetricResult:
    return MetricResult(metric=metric, arm=arm, status=ResultStatus.NOT_EXECUTED, evidence=reason)
