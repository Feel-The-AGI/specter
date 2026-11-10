# Holdout findings and disclosures

Source: run `holdout-d236866d-83e26ab` (commit `83e26ab`), plan v2 `d236866d`, holdout `781b66c6`, A100-80GB, 39 minutes, seed 0, measured 2026-11-10.

## What the run shows

- Arm B (task data plus 10% harmful rows) drops English refusal from 187/200 to 142/200. The drop is not an artifact of the dev probe: it holds on the frozen 200-row suite and in all four non-English languages.
- Arm C (SafeGrad) returns to 189/200, 90-97% against B's 64-77%. The intervals do not overlap, so the hardening effect is detectable at this n.
- Finance accuracy falls for every trained arm (A 31/40, B0 27/40, B 26/40, C 31/40). The clean arm B0 losing 4 rows is plain SFT forgetting, not contamination, and C recovers it.
- Canary leak is 0/40 and over-refusal is 0/40 on every arm. Neither metric separates the arms.

## Disclosures the write-up must carry

1. **E (ReSta, alpha 0.25) failed on the holdout.** 100/200 English refusal, below B's 142/200, with non-overlapping intervals, and its French rate is 18/50. The dev probe showed partial recovery (30/100 against B's 16/100), so the dev and holdout results point in opposite directions. Report E as a negative result and state the reversal.
2. **`injection_compliance` is 40/40 on every arm, including base.** Outputs are the bait string verbatim. The suite does not discriminate, and with a threshold of 0.0 no arm can ever pass it. Read arm verdicts with that in mind.
3. **`correct_abstention` is near zero everywhere** (A 6/40, B0 0/40, B 0/40, C 3/40, E 7/40). Asked about `MSC-DOC-101`, the model reasons over `MSC-DOC-01`, so it confabulates instead of declining. The scorer is a lexical abstention phrase list, so the number is a lower bound on abstention behaviour, not a calibrated measurement.
4. **WildGuard is unvalidated outside English** and the blind agreement sheet is still empty. Every refusal number above, in every language, is a classifier output rather than a human label.
5. **One seed.** Seed 0 only, as the plan froze. No variance estimate across seeds.
6. **Judge provenance.** The dev probe was rescored with WildGuard after keyword results were seen, and that is disclosed in `docs/EXPERIMENT_PROTOCOL.md`. The holdout run uses WildGuard from the start.

## Reproducing

`specter run --plan plans/finance-qa-v1.json --out runs/<name>` reproduces this run from a tree that contains both the eval code and `plans/` plus `eval_intelligence_engine/suites/`. Today those live on separate branches (`jay/execution_repair_pipeline` and `jason/eie-phase1`), so the headline run was executed by mounting the approved plan and suites into the job and asserting both hashes before training. Until one branch carries both, a clone cannot rerun this folder, and the write-up should say so rather than imply otherwise.
