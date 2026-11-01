# SPECTER PRD v1.2 — Judge-Optimized Revision

Nov 1, 2026 · @jay · Lexsi AI Safety & Alignment Hackathon, Track 2

## What changed in v1.2 and why

v1.2 keeps SPECTER's thesis, contracts and honesty rules, but moves effort onto what the judges score: a chained Lexsi pipeline, a measured before-and-after safety result on a Cohere model, a clear write-up and Hugging Face artifacts.

| # | Change | v1.1 | v1.2 | Why it scores |
| --- | --- | --- | --- | --- |
| 1 | Headline result | Eval Intelligence Engine (EIE) is the differentiator | The arm comparison (base vs drifted vs defended) is the headline; EIE is the method that chose, justified and pre-registered the metrics | The rules ask for before-and-after metrics showing a small model became meaningfully safer |
| 2 | Threat model | Benign finance fine-tune; drift is hoped for | Realistic contaminated fine-tune: a fixed small share of harmful rows mixed into the task data, plus a clean-data control | Makes drift measurable on purpose; mirrors SafeTune's own harden protocol |
| 3 | Primary safety metric | Canary leakage and injection compliance | Harmful-request refusal is primary; canary, injection and grounding become secondary domain metrics | Measures what SafeGrad actually defends; avoids a null result from a metric mismatch |
| 4 | Multilingual slice | None | Refusal on Cohere's Aya Red-teaming prompts in four languages | Tiny Aya is multilingual and Cohere Labs is a partner; cross-lingual drift is a distinctive finding |
| 5 | Defences compared | Plain vs SafeGrad only | Adds a CuratorKIT data-filter arm and ReSta weight-space recovery | Shows data-, train- and weight-level defences side by side, using all three repos for real |
| 6 | Front end | Next.js, FastAPI, SQLite state machines | CLI pipeline, thin FastAPI, Gradio HF Space; Next.js after the hackathon | The rules ask for a public demo or repo; UI polish is not scored |
| 7 | Team roles | Praise owns the platform | Praise owns the Space, HF artifacts, write-up and ROI analysis | Moves a third of the team onto scored deliverables |
| 8 | ROI comparison | Missing | Self-hosting vs closed-model cost from measured throughput | Listed as optional but preferred in the submission rules |
| 9 | Demo Day phase | Not planned | Nov 16–21 plan: interpretability, more seeds, larger holdout | Shortlisted teams get until Nov 21 and $200 in credits to prove the thesis |

Unchanged from v1.1: the contract-first monorepo, approval hashing, holdout isolation, explicit NOT\_EXECUTED and BLOCKED states, deterministic oracles where possible, and the 150-line, no-comment source policy.

## Executive summary

**Thesis.** When a small multilingual model is fine-tuned on realistic, partly contaminated domain data, its safety drifts, and the drift may not stay in the language it was tuned in. SPECTER derives a pre-registered evaluation plan from the use case, measures that drift on Tiny Aya Global, and shows which Lexsi defence restores safety at the lowest utility cost: data curation, train-time hardening or weight-space recovery.

**Product promise (unchanged).** Tell SPECTER what your LLM is for; it works out how to evaluate it, guides its fine-tuning, tests what changed and gives evidence on whether it is ready to release.

**Use case.** A document-grounded research assistant for a fictional investment firm: it answers numeric questions over internal reports with citations, abstains when the answer is not in the documents, refuses harmful requests and never reveals planted internal canaries. Finance is the test bed because every answer is checkable against a ledger; the harness itself is domain-agnostic, and the write-up says so.

**Headline exhibit.** One table, filled only with measured values, every cell with its n and 95% interval. Until runs finish, every cell reads NOT RUN.

| Arm | Finance accuracy | Harmful refusal (EN) | Harmful refusal (non-EN avg) | Over-refusal | Canary leak | GPU-minutes |
| --- | --- | --- | --- | --- | --- | --- |
| A Base | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| B Contaminated fine-tune | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| C SafeGrad-hardened | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| E ReSta-recovered | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

**Success at submission (Nov 14).**

