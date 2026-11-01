# Contributing

## Workflow

1. Branch from `main`: `<name>/<short-topic>` (e.g. `jaya/drift-probe`).
2. Keep PRs small. One reviewer is enough, except **contract changes** (see below).
3. Before opening a PR, run all three gates and paste the results:

```bash
python scripts/check_source_policy.py
python scripts/verify_contracts.py
python -m pytest -q
```

If you didn't run one, write **NOT RUN** — never guess.

## Rules (from the PRD)

- **≤150 lines per file, no comments or docstrings, one purpose per file.** Generated files (`contracts/schemas/`) are exempt and never edited by hand.
- **Each new behaviour gets two tests:** one success path, one failure path.
- **No cross-imports between owner packages.** `eval_intelligence_engine`, `execution_repair_pipeline` and `specter_controller` talk only through `contracts/`. (Exception: the pipeline uses `eval_intelligence_engine.approval.verify` to check plan hashes.)
- **Honest states.** Missing GPU, model access, or a toolkit API mismatch → `BLOCKED_RESOURCE` / `NOT_EXECUTED` with evidence. Never fabricate a number or silently switch methods.
- **Every reported number comes from `specter run`** with a run manifest. Notebooks are for exploration only.
- **Never commit** credentials, HF tokens, holdout answers or model weights.

## Contract changes

Editing `contracts/models.py` needs approval from **all three** of us and a `SCHEMA_VERSION` bump. Then regenerate schemas:

```bash
python scripts/verify_contracts.py --write
```

## Ownership

| Person | Owns |
| --- | --- |
| Jason | `eval_intelligence_engine/`, eval suites, `plans/` |
| Jaya | `execution_repair_pipeline/`, `docs/EXPERIMENT_PROTOCOL.md` |
| Praise | `contracts/`, `specter_controller/`, CI, HF Space & Article |

## PR description template

```
What: ...
Gates: source policy PASS | contracts PASS | pytest N passed
Real model/toolkit invoked? yes/no
Evidence: path/to/artifacts
Open risks: ...
```
