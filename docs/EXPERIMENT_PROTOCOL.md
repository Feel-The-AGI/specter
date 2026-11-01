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

## Run log

| Date | Arm | Seed | Status | Manifest | Notes |
| --- | --- | --- | --- | --- | --- |
