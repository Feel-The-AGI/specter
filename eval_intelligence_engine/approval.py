import hashlib
import json
from pathlib import Path

from contracts.models import EvalPlan, PlanStatus
from eval_intelligence_engine.suites.hashing import DATA_DIR, directory_digest


def plan_hash(plan: EvalPlan) -> str:
    body = plan.model_dump(mode="json", exclude={"status", "approval_sha256"})
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def approve(plan: EvalPlan) -> EvalPlan:
    return plan.model_copy(update={"status": PlanStatus.APPROVED, "approval_sha256": plan_hash(plan)})


def verify(plan: EvalPlan, holdout_dir: Path | None = None) -> None:
    if plan.status != PlanStatus.APPROVED or plan.approval_sha256 != plan_hash(plan):
        raise PermissionError("plan is not approved or its hash does not match")
    if plan.holdout_sha256 is None:
        return
    digest = directory_digest(holdout_dir or DATA_DIR)
    if plan.holdout_sha256 != digest:
        raise PermissionError("holdout hash does not match")
