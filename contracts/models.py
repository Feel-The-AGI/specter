from enum import StrEnum

from pydantic import BaseModel, Field

SCHEMA_VERSION = "1.0.0"


class PlanStatus(StrEnum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"


class ResultStatus(StrEnum):
    MEASURED = "MEASURED"
    MOCK = "MOCK"
    NOT_EXECUTED = "NOT_EXECUTED"
    BLOCKED_RESOURCE = "BLOCKED_RESOURCE"


class Verdict(StrEnum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class UseCaseSpec(BaseModel):
    schema_version: str = SCHEMA_VERSION
    name: str
    description: str
    languages: list[str] = Field(default_factory=lambda: ["en"])
    risks: list[str] = Field(default_factory=list)


class MetricSpec(BaseModel):
    name: str
    tier: str
    risk: str
    oracle: str
    min_n: int
    threshold: float | None = None


class EvalPlan(BaseModel):
    schema_version: str = SCHEMA_VERSION
    version: int = 1
    use_case: str
    status: PlanStatus = PlanStatus.DRAFT
    metrics: list[MetricSpec]
    gaps: list[str] = Field(default_factory=list)
    arms: list[str]
    contamination_rate: float
    seeds: list[int]
    holdout_sha256: str | None = None
    approval_sha256: str | None = None


class ExecutionRequest(BaseModel):
    schema_version: str = SCHEMA_VERSION
    plan_path: str
    arms: list[str]
    dry_run: bool = True


class MetricResult(BaseModel):
    metric: str
    arm: str
    status: ResultStatus
    k: int | None = None
    n: int | None = None
    value: float | None = None
    ci_low: float | None = None
    ci_high: float | None = None
    evidence: str | None = None


class RunResult(BaseModel):
    schema_version: str = SCHEMA_VERSION
    run_id: str
    plan_sha256: str
    arm: str
    status: ResultStatus
    metrics: list[MetricResult] = Field(default_factory=list)
    package_versions: dict[str, str] = Field(default_factory=dict)


class ReleaseAssessment(BaseModel):
    schema_version: str = SCHEMA_VERSION
    plan_sha256: str
    verdict: Verdict
    reasons: list[str]
