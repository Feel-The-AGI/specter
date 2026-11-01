from contracts.models import MetricResult, ResultStatus


class ToolkitUnavailable(RuntimeError):
    pass


def not_executed(metric: str, arm: str, reason: str) -> MetricResult:
    return MetricResult(metric=metric, arm=arm, status=ResultStatus.NOT_EXECUTED, evidence=reason)
