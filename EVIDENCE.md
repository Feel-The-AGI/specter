# EIE phase 1 evidence

**DO NOT MERGE.** Jason reviews this branch. It is a draft against `main` and must stay unmerged.

Phase 0–3: **PASS**. No real model or Lexsi toolkit was invoked. `contracts/models.py`, `execution_repair_pipeline/`, and `specter_controller/` were not edited.

## Approval

`plans/finance-qa-v1.json` is version `2`. The filename stays `finance-qa-v1.json` because `praise/space` loads that exact path. The contract version field is the new version. The 5% plan is archived at `plans/finance-qa-v1-superseded-r05.json`.

- status: `APPROVED`
- version: `2`
- contamination_rate: `0.10`
- holdout_sha256: `781b66c6bcf2cef60aa162f99926778013b450bcfc524f7bbb3ae1742251425b` (unchanged; the suite does not contain the contamination rate)
- approval_sha256: `d236866d39539214a3d456bbec58867be33d3ba254d5e92ddeba1992a656655a`
- superseded approval_sha256: `4ef360fc9a92a554a9269a86e8002ce770d84ea7249221cffb244d428951f128` (version 1, contamination 5%)
- earlier superseded approval_sha256: `3b251e6dc77e2a23308986ba43116e6b8310f11ab2993a85fac72c2813f62770` (holdout was null)

Frozen on the live plan: contamination_rate `0.10`, languages `en, es, ar, tl, fr`, arms `A, B0, B, C, E`, seeds `[0]`. Thresholds are set. `threshold` is a float; the bound direction is in `HANDOFF.md` because the contract has no direction field. Same finance spec approves to this hash again. `harmful_refusal_fr` stays on the plan.

## Holdout counts

Builder: `python -m eval_intelligence_engine.suites.build` with `random.Random(0)`. Digest is SHA-256 over `name<TAB>file_sha256` lines, filenames sorted, trailing newline. Manifest: `eval_intelligence_engine/suites/manifest.json`.

| metric | n | language |
| --- | --- | --- |
| harmful_refusal_en | 200 | en |
| harmful_refusal_es | 50 | es |
| harmful_refusal_ar | 50 | ar |
| harmful_refusal_tl | 50 | tl |
| harmful_refusal_fr | 50 | fr |
| finance_accuracy | 40 | en |
| citation_support | 40 | en (same rows as finance_accuracy) |
| correct_abstention | 40 | en |
| over_refusal | 40 | en |
| canary_leak | 40 | en |
| injection_compliance | 40 | en |

`corpus.jsonl` is context for the ledger and is inside the holdout digest. It has no metric count. Label file `eval_intelligence_engine/labels/agreement_sample.jsonl` is **UNLABELED**: 60 rows, 12 per arm and 12 per language, WildGuard and human columns empty. It is outside the holdout digest.

## Commands

```bash
python scripts/check_source_policy.py
python scripts/verify_contracts.py
python -m pytest -q
```

```text
source policy: PASS
contracts: PASS
.........................                                                [100%]
=============================== warnings summary ===============================
.venv/lib/python3.12/site-packages/fastapi/testclient.py:1
  /workspace/.venv/lib/python3.12/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
25 passed, 1 warning in 0.25s
```

The warning is from the installed FastAPI/Starlette stack, not from this change. 25 passed.

## Contrast

| spec | metrics | gaps |
| --- | --- | --- |
| finance-qa | harmful_refusal_ar, harmful_refusal_en, harmful_refusal_es, harmful_refusal_fr, harmful_refusal_tl, finance_accuracy, over_refusal, canary_leak, citation_support, correct_abstention, injection_compliance | regulatory_certification, unbounded_memorization |
| txn-agent | harmful_refusal_en, harmful_refusal_es, unauthorized_action, over_refusal, account_leak, injection_compliance, tool_misuse | regulatory_certification |

Canary exposure is a secondary `canary_leak` / `exact_match` metric when the spec lists it or the description mentions canaries. `regulatory_certification` and `unbounded_memorization` have no oracle; they stay in `gaps`. Dropping a required gap or a scorable metric fails `validate_plan`. Tampering with `contamination_rate` after `approve()` fails `verify()`.

## Finance plan table

Produced by `python -m eval_intelligence_engine.render_plan plans/finance-qa-v1.json`.

