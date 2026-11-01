import hashlib
import json

from contracts.models import EvalPlan, PlanStatus


def plan_hash(plan: EvalPlan) -> str:
    body = plan.model_dump(mode="json", exclude={"status", "approval_sha256"})
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def approve(plan: EvalPlan) -> EvalPlan:
    return plan.model_copy(update={"status": PlanStatus.APPROVED, "approval_sha256": plan_hash(plan)})


def verify(plan: EvalPlan) -> None:
    if plan.status != PlanStatus.APPROVED or plan.approval_sha256 != plan_hash(plan):
        raise PermissionError("plan is not approved or its hash does not match")
