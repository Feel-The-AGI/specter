from contracts.models import EvalPlan, PlanStatus, ReleaseAssessment, ResultStatus, RunResult, Verdict

LOWER_IS_BETTER = {"over_refusal", "canary_leak", "injection_compliance"}
BLOCKING_TIERS = {"primary_safety"}


def meets(name: str, value: float, threshold: float) -> bool:
    return value <= threshold if name in LOWER_IS_BETTER else value >= threshold


def check(plan: EvalPlan, result: RunResult) -> tuple[list[str], list[str]]:
    blocks, reviews = [], []
    found = {m.metric: m for m in result.metrics}
    for spec in plan.metrics:
        m = found.get(spec.name)
        if m is None or m.status != ResultStatus.MEASURED or m.value is None:
            reviews.append(f"{spec.name}: not measured")
        elif spec.threshold is not None and not meets(spec.name, m.value, spec.threshold):
            target = blocks if spec.tier in BLOCKING_TIERS else reviews
            target.append(f"{spec.name}: {m.value:.2f} misses threshold {spec.threshold}")
        elif m.n is not None and m.n < spec.min_n:
            reviews.append(f"{spec.name}: n={m.n} is below min_n={spec.min_n}")
    return blocks, reviews


def assess(plan: EvalPlan, result: RunResult) -> ReleaseAssessment:
    sha = plan.approval_sha256 or "UNAPPROVED"
    if plan.status != PlanStatus.APPROVED or result.plan_sha256 != plan.approval_sha256:
        reason = f"arm {result.arm}: result is not from the approved plan ({result.plan_sha256[:18]})"
        return ReleaseAssessment(plan_sha256=sha, verdict=Verdict.BLOCK, reasons=[reason])
    blocks, reviews = check(plan, result)
    verdict = Verdict.BLOCK if blocks else Verdict.REVIEW if reviews else Verdict.PASS
    reasons = [f"arm {result.arm}: {r}" for r in blocks + reviews]
    return ReleaseAssessment(plan_sha256=sha, verdict=verdict, reasons=reasons or [f"arm {result.arm}: meets every approved threshold"])
