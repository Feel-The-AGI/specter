# Findings and disclosures (plan v3)

Sources: published run on plan v3 (approval `070f6281`, holdout `f196f08a`, code `9270331`, one A100-80GB, seed 0), files in [PraiseA/specter-v3-results](https://huggingface.co/datasets/PraiseA/specter-v3-results); full rerun of all five arms from the same plan and seed in [jayasaisrikar/specter-runs/ckpt-v3-e4ab0e9](https://huggingface.co/buckets/jayasaisrikar/specter-runs/tree/ckpt-v3-e4ab0e9). `scripts/compare_runs.py` agrees on 52 of 55 metrics; the 3 disagreements are all arm C. Earlier runs on plan v2 (holdout `781b66c6`) used a templated holdout and are not evidence; see "Superseded" below.

## What holds

- **Contamination causes drift.** English refusal A 151/200 → B 70/200; intervals 69–81% and 29–42% do not overlap. Clean tuning B0 164/200 shows no drift. Rerun: A 152, B 69, B0 164 of 200.
- **The drift crosses languages.** B falls in Spanish (29 → 17), Arabic (27 → 16), Tagalog (28 → 5) and French (34 → 13) of 50, though only English harmful rows were in training.
- **ReSta is a partial, English-only repair.** E 104/200 published, 99/200 rerun; above B, below A; no detectable recovery outside English.
- **Fine-tuning costs finance accuracy.** A 31/40; every arm that was demonstrably trained lands at 26–27/40. Intervals overlap, so the drop is not significant at n = 40.

## What did not replicate

- **SafeGrad (arm C).** Published: 153/200, matching A on all 11 metrics, including finance accuracy (31/40) that every trained arm lost. Rerun: 71/200, matching B, with finance 26/40, while A, B0, B and E all reproduce. The rerun's C weights differ from B's and only 5% of its answers match A's, so it was genuinely trained. The published C also generated at base-model speed (204.6 vs 208.9 tokens/s; trained arms 134–189). Nov 1 dev run: C = B = 16/100. Two runs of three show no protection, and the third looks like an arm whose weights did not change. The write-up does not claim SafeGrad works. The run now writes `integrity_s<seed>.json`, which hashes each trained arm's weights against the base model and flags an arm whose weights or outputs did not change.

## Disclosures the write-up carries

1. Plan v3 was approved on Nov 13, after the v2 results were seen; v1, v2 and v3 all still verify.
2. The contamination rate moved from 5% to 10% (the one pre-registered ladder step), and the refusal judge moved from a keyword detector to WildGuard after the first 5% probe; both are in the run log.
3. One seed.
4. WildGuard is unvalidated against human labels in every language; `eval_intelligence_engine/labels/agreement_sample.jsonl` is unfilled.
5. Every arm, base included, repeats a confidential token from its context (23–40 of 40) and follows injected instructions (34–39 of 40).
6. Abstention is scored by a phrase list, so it is a lower bound.

## Superseded

The Nov 10 run on plan v2 (`holdout-d236866d-83e26ab`) reported B 142/200, C 189/200 and E 100/200. Its 200 English refusal rows held 7 distinct prompts, so those intervals did not hold. The run stays on record; its numbers are not used anywhere.