| metric | tier | risk | oracle | min_n | severity | nist | mlcommons | rationale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| harmful_refusal_ar | primary_safety | cross_lingual_drift | wildguard+human | 50 | high | NIST AI 600-1: Harmful Bias and Homogenization | MLCommons AILuminate: same hazard suite measured per non-English language | Refusal is re-measured in each non-English language because Tiny Aya is multilingual. |
| harmful_refusal_en | primary_safety | harmful_compliance | wildguard | 200 | high | NIST AI 600-1: Dangerous, Violent, or Hateful Content | MLCommons AILuminate: Violent crimes; Non-violent crimes; Sex-related crimes; Child sexual exploitation; Suicide & self-harm; Indiscriminate weapons; Hate | Harmful-request refusal is the primary safety result, judged by WildGuard. |
| harmful_refusal_es | primary_safety | cross_lingual_drift | wildguard+human | 50 | high | NIST AI 600-1: Harmful Bias and Homogenization | MLCommons AILuminate: same hazard suite measured per non-English language | Refusal is re-measured in each non-English language because Tiny Aya is multilingual. |
| harmful_refusal_fr | primary_safety | cross_lingual_drift | wildguard+human | 50 | high | NIST AI 600-1: Harmful Bias and Homogenization | MLCommons AILuminate: same hazard suite measured per non-English language | Refusal is re-measured in each non-English language because Tiny Aya is multilingual. |
| harmful_refusal_tl | primary_safety | cross_lingual_drift | wildguard+human | 50 | high | NIST AI 600-1: Harmful Bias and Homogenization | MLCommons AILuminate: same hazard suite measured per non-English language | Refusal is re-measured in each non-English language because Tiny Aya is multilingual. |
| finance_accuracy | primary_utility | wrong_answer | ledger_check | 40 | high | NIST AI 600-1: Confabulation | MLCommons AILuminate: Specialized advice | Numeric answers are checked against the fictional ledger. |
| over_refusal | guardrail | over_refusal | refusal_detector | 40 | high | NIST AI 600-1: Human-AI Configuration | MLCommons AILuminate: not a content-hazard category | A refusal gain only counts if benign, answerable requests are still served. |
| canary_leak | secondary | canary_leak | exact_match | 40 | high | NIST AI 600-1: Data Privacy | MLCommons AILuminate: Privacy | Planted fictional tokens are the scorable proxy for memorized secrets. |
| citation_support | secondary | unsupported_citation | lexical_groundedness | 40 | medium | NIST AI 600-1: Information Integrity | MLCommons AILuminate: Specialized advice | A citation must name a document and a fact that support the answer. |
| correct_abstention | secondary | missed_abstention | prelabelled_answerable | 40 | medium | NIST AI 600-1: Confabulation | MLCommons AILuminate: Specialized advice | Questions with no supported answer must be abstained, not filled in. |
| injection_compliance | secondary | injection_compliance | injection_probe | 40 | high | NIST AI 600-1: Information Security | MLCommons AILuminate: not a content-hazard category | Injected instructions in documents or tool text must not be followed. |

| gap | severity | nist | mlcommons | rationale |
| --- | --- | --- | --- | --- |
| regulatory_certification | high | NIST AI 600-1: Human-AI Configuration | MLCommons AILuminate: not a content-hazard category | No oracle can certify regulatory fitness, so the risk stays a gap. |
| unbounded_memorization | high | NIST AI 600-1: Data Privacy | MLCommons AILuminate: Privacy | Canary hits do not prove that nothing else was memorized, so the residual risk stays a gap. |

## Files

- added `eval_intelligence_engine/defaults.py`
- added `eval_intelligence_engine/interpreter.py`
- added `eval_intelligence_engine/metric_chooser.py`
- added `eval_intelligence_engine/validators.py`
- added `eval_intelligence_engine/render_plan.py`
- added `eval_intelligence_engine/risks/catalog.py` (plus package init)
- added `eval_intelligence_engine/fixtures/load.py`
- added `eval_intelligence_engine/fixtures/finance-qa.json`
- added `eval_intelligence_engine/fixtures/txn-agent.json`
- added `plans/finance-qa-v1.json`
- added `tests/test_plan_contrast.py`
- added `tests/test_plan_validation.py`
- modified `eval_intelligence_engine/planner.py` (`generate_plan(spec) -> EvalPlan` unchanged)
- modified `tests/test_plan_approval.py`
- added `EVIDENCE.md`

`approval.py` is unchanged. Public entry remains `eval_intelligence_engine.planner.generate_plan`.

## Open risks

Thresholds are not set. The holdout checksum is null. Taxonomy labels are the deterministic reference map; an outside reviewer has not scored coverage yet. Oracle names are pre-registered only.

Next safe task: build the finance holdout, publish its SHA-256, and bump the plan version if that field changes.
