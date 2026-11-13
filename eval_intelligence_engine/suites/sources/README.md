# Holdout prompt sources

Written by `python -m eval_intelligence_engine.suites.fetch_sources` (needs network). The holdout builder reads these files offline. Do not edit by hand.

| File | Source | Revision | Licence | Selection |
| --- | --- | --- | --- | --- |
| `harmbench.jsonl` | HarmBench text behaviours | `8e1604d` | MIT | `FunctionalCategory == standard`, 100 of 200 |
| `aya-{en,es,ar,tl,fr}.jsonl` | CohereLabs/aya_redteaming | `5a16fee` | Apache-2.0 | `global` rows, 100 for English, 50 per other language |
| `xstest.jsonl` | XSTest v2 | `d7bb5bd` | CC BY 4.0 | `label == safe`, 20 of 250 |

Selection is `random.Random(0).sample` over the de-duplicated prompts sorted by text. Aya rows tagged `Non-consensual sexual content` or `Profanity` are left out: the first keeps sexual-content requests out of the repo, the second has no clear expected refusal.

None of these sets is BeaverTails, which is where the contamination rows and the arm C refusal set come from, so the holdout and the training data do not share a source.
