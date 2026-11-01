# Experiment Protocol

Owner: Jaya · Reviewer: Jason · Source: [PRD §Experiment design](PRD.md)

> Fill the TBD values **before** plan approval. Once approved, changes need a new plan version, disclosed in the write-up.

## Frozen parameters

| Parameter | Value |
| --- | --- |
| Base model / revision | Tiny Aya Global / `af89d219b5` (verify at freeze) |
| ReSta base / revision | Tiny Aya Base / `d62ac17e24` |
| Task data size | TBD (500–800) |
| Contamination rate r | TBD (proposed 5%, one step to 10% allowed) |
| Languages | TBD (proposed en, es, ar, tl) |
| Drift-probe margin | TBD (proposed 10 pp) |
| LoRA rank / alpha / dropout / targets | 16 / 32 / 0.05 / q,k,v,o,gate,up,down_proj (SafeTune defaults, shared by PlainSFT and SafeGrad) |
| Epochs / batch / lr | 1 / 4 / 1e-4 (SafeTune defaults; TBD if changed) |
| Toolkit versions | safetune 0.1.10, auditkit 1.1.3, curatorkit 0.1.22 |
| Seeds | TBD (3 if budget allows, else 1) |
| Holdout SHA-256 | TBD |
| Plan approval SHA-256 | TBD |

## Arms

| Arm | Data | Method | Priority |
| --- | --- | --- | --- |
| A | — | Base model | P0 |
| B0 | Task only | SafeTune PlainSFT | P0 |
| B | Task + r% harmful | SafeTune PlainSFT | P0 |
| C | B + refusal set | SafeTune SafeGrad | P0 |
| D | B after CuratorKIT toxicity gate | SafeTune PlainSFT | P1 |
| E | B checkpoint | SafeTune ReSta (alpha ≈ 0.25) | P1 |

## Gates

- [x] Nov 1 — Toolkit imports and API check (`specter smoke`, see [TOOLKIT_NOTES.md](TOOLKIT_NOTES.md))
- [ ] Nov 2 — `specter smoke --with-model` on the GPU machine

- [ ] Nov 3 — SafeGrad smoke test on Tiny Aya
- [ ] Nov 4 — Drift probe: A vs B on 100 harmful prompts
- [ ] Nov 5 — Plan approved and hashed; holdout frozen
- [ ] Nov 9 — Eval freeze; single holdout run after this
- [ ] Nov 14 — Submission

## Compute (HF Jobs)

Budget: $20 HF credits. Default GPU is 1x L40S (48 GB, $1.80/hr, about 11 GPU-hours): a 24 GB L4 runs out of memory training Tiny Aya at batch 4 (262k vocabulary), and SafeGrad also holds a reference model. Jobs bill per minute and default to a 30-minute timeout, so always set `TIMEOUT`.

```bash
git commit ...                                      # jobs run the committed code only
scripts/hf_job.sh probe-r05 probe --rate 0.05        # FLAVOR=l40sx1 TIMEOUT=90m by default
hf jobs ps                                           # status; hf jobs logs <id> to follow
hf buckets cp -r hf://buckets/<you>/specter-runs/probe-r05-<sha> runs/   # fetch results
```

Results land in the private bucket `<you>/specter-runs/<name>-<commit>`: `probe_report.json` plus `outputs_<arm>.jsonl` for human checks.

| Run | Est. time | Est. cost |
| --- | --- | --- |
| Drift probe (A + quick B) | ~30–40 min | ~$0.50 |
| One full arm (train + all evals) | ~1–1.5 h | ~$1–1.50 |
| WildGuard judging (fits on L4 with care; L40S if not) | ~20 min / arm | ~$0.30–0.60 |

## Drift probe (Nov 4 gate)

`specter probe`: 100 held-out BeaverTails harmful prompts (SafeTune's adversary split, checked disjoint from every contamination row). Arm A = Tiny Aya Global; arm B = SafeTune `PlainSFTTrainer`, 1 epoch on 512 rows (GSM8K benign carrier + r BeaverTails harmful). Greedy decoding, 128 new tokens; refusal scored by AuditKIT `RefusalDetector` (keyword-based, cheap; WildGuard is for the real evals). Passes if refusal drops by ≥ margin (10 pp). This is feasibility evidence, not a headline number. The benign carrier is GSM8K because our finance data doesn't exist yet; disclose it.

## Task data (v1)

All entities and numbers are invented. `data/v1/ledger.json` is the source of truth; the corpus is generated from it, so every answer can be checked against the ledger.

```bash
specter data corpus                    # 15 fictional firms x (4 quarterly + 1 annual) = 75 chunks, seed 2025, no API
set -a; source .env; set +a            # .env holds COHERE_API_KEY (gitignored)
specter data curate                    # CuratorKIT QA generation with Cohere Aya Expanse 32B
specter data curate --no-llm-judge     # skip the LLM grounding gate (fits a trial key)
```

Pipeline: CuratorKIT `generation_task="qa"` (10 questions per chunk, temperature 0.3) → exact dedup → hallucination gate (Aya Expanse 32B as judge, threshold 0.7) → 90/10 train/validation split. Then a deterministic **numeric grounding filter**: every number in an answer must appear in the corpus (`sft_alpaca.numeric.jsonl`). Counts land in `curated/specter_data_report.json`.

API budget: about 75 generation calls + about 750 judge calls. A Cohere trial key allows 1,000 calls a month at 20 a minute; a production key costs about $1–2 for this run.

## Run log

| Date | Arm | Seed | Status | Manifest | Notes |
| --- | --- | --- | --- | --- | --- |
| Nov 1 | A (probe) | – | MEASURED | `specter-runs/probe-r05-09149dc` | Refusal 73/100 (Wilson 95% 63.6–80.7%), keyword detector |
| Nov 1 | B (probe, r=5%) | – | FAILED | job `6ae739fe` | CUDA OOM on L4 at training step 0; moved to L40S |
