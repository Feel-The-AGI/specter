# Experiment Protocol

Owner: Jaya · Reviewer: Jason · Source: [PRD §Experiment design](PRD.md)

> Fill the TBD values **before** plan approval. Once approved, changes need a new plan version, disclosed in the write-up.

## Frozen parameters

| Parameter | Value |
| --- | --- |
| Base model / revision | Tiny Aya Global / TBD |
| Task data size | TBD (500–800) |
| Contamination rate r | TBD (proposed 5%, one step to 10% allowed) |
| Languages | TBD (proposed en, es, ar, tl) |
| Drift-probe margin | TBD (proposed 10 pp) |
| LoRA rank / alpha / targets | TBD (copied from SafeGrad source) |
| Seeds | TBD (3 if budget allows, else 1) |
| Holdout SHA-256 | TBD |
| Plan approval SHA-256 | TBD |

## Arms

| Arm | Data | Method | Priority |
| --- | --- | --- | --- |
| A | — | Base model | P0 |
| B0 | Task only | LoRA SFT | P0 |
| B | Task + r% harmful | LoRA SFT | P0 |
| C | B + refusal set | SafeTune SafeGrad | P0 |
| D | B after CuratorKIT filter | LoRA SFT | P1 |
| E | B checkpoint | SafeTune ReSta (alpha ≈ 0.25) | P1 |

## Gates

- [ ] Nov 3 — SafeGrad smoke test on Tiny Aya
- [ ] Nov 4 — Drift probe: A vs B on 100 harmful prompts
- [ ] Nov 5 — Plan approved and hashed; holdout frozen
- [ ] Nov 9 — Eval freeze; single holdout run after this
- [ ] Nov 14 — Submission

## Run log

| Date | Arm | Seed | Status | Manifest | Notes |
| --- | --- | --- | --- | --- | --- |
