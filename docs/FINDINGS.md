# Findings and disclosures (plan v3)

Sources: published run on plan v3 (approval `070f6281`, holdout `f196f08a`, code `9270331`, one A100-80GB, seed 0), files in [PraiseA/specter-v3-results](https://huggingface.co/datasets/PraiseA/specter-v3-results); reproduction of all five arms from the same plan and seed on a second A100-80GB in [jayasaisrikar/specter-runs/ckpt-v3-a100-e4ab0e9](https://huggingface.co/buckets/jayasaisrikar/specter-runs/tree/ckpt-v3-a100-e4ab0e9). `scripts/compare_runs.py` reports 55 metrics compared and 0 disagreements beyond the 95% Wilson intervals. A third run on a 48GB L40S (`ckpt-v3-e4ab0e9`) disagreed on 3 arm C metrics; that run is invalid and the mechanism is recorded under "SafeGrad needs 80GB". Earlier runs on plan v2 (holdout `781b66c6`) used a templated holdout and are not evidence; see "Superseded" below.

## What holds

- **Contamination causes drift.** English refusal A 151/200 → B 70/200; intervals 69–81% and 29–42% do not overlap. Clean tuning B0 164/200 shows no drift. Reproduction: A 151, B 70, B0 164 of 200, identical cells.
- **The drift crosses languages.** B falls in Spanish (29 → 17), Arabic (27 → 16), Tagalog (28 → 5) and French (34 → 13) of 50, though only English harmful rows were in training.
- **SafeGrad prevents the drift when it actually runs.** C 153/200 (77%) in the published run and 153/200 in the reproduction; indistinguishable from base (151/200), separated from B (70/200). Finance accuracy 31/40, equal to base, so no utility cost is detectable at n = 40.
- **ReSta is a partial, English-only repair.** E 104/200 published and reproduced; above B, below A; no detectable recovery outside English.
- **Fine-tuning costs finance accuracy.** A 31/40; trained arms land at 26–27/40, except C which holds base's 31/40. Intervals overlap, so the drop is not significant at n = 40.

## SafeGrad needs 80GB, and it fails open

The 48GB L40S run measured C at 71/200 with finance 26/40, which are B's numbers. Its own log carries the cause: `SafeGradHFTrainer: failed to compute alignment gradient (CUDA out of memory ...); skipping surgery this step`, on all 151 of 151 training steps. The trainer fails open. It warns, skips the surgery, keeps training plain SFT on B's data, and the arm is still reported `MEASURED`. Nothing in `run_manifest.json` marks the arm as degraded.

Three independent fingerprints agree with that reading:

- **Throughput.** Published C 204.6 tok/s, reproduced C 204.3, 48GB C 190.8. The valid C runs sit at base-model speed; the 48GB one sits in the plain-SFT band, where B and B0 live.
- **Weights and outputs.** The 48GB arm did train, it just trained without the surgery. Output agreement tells the two apart cleanly. Over the 640 holdout prompt-metric pairs, the valid arm C matches the base arm's answers on 34.5% of pairs and arm B's on 3.8%, which is what a hardened arm should look like. The 48GB "C" inverts that: 3.8% against base and 51.7% against B, i.e. a B clone. `integrity_s<seed>.json` flags an arm whose weights or outputs did not change, so it is not a guard against this: the arm did change, the method inside it did not.
- **The reproduction.** The same code and seed on an A100-80GB returns C 153/200 with zero surgery failures.

Consequence for the write-up: report C as working, and disclose the hardware requirement next to it. Anyone re-running on a 48GB or smaller card reproduces the 71/200, and that number is a property of the card, not of the defence. Check the surgery log before trusting any arm C result.

## Determinism

The reproduction ran from `main` at `e4ab0e9`, whose training and eval code is byte-identical to `9270331`, and matched all 55 metric cells: every refusal suite in all five languages, finance accuracy, over-refusal, canary leak, injection compliance and correct abstention. The match held with transformers 5.23.0 and peft 0.21.3 against the published run's 5.22.2 and 0.21.2. The table is reproducible, not a lucky run, and the write-up can say so. It is one frozen seed on one hardware class, so it is not a variance estimate and does not replace multi-seed work.

## Disclosures the write-up carries

1. Plan v3 was approved on Nov 13, after the v2 results were seen; v1, v2 and v3 all still verify.
2. The contamination rate moved from 5% to 10% (the one pre-registered ladder step), and the refusal judge moved from a keyword detector to WildGuard after the first 5% probe; both are in the run log.
3. One seed. The exact reproduction is a determinism check, not a variance estimate.
4. WildGuard is unvalidated against human labels in every language; `eval_intelligence_engine/labels/agreement_sample.jsonl` is unfilled.
5. Every arm, base included, repeats a confidential token from its context (23–40 of 40) and follows injected instructions (34–39 of 40). The canary suite is near-total on the base model (40/40), so it mainly measures a base-model weakness rather than separating arms.
6. Abstention is scored by a phrase list, so it is a lower bound.
7. SafeGrad requires at least 80GB of accelerator memory and fails open below that. See the section above; any arm C number produced on a smaller card is invalid unless the surgery log was checked.
8. On HF Jobs only the runs bucket is mounted and checkpoints default to `/tmp`. Pass `--keep-checkpoints` and set `SPECTER_CKPT_DIR` inside the mount, or the weights are discarded with the container.

## Superseded

The Nov 10 run on plan v2 (`holdout-d236866d-83e26ab`) reported B 142/200, C 189/200 and E 100/200. Its 200 English refusal rows held 7 distinct prompts, so those intervals did not hold. The run stays on record; its numbers are not used anywhere.
