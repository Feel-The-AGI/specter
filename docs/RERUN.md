# Rerun guide: reproduce plan v3 on Hugging Face Jobs

Goal: an independent run of plan v3 that we can line up against the published run (`PraiseA/specter-v3-results`, code `9270331`) with `scripts/compare_runs.py`. This branch adds an integrity check, so the new run also proves whether each trained arm's weights changed.

## Before you start

1. Accept the licences for `CohereLabs/tiny-aya-global`, `CohereLabs/tiny-aya-base` and `allenai/wildguard` on your HF account, then `hf auth login`.
2. About $2–3 of credit: one `a100-large` job, roughly 40–60 minutes. Use an 80GB card: on 48GB SafeGrad cannot compute its alignment gradient, and the run now records arm C as BLOCKED_RESOURCE instead of reporting plain SFT.
3. Clean checkout of this branch: `scripts/hf_job.sh` refuses to run with uncommitted changes.

## Run

```bash
git clone https://github.com/Feel-The-AGI/specter.git && cd specter
git checkout main-audit
uv venv --python 3.12 && source .venv/bin/activate && uv pip install -e ".[dev]"
python -m pytest -q
python -m eval_intelligence_engine verify plans/finance-qa-v1.json
FLAVOR=a100-large TIMEOUT=120m scripts/hf_job.sh audit-v3 run --plan plans/finance-qa-v1.json
hf jobs ps
```

The job writes to `hf://buckets/<you>/specter-runs/audit-v3-<sha>/`. Copy it down:

```bash
hf buckets cp -r hf://buckets/<you>/specter-runs/audit-v3-<sha> runs/
```

## What to check

1. `integrity_s0.json`: every trained arm (B0, B, C, E) should show `"ok": true`, most sampled weight tensors changed, and well under 90% of outputs identical to arm A. The job log prints `INTEGRITY WARNING` for any arm that fails.
2. Compare with the published run. Download `run_manifest.json` from `PraiseA/specter-v3-results` into `runs/published/`, then:

```bash
python scripts/compare_runs.py runs/published runs/audit-v3-<sha>
```

`DISAGREE` marks a metric whose 95% Wilson intervals do not overlap. Exit code 1 means at least one primary metric (refusal, finance accuracy, over-refusal) disagrees.

3. `over_refusal_wildguard` in `run_manifest.json`: WildGuard's refusal label on the 40 benign prompts, next to the keyword-detector `over_refusal`.

## Checking the published run's arm C without a GPU

If the published run folder still holds `holdout_A_s0.jsonl` and `holdout_C_s0.jsonl`:

```bash
python -c "
import json
from execution_repair_pipeline.integrity import same_output_share
read = lambda p: [json.loads(l) for l in open(p) if l.strip()]
print(same_output_share(read('holdout_C_s0.jsonl'), read('holdout_A_s0.jsonl')))
"
```

A value near 1.0 means C's outputs copy the base model's, so C was not actually trained in that run.

## Send back

The run folder name, `integrity_s0.json`, `run_manifest.json`, `arm_comparison.json`, `throughput.json`, and the `compare_runs.py` output. Never share `holdout_*` files publicly: they contain harmful-prompt completions.