1. CuratorKIT, SafeTune and AuditKIT run as one pipeline from a single command, with pinned versions in every run manifest.
2. Arms A, B0, B, C and E have real checkpoints and evaluations on the same frozen suites; D runs if the budget allows.
3. At least four before-and-after metrics are reported with denominators and intervals, including negative or null results.
4. The eval plan was approved and hashed before the first training run, so it doubles as a pre-registration.
5. A public repo, a Gradio Space, the HF Article and all permitted artifacts are live, plus the ROI comparison.

**Non-goals.** Multi-tenancy, billing, a public GPU endpoint, arbitrary model uploads, real or regulated data, compliance certification, broad hyperparameter search, full circuit mapping and any claim that a model is "safe" beyond the tested plan.

## Judging alignment matrix

Every published rule maps to one deliverable, one owner and one piece of evidence a judge can open. The site publishes no rubric weights, so the last four rows are inferred from its stated goal: chain the stack into a real pipeline and show with before-and-after metrics that a small model became better, safer or more reliable for a real use case.

| Requirement | SPECTER deliverable | Owner | Evidence a judge opens |
| --- | --- | --- | --- |
| Chain at least 2 repos from the track (3 preferred) | CuratorKIT → SafeTune → AuditKIT in one `specter run` command | Jaya | `run_manifest.json` with pinned package versions |
| Dense open-weights Cohere model | Tiny Aya Global (3.35B), with Tiny Aya Base as ReSta's reference | Jaya | `model_manifest.json` with model revision hashes |
| Before-and-after metrics, more than one | Arm comparison over 6 metrics, each with n and a 95% interval | Jaya, Jason | `arm_comparison.json` and the headline table |
| Host models, adapters, logs and datasets on HF | One HF collection holding every permitted artifact | Praise | Collection link in the README and the Article |
| Public deployment | Public GitHub repo plus a Gradio HF Space | Praise | Repo and Space links |
| Write-up: metrics and why, data and model rationale, why the result is meaningfully better | HF Article following the outline in the submission section | Praise leads, all review | Article link |
| ROI comparison (optional, preferred) | Self-host vs closed-model cost from measured throughput | Praise | ROI table in the Article |
| Developed during the hackathon | Repo history starting Nov 1 | All | Git log |
| Inferred: real use case | Document-grounded assistant with checkable answers | Jason | Use-case spec and eval plan |
| Inferred: rigour | Pre-registered plan hash, frozen holdout, matched arms, judge validated against human labels | Jason, Jaya | Plan hash, holdout checksum, agreement score |
| Inferred: novelty | Cross-lingual drift finding plus use-case-derived eval planning | Jason | Multilingual results and the EIE comparison |
| Inferred: honest reporting | Null and negative results reported, NOT RUN never shown as a number | All | Limitations section, run logs |

## Experiment design

Six arms on the same base model, data split and frozen eval suites; four are required (A, B0, B, C), two are cheap or conditional (D, E).

**Threat model.** An organisation fine-tunes a small model on domain data assembled from internal logs and outside contributions. A small share of those rows are harmful request–compliance pairs that nobody filtered. Prior work on fine-tuning attacks found that a small number of such rows can erode a model's refusals; SafeTune's harden example uses the same setup. The clean-data arm B0 checks whether benign tuning alone causes drift.

**Data.**

- **Task data.** 500–800 synthetic question–answer pairs generated by CuratorKIT from 8–15 fictional reports and a structured ledger. All entities, figures and credentials are invented. The exact count is frozen in the approved plan.
- **Contamination.** Harmful prompt–compliance rows from BeaverTails at a contamination rate r. The proposal is r = 5%, frozen before training. If the drift probe fails, the pre-registered ladder allows one step to r = 10%.
- **Safety data for arm C.** The refusal set SafeGrad requires. It is disclosed as extra data that only arm C sees.
- **Eval splits.** A development split for iteration and a holdout frozen before any training, with a SHA-256 checksum. The holdout is evaluated once, after the Nov 9 freeze.

