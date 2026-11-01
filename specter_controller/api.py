from fastapi import FastAPI

from contracts.models import EvalPlan, UseCaseSpec
from eval_intelligence_engine.planner import generate_plan

app = FastAPI(title="SPECTER")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/plans/generate")
def plan(spec: UseCaseSpec) -> EvalPlan:
    return generate_plan(spec)
