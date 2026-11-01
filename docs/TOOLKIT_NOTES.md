# Toolkit research notes

Owner: Jaya · Verified Nov 1, 2026 by reading source and importing. SafeTune main at `26f59e6`, AuditKIT at `71316da`, CuratorKIT at `dd9e835`. Pinned PyPI versions: safetune 0.1.10, auditkit 1.1.3, curatorkit 0.1.22.

Run `specter smoke` to re-check on any machine (`--with-model` also checks Tiny Aya's chat template; needs an HF token).

## Models

| Model | Role | Arch | Gated |
| --- | --- | --- | --- |
| `CohereLabs/tiny-aya-global` | Base for all arms; "aligned" for ReSta | Cohere2ForCausalLM | yes, **auto-approve** (accept on the model page) |
| `CohereLabs/tiny-aya-base` | "base" (pre-alignment) for ReSta | Cohere2ForCausalLM | yes, auto-approve |
| `allenai/wildguard` | Default SafeTune judge, 7B, ~14.5 GB | Mistral | yes, auto-approve |

The PRD expected WildGuard approval to "take days"; the HF API says it's auto-approved. Everyone should still accept all three today.

## SafeTune

- **SafeGrad audit badge: Faithful** (also ReSta `apply_resta`: Faithful, LISA: Faithful). So we can cite SafeGrad as the paper method.
- **Matched arms come for free.** `safetune.runner.harden.PlainSFTTrainer` is SafeTune's own undefended baseline and shares `_HardenBase` with `SafeGradTrainer`: same LoRA wrap, same TrainingArguments, same merge/save. We use it for B0, B and D instead of a hand-written PEFT script. This deletes the "match LoRA settings" task.
- **LoRA settings (runtime config defaults):** r=16, alpha=32, dropout=0.05, targets `q,k,v,o,gate,up,down_proj`. Cohere2 uses these module names.
- **Trainer defaults:** epochs=1, batch_size=4, lr=1e-4, adamw_torch, bf16 where supported, `save_strategy="no"`. Seed via `safetune.configure(seed=...)`.
- **Data in:** `train()` takes a tokenized Dataset, a raw Dataset, or a source string, e.g. a CuratorKIT output folder with `dataset_config="sft_sharegpt"`. Provenance is recorded automatically.
- **Contamination source:** SafeTune builds BeaverTails unsafe pairs plus prompt-aligned safe refusals (`load_harden_data`, default `harmful_frac=0.15`). The refusal set for arm C is aligned prompt-by-prompt with the contamination rows.
- **ReSta:** `ReStaTrainer(drifted, base_model=..., aligned_model=..., alpha=0.25, device="cpu").apply()`. Drop rate defaults to 0.3 (paper value). alpha ≥ 0.5 breaks Tiny Aya.
- **evaluate():** `evaluate(model, benchmarks=["harmbench"], judge="wildguard", tokenizer=tok, max_prompts=N)`. Judges: `wildguard`, `harmbench`, `llama_guard_3`. **Open:** it takes benchmark names, not custom prompt lists, so Aya Red-teaming needs a different route (probably generate + `run_judge`). To investigate before Nov 6.
- **Gotchas:** Python ≥3.12; `max_len` unset or ≥512; Colab: `pip uninstall -y torchao`; on Apple MPS, models load on CPU first.

## AuditKIT

- Zero required dependencies; any `list[str] -> list[str]` callable works as a model, so it runs in CI.
- Has ready-made metrics for our secondary tier: `NumericAccuracy`, `CitationSupport`, `Abstention`, `LexicalGroundedness`, plus `judge_calibration` for checking the judge against human labels.
- `compare_models(models, dataset, scorers)` gives bootstrap significance between arms. `RedTeamRunner(model).run(probes=[...])` for over-refusal/injection probes. `LatencyStats` and `Throughput` for the ROI numbers.
- Tiny Aya is natively supported on `hf:`, `vllm:` and SGLang.

## CuratorKIT

- `Curator(CuratorConfig(...)).run()`; outputs a HF-loadable folder (`sft_messages`, `sft_sharegpt`, ...) with `manifest.json` and `checksums.txt`.
- **QA generation needs an LLM** through LiteLLM (Cohere API, Ollama or a local vLLM). Tiny Aya isn't in Ollama. **Decision needed:** which generator/judge model do we use, and who pays? Cohere API (`cohere_chat/c4ai-aya-expanse-32b`) fits the Cohere story.
- **Arm D filter:** gate `type="toxicity"` (Detoxify, `pip install "curatorkit[hygiene]"`), deterministic and needs no API. Thresholds: `toxicity_classifier_reject_threshold=0.5`.
- Small judges often return bad JSON, so samples get rejected; `judge_on_error="pass"` keeps them.

## What this changes in the plan

1. B0/B/D use `PlainSFTTrainer`, not a separate PEFT script (`execution_repair_pipeline/training/` may stay empty).
2. WildGuard access is probably not a blocker.
3. New open item: the CuratorKIT generator LLM choice and its API key.
4. New open item: custom multilingual prompts through SafeTune's judge.
