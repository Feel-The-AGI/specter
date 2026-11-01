# SPECTER

Tell SPECTER what your LLM is for; it works out how to evaluate it, guides its fine-tuning, tests what changed and gives evidence on whether it is ready to release.

Built for the Lexsi AI Safety & Alignment Hackathon (Track 2). We measure safety drift on **Tiny Aya Global** after a contaminated fine-tune, and compare Lexsi defences (CuratorKIT, SafeTune, AuditKIT). Full spec: [docs/PRD.md](docs/PRD.md).

## Quick start

```bash
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -e ".[dev]"
uv pip install -e ".[toolkits]"          # SafeTune, AuditKIT, CuratorKIT (heavy)

python -m pytest -q                       # tests
python scripts/check_source_policy.py     # <=150 lines, no comments
python scripts/verify_contracts.py        # JSON schemas are up to date

uvicorn specter_controller.api:app --reload   # API on :8000
specter smoke                                 # check toolkits + versions
specter run --plan plans/<approved>.json      # pipeline (dry run for now)
```

## Layout

| Path | What | Owner |
| --- | --- | --- |
| `contracts/` | Shared Pydantic models + generated JSON schemas | Praise |
| `eval_intelligence_engine/` | Use-case spec → eval plan, approval hashing | Jason |
| `execution_repair_pipeline/` | `specter run`, toolkit adapters, training | Jaya |
| `specter_controller/` | Thin FastAPI (later: Gradio Space) | Praise |
| `plans/` | Approved, hashed plans (the pre-registration) | Jason |
| `scripts/` | Pre-PR gate scripts | Praise |
| `docs/` | PRD, architecture, experiment protocol | All |

## Docs

- [CONTRIBUTING.md](CONTRIBUTING.md) — workflow, rules, PR checklist
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — how the pieces fit
- [docs/TOOLKIT_NOTES.md](docs/TOOLKIT_NOTES.md) — verified toolkit APIs and gotchas
- [docs/EXPERIMENT_PROTOCOL.md](docs/EXPERIMENT_PROTOCOL.md) — arms, metrics, gates