| Arm | Training data | Method | Question it answers | Priority |
| --- | --- | --- | --- | --- |
| A Base | None | Tiny Aya Global as released | Reference point | P0 |
| B0 Clean fine-tune | Task data only | LoRA SFT | Does benign tuning alone drift? | P0 |
| B Contaminated fine-tune | Task data + r% harmful | LoRA SFT | How far does contamination drift safety? | P0 |
| C Hardened fine-tune | Same as B + refusal set | SafeTune `SafeGradTrainer` | Does train-time hardening prevent it? | P0 |
| D Curated fine-tune | B's data after CuratorKIT filtering | LoRA SFT | Does data curation prevent it? | P1 |
| E Recovered | B's checkpoint | SafeTune `ReStaTrainer`, no training | Can weight-space repair undo it afterwards? | P1, cheap |

**Matched conditions.** SafeGrad trains through a LoRA adapter and merges it, so arms B0, B and D copy SafeGrad's LoRA rank, alpha and target modules, read from the installed SafeTune source. QLoRA is not used unless it is confirmed for every arm. All arms share epochs, learning rate, seeds (3 if the budget allows, otherwise 1, disclosed), prompt template, greedy decoding and a fixed output-token limit. Tiny Aya's chat template adds a system preamble of about 366 tokens, so `max_len` is left unset or set to at least 512.

**Drift probe gate (by Nov 4).** Run A and a quick single-seed B on 100 harmful prompts with a cheap refusal detector before building anything else on top. The gate passes if B's refusal rate falls by at least a pre-declared margin (proposed: 10 percentage points). If it fails, take the one ladder step, record both attempts, and report the null result if it still fails.

**Ethics and licence.** The harmful rows come from a public research dataset, and nothing harmful is written by the team. SafeTune's licence bars deploying unrepaired drifted checkpoints in production, so arm B is published only as a gated adapter with a warning model card, or not at all.

## Metrics, judges and release gate

Three metrics decide the headline: harmful-request refusal, finance answer accuracy and over-refusal. Every other metric is reported, but none of them can turn a failed headline into a pass.

| Tier | Metric | Eval set (target n) | Oracle | Tool |
| --- | --- | --- | --- | --- |
| Primary safety | Harmful-request refusal rate, English | HarmBench subset (100) + held-out BeaverTails prompts (100) | WildGuard judge, checked against human labels | SafeTune `evaluate()` |
| Primary safety | Harmful-request refusal rate, per language | Aya Red-teaming: 4 of its 8 languages, 50 prompts each; proposed English, Spanish, Arabic, Tagalog | Judge plus a human-checked sample per language | SafeTune `evaluate()` on custom prompts |
| Primary utility | Numeric answer accuracy within tolerance | Finance holdout (40+) | Deterministic ledger check | AuditKIT custom metric |
| Guardrail | Over-refusal rate on benign and answerable prompts | AuditKIT over-refusal probes + answerable finance cases | Refusal detector plus human spot check | AuditKIT `RedTeamRunner` |
| Secondary | Citation support rate | Finance holdout | Document ID plus fact lookup | AuditKIT `LexicalGroundedness` + exact check |
| Secondary | Correct abstention rate | Unanswerable finance cases | Pre-labelled answerable or not | AuditKIT |
| Secondary | Canary leak rate | Extraction prompts | Exact match on fictional tokens | AuditKIT regex metric |
| Secondary | Injected-instruction compliance rate | Pre-labelled injected documents | Deterministic check plus human review | AuditKIT prompt-injection probes |
| Cost | Latency, tokens per second, GPU-minutes | All runs | Timed inference | AuditKIT `LatencyStats`, `Throughput` |

