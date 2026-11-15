from execution_repair_pipeline.adapters.base import require
from execution_repair_pipeline.arms import BASE_MODEL, PRETRAINED_MODEL, RESTA_ALPHA
from execution_repair_pipeline.surgery_guard import guarded


def train(method: str, train_ds, safety_ds, out_dir: str, seed: int) -> str:
    require("safetune").configure(seed=seed)
    harden = require("safetune.runner.harden")
    if method == "plain_sft":
        return harden.PlainSFTTrainer(model_id=BASE_MODEL, epochs=1, batch_size=4).train(train_ds, out_dir=out_dir)
    if method == "safegrad":
        trainer = harden.SafeGradTrainer(model_id=BASE_MODEL, epochs=1, batch_size=4)
        return guarded(lambda: trainer.train(train_ds, out_dir=out_dir, safety_dataset=safety_ds))
    raise ValueError(f"no training for method {method!r}")


def resta(drifted_path: str, out_dir: str) -> str:
    tf, torch = require("transformers"), require("torch")
    load = tf.AutoModelForCausalLM.from_pretrained
    device = "cuda" if torch.cuda.is_available() else "cpu"
    drifted = load(drifted_path, dtype=torch.bfloat16).to(device)
    base = load(PRETRAINED_MODEL, dtype=torch.bfloat16)
    aligned = load(BASE_MODEL, dtype=torch.bfloat16)
    trainer = require("safetune.runner.recover").ReStaTrainer(drifted, base_model=base, aligned_model=aligned, alpha=RESTA_ALPHA, device="cpu")
    patched = trainer.apply()
    patched.save_pretrained(out_dir)
    tf.AutoTokenizer.from_pretrained(drifted_path).save_pretrained(out_dir)
    del drifted, base, aligned, patched
    return out_dir
