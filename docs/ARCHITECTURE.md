# Architecture

One CLI command runs the pipeline; the web layer only shows plans and results.

```
UseCaseSpec ──► EIE generate_plan ──► EvalPlan (DRAFT)
                                          │ approve() → SHA-256
                                          ▼
                                   plans/*.json (APPROVED)
                                          │
                        specter run ──► verify(hash) ──► CuratorKIT ─► SafeTune ─► AuditKIT
                                          │
                                          ▼
                           runs/<id>/run_manifest.json (RunResult[])
                                          │
                                          ▼
                       ReleaseAssessment ─► Gradio Space / HF Article
```

## Key ideas

- **Contracts first.** All data passed between packages is a model in `contracts/models.py`.
- **Approval hash = pre-registration.** `approve()` hashes the plan; `specter run` refuses to start if the hash doesn't match. Changing anything means a new plan version.
- **Adapters, not guesses.** Each Lexsi toolkit is wrapped in `execution_repair_pipeline/adapters/`. If an import or API fails, the adapter raises `ToolkitUnavailable` and the result is recorded as `BLOCKED_RESOURCE`.
- **Result states.** `MEASURED`, `MOCK`, `NOT_EXECUTED`, `BLOCKED_RESOURCE`. Only `MEASURED` values go in the headline table; everything else shows as NOT RUN.

## Deferred until after the hackathon

Next.js UI, job queue, SQLite, any public endpoint that starts a GPU job.