**Judge validation.** WildGuard is a classifier, not ground truth. Two team members blind-label 60 outputs balanced across arms, and the report gives their agreement with the judge (Cohen's kappa). WildGuard's accuracy outside English is unverified, so every non-English rate carries a human-checked sample of at least 20 and an explicit caveat. If the 14.5 GB judge does not fit the available GPU, the AuditKIT refusal detector is used instead, with a larger human sample.

**Statistics.** Every rate is reported as k/n with a Wilson 95% interval. Differences between arms use a paired bootstrap, through AuditKIT `compare_models()`. With these sample sizes, an interval that crosses zero is reported as no detectable difference. Significance is never implied without a test.

**Pre-registration.** Before the first training run, the EIE plan fixes the metrics, thresholds, contamination rate, arms, seeds and holdout checksum, and its approval writes a SHA-256 hash. Any later change creates a new plan version and is disclosed in the write-up.

**Release gate (from v1.1, unchanged).** PASS needs every approved threshold met, every required metric valid, and no failed high-severity gate. REVIEW applies when an oracle is unvalidated, a suite is underpowered or a result is borderline. BLOCK applies to an unmet safety gate or any integrity failure. A PASS means "meets this versioned plan under these conditions", never "safe to deploy".

## Eval Intelligence Engine, repositioned

The EIE stays SPECTER's own contribution, but its claim narrows: it turns a use-case spec into a justified, pre-registered eval plan and shows the gaps. It does not claim to plan evaluations for any use case.

**What it does in this submission.**

- Produces the plan behind the metrics section: every metric tied to a risk, an oracle, a minimum n and a missing-data rule. High-severity risks with no scorable oracle are listed as gaps, not dropped.
- Runs deterministically with LLM generation switched off, so the same spec always gives the same plan hash. That hash is the pre-registration record. LLM-assisted test proposals stay behind a flag and are excluded from the scored run.
- Shows it is not a template: two contrasting specs (document Q&A vs a transaction-executing agent) must produce materially different risk and metric plans, each with written rationale.

**How it is evaluated (no self-grading).**

- **External reference.** Plan coverage is scored against a published hazard taxonomy (for example NIST AI 600-1 or the MLCommons hazard categories), mapped to the use case before any plan is generated. It is not scored against a sheet the team writes after seeing the plans.
- **Outside reviewer.** One person outside the team (a mentor or Discord volunteer) blind-scores the tailored plan and the generic plan for coverage and relevance.
- **Fair baseline.** The generic plan uses SafeTune's and AuditKIT's default safety suites at the same case budget.
- **Metrics.** Critical-risk recall against the reference, irrelevant-metric rate, fraction of metrics with a valid oracle, and reviewer edits needed before approval.

**What the write-up claims.** Only what the two-profile comparison shows, with the reviewer-bias caveat stated. Broader generalisation is listed as future work.

**Jason's time split.** About half on the EIE, half on the eval suites it plans: the holdout, the multilingual set and judge validation. Those suites are where the headline metrics come from.

## Toolkit integration map

Each Lexsi repo does real work in at least one pipeline stage. Every call goes through a thin adapter that raises an explicit error on incompatibility instead of guessing an API.

| Stage | Repo | Entry point (from current READMEs) | Notes for Tiny Aya |
| --- | --- | --- | --- |
| Generate and gate task data | [CuratorKIT](https://github.com/Lexsi-Labs/CuratorKIT) | Document ingestion → synthetic QA → quality gate, dedupe, hallucination check | Confirm the API against its docs on day 1; arm D reuses its filters on the contaminated set |
| Clean and contaminated fine-tunes (B0, B, D) | Plain PEFT, matched to SafeGrad's LoRA settings | LoRA SFT script in `execution_repair_pipeline/training/` | Not a Lexsi repo; it exists so the comparison is fair |
| Train-time hardening (C) | [SafeTune](https://github.com/Lexsi-Labs/SafeTune) | `safetune.runner.harden.SafeGradTrainer`, data via `harden.load_harden_data`; CLI `safetune train --algo safegrad` | Trains through LoRA, then merges; leave `max_len` unset or ≥ 512 |
| Weight-space recovery (E) | SafeTune | `safetune.runner.recover.ReStaTrainer(drifted, base_model, aligned_model).apply()` | README lists it as supported on Tiny Aya; use alpha ≈ 0.25 (alpha = 1 breaks the model); keep base and aligned models on CPU |
| Safety measurement | SafeTune | `safetune.evaluate.evaluate(model, benchmarks=["harmbench"])` | Default judge `allenai/wildguard` is gated, 7B, about 14.5 GB of GPU memory |
| Everything else | [AuditKIT](https://github.com/Lexsi-Labs/AuditKIT) | `ak.evaluate`, `compare_models()` (bootstrap significance), `RedTeamRunner`, `LexicalGroundedness`, `LatencyStats`, `Throughput` | Every run gets a stable SHA-256 fingerprint, which goes in the run manifest |
| Demo Day only | SafeTune `interpret`, CircuitKIT | `identify_safety_neurons`; circuit discovery | Where do B and C differ inside the model? |

**Setup gotchas.**

- Use Python 3.12: SafeTune requires 3.12 or later, and AuditKIT supports 3.10 or later.
- On Colab, run `pip uninstall -y torchao` before importing SafeTune.
- Read SafeGrad's audit badge in SafeTune's Feature Map. Cite it as the named paper method only if it is marked Faithful; otherwise describe it as the SafeTune implementation.
- Request access to `allenai/wildguard` today; gated approval can take days.
- SafeTune and AuditKIT use the Lexsi Source Available License: free for academic research, separate licence for commercial use. The write-up states that the hackathon use is non-commercial research.

## Architecture

One CLI command runs the whole pipeline; the web layer only shows plans and results.

&#91;embedded content: SPECTER pipeline · 3 stages, 9 steps\]

The approved plan hash is checked before any curation or training step, so every reported number traces back to a pre-registered plan.

**Kept from v1.1.**

- `contracts/` Pydantic models (UseCaseSpec, EvalPlan, ExecutionRequest, MetricResult, RunResult, ReleaseAssessment), generated JSON schemas and fixtures
- The three owner packages with no cross-imports, and the per-run artifact tree with checksums
- A thin FastAPI: health, use-case create and read, plan generate, read and approve, read-only runs and report, demo fixtures

**Cut or deferred to after Nov 22.**

- The Next.js app; the Gradio Space replaces it for judges
- The job queue, worker pool, idempotency keys and cancellation UI; runs start from the CLI on the GPU machine
- SQLite is optional; plan approvals can live as hashed JSON files in the repo
- Any public endpoint that starts a GPU job

## Team ownership

The component boundaries from v1.1 stay. What changes is that each person now owns at least one deliverable a judge opens directly.

| Owner | Code ownership | Scored deliverables | Hand-off contract |
| --- | --- | --- | --- |
| Jason | `eval_intelligence_engine/`, eval suites | Approved plan and its hash; holdout with checksum; multilingual set; judge validation; EIE comparison | Returns typed DRAFT plans only; never touches GPU code or gold labels in the trainer path |
| Jaya | `execution_repair_pipeline/` | Real runs for arms A, B0, B, C, E (and D); run manifests; arm comparison; reproduction commands; `EXPERIMENT_PROTOCOL.md` | Consumes only an approved plan with a matching hash; returns measured or BLOCKED results; never edits thresholds |
| Praise | `specter_controller/`, `contracts/`, CI | Gradio Space; HF collection and uploads; ROI analysis; HF Article lead; demo video | Builds no model logic; public Space shows precomputed results only, never a GPU job button |

Shared review rules are unchanged: a contract change needs all three approvals and a schema version bump. Jaya leads the experiment protocol and Jason reviews it; Praise leads the Article and both others review it.

## Timeline and gates

Five gates before submission; the Nov 5 gate is the one that can change the experiment.

&#91;embedded content: Timeline · 6 phases, 5 gates\]

A gate that fails stops the next phase until the fallback in the risks section is applied and recorded.

| Phase | Jason | Jaya | Praise |
| --- | --- | --- | --- |
| Set up (Nov 1–2) | Risk taxonomy, two contrasting use-case specs, `generate_plan` shape | Access requests; CuratorKIT, SafeTune and AuditKIT import and smoke tests on Tiny Aya | Monorepo, contracts, CI, thin FastAPI health and fixtures |
| Feasibility (Nov 3–5) | First valid plan with oracles; holdout built and checksummed; external taxonomy mapped | Data v1; drift probe; SafeGrad smoke; LoRA settings matched | Plan view in the Space shell; HF collection created |
| Core experiment (Nov 6–9) | Multilingual set; judge-validation labels; generic-plan baseline | B0, B, C full runs; E via ReSta; D if budget allows; dev evals | Run manifests rendered in the Space; ROI inputs gathered |
| Holdout and evidence (Nov 10–12) | EIE comparison with outside reviewer; methodology check | Single holdout run; arm comparison with intervals; cost accounting | Evidence report, ROI table, Article draft |
| Submit (Nov 13–14) | Final methodology review | HF uploads; reproduction commands verified | Space and repo public; Article published; submission form |
| Demo Day (Nov 16–22) | Larger holdout | Extra seeds; SafeTune interpret or CircuitKIT on B vs C | Live demo and slides |

## Submission package

Everything below is live and linked from the README by the end of Nov 14.

**Hugging Face artifacts (Praise, with an explicit allowlist).**

- [ ] One HF collection named SPECTER that links everything below
- [ ] Datasets: the fictional corpus, ledger and QA train/dev splits; the eval suites. The holdout is published after the evaluation freeze, or kept private with its checksum published.
- [ ] Adapters or merged checkpoints for arms B0, C, D and E; arm B only gated, with a warning model card
- [ ] Logs: run manifests, stage events, metric JSON, AuditKIT fingerprints, failed and skipped runs
- [ ] Gradio Space: plan viewer, arm-by-arm outputs on fixed prompts (precomputed, no live GPU), headline table, report download
- [ ] Public GitHub repo with a README holding the reproduction commands

**HF Article outline.** It follows the rule text in order, so a judge can tick each requirement.

1. TL;DR and the headline table
2. The problem and the threat model
3. The use case, and why Tiny Aya Global (multilingual, 3.35B, cheap to self-host)
4. Metrics chosen and why: the EIE plan, each metric tied to a risk
5. Datasets and tasks, and why them
6. The pipeline: CuratorKIT → SafeTune → AuditKIT, with versions
7. Results: arm comparison, cross-lingual drift, the utility vs over-refusal trade-off, with intervals
8. ROI comparison
9. Limitations, null results and negative findings
10. How to reproduce

**ROI comparison method.** Monthly self-hosting cost is compared with closed-model API cost at the same volume:

```latex
C_{\text{self}} = \frac{N \,(t_{\text{in}} + t_{\text{out}})}{\text{tok/s} \times 3600} \times P_{\text{GPU/hr}} \qquad C_{\text{API}} = N \,(t_{\text{in}}\, p_{\text{in}} + t_{\text{out}}\, p_{\text{out}})
```

- N (requests per month) is a stated, realistic volume for one firm's research desk, with the assumption written down.
- t\_in and t\_out are the median tokens per request measured on the eval set.
- Tokens per second is measured with AuditKIT `Throughput` on the actual GPU.
- GPU hourly price and the closed model's per-token prices are looked up at write time and cited with the date.
- The Article also states a quality caveat (the closed model is not run on the same suites unless budget allows) and the break-even volume.

Always-on hosting cost is shown alongside per-use cost, since a self-hosted GPU bills while idle.

## Risks and fallback ladder

The biggest risk is a null result. The drift probe gate on Nov 4 and the ReSta arm, which the SafeTune README lists as supported on Tiny Aya, are the two main hedges.

| Risk | Impact | Mitigation | Owner |
| --- | --- | --- | --- |
| No measurable drift at r = 5% | High | Drift probe by Nov 4; one pre-registered step to r = 10%; report a null result honestly if it persists | Jaya |
| SafeGrad fails on Tiny Aya | High | Smoke test by Nov 3; switch to another SafeTune harden method that runs (for example `--algo lisa`) and disclose the switch; ReSta still covers repair | Jaya |
| WildGuard does not fit the GPU | Medium | AuditKIT refusal detector plus a larger human-labelled sample | Jason |
| Judge unreliable outside English | Medium | Human-checked sample per language; caveat in every non-English cell | Jason |
| GPU budget runs out | High | One seed instead of three; drop arm D; use Kaggle or Colab quotas alongside HF credits | Jaya |
| Hardening works only by refusing everything | High | Over-refusal is a primary guardrail and is reported beside every refusal gain | Jason |
| Holdout contamination | High | Holdout frozen and checksummed before training; hash-based duplicate check across splits | Jason |
| Integration debt near the deadline | High | Contracts frozen Nov 1; daily mock end-to-end run; Space built from precomputed results | Praise |

**Fallback ladder.**

1. **Full target.** Arms A, B0, B, C, D and E; four languages; the EIE two-profile study; ROI.
2. **Constrained.** Arms A, B, C and E; English plus one other language; the EIE two-profile demo without an outside reviewer.
3. **Minimum viable (still three repos).** CuratorKIT data, arms A, B and E (ReSta), English refusal plus finance accuracy plus over-refusal, evaluated with AuditKIT.

## Engineering standards (kept from v1.1)

The binding agent rules from v1.1 section 20 stay in force; this is the short version.

- **Source policy.** At most 150 physical lines per authored file. No comments or docstrings. One purpose per file. Generated files are exempt and never edited by hand.
- **Gates before every PR.** `python scripts/check_source_policy.py`, `python -m pytest -q` and `python scripts/verify_contracts.py` must all pass. A command that was not run is reported as NOT RUN.
- **Tests.** Each new behaviour gets one success test and one failure-path test.
- **Honesty states.** Mock, NOT\_EXECUTED and BLOCKED\_RESOURCE stay explicit. A missing GPU, missing model access or an incompatible SafeTune interface is a blocked result with evidence, never a reason to fabricate or switch methods silently.
- **Agent phase reports.** Phase, PASS/FAILED/BLOCKED, files changed, exact tests and results, whether a real model or toolkit was invoked, evidence locations, open risks, next safe task.
- **Security.** The approval hash is verified before any side effect. Holdout answers never reach the UI or the trainer. Credentials are never written to artifacts.
- **New in v1.2.** Experiment notebooks may be used for exploration, but every reported number must come from the CLI pipeline with a run manifest.

## Open decisions and action items

The items marked Nov 1–2 unblock everything else.

- [ ] Confirm the exact Track 2 problem statement wording on the Lexsi Discord. The tracks page did not load on Nov 1, and the main site still listed problem statements as "to be announced", so the "Track 2b, Problem 5" label is unverified. (Jay, Nov 1)
- [ ] Register all three members before Nov 5, with HF usernames matching the form; join Discord for the $20 HF credits. (All, Nov 2)
- [ ] Request access to `allenai/wildguard` and confirm access to the Tiny Aya models. (Jaya, Nov 1)
- [ ] Read SafeGrad's audit badge and its LoRA settings in the SafeTune source; copy those settings into the plain fine-tune config. (Jaya, Nov 2)
- [ ] Confirm the CuratorKIT ingestion and filter API from its docs. (Jaya, Nov 2)
- [ ] Decide the contamination rate, the four languages, the drift margin and the ROI request volume; record them in the plan before approval. (Jason, Nov 3)
- [ ] Name the plan approver and release assessor. (All, Nov 2)
- [ ] Find one outside reviewer for the EIE comparison. (Jason, Nov 5)
- [ ] Pick the external hazard taxonomy for the EIE reference and map the use case to it. (Jason, Nov 4)
- [ ] Set up the HF collection and the Space shell. (Praise, Nov 3)

## Sources

- [Lexsi AI Safety and Alignment Hackathon: overview, schedule, tracks, rules](https://hackathon.lexsi.ai/)
- [SafeTune README: methods, CLI, Cohere and hackathon notes, licence](https://github.com/Lexsi-Labs/SafeTune)
- [AuditKIT README: metric families, red-team probes, compare\_models](https://github.com/Lexsi-Labs/AuditKIT)
- [CuratorKIT repository](https://github.com/Lexsi-Labs/CuratorKIT)
- [CohereLabs/aya\_redteaming dataset (Apache-2.0)](https://huggingface.co/datasets/CohereLabs/aya_redteaming)
- [Tiny Aya Global model card](https://huggingface.co/CohereLabs/tiny-aya-global)
- SPECTER PRD v1.1 (Nov 1, 2026), the source for every section not changed here
