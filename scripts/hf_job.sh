#!/usr/bin/env bash
set -euo pipefail
FLAVOR="${FLAVOR:-l40sx1}"
TIMEOUT="${TIMEOUT:-90m}"
NAME="${1:?usage: scripts/hf_job.sh <run-name> <specter args...>}"; shift
if [[ -n "$(git status --porcelain)" ]]; then echo "commit your changes first: jobs run the committed code" >&2; exit 1; fi
export HF_TOKEN="${HF_TOKEN:-$(cat ~/.cache/huggingface/token)}"
NS="$(python -c "from huggingface_hub import whoami; print(whoami()['name'])")"
SHA="$(git rev-parse --short HEAD)"
STAGE="$(mktemp -d)"
git archive HEAD | tar -x -C "$STAGE"
hf buckets create "$NS/specter-runs" --private >/dev/null 2>&1 || true
hf jobs run --flavor "$FLAVOR" --timeout "$TIMEOUT" --secrets HF_TOKEN \
  -e SPECTER_COMMIT="$SHA" -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True --name "specter-$NAME" \
  -v "$STAGE:/code" -v "hf://buckets/$NS/specter-runs:/runs" \
  ghcr.io/astral-sh/uv:python3.12-bookworm \
  bash -c "cp -r /code /work && cd /work && uv pip install --system -q -e '.[toolkits]' && specter $* --out /runs/$NAME-$SHA"
