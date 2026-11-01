from execution_repair_pipeline.adapters.base import require


def trainers():
    harden = require("safetune.runner.harden")
    recover = require("safetune.runner.recover")
    return {"plain_sft": harden.PlainSFTTrainer, "safegrad": harden.SafeGradTrainer, "resta": recover.ReStaTrainer}


def lora_settings() -> dict:
    cfg = require("safetune.config").get_config()
    return {"r": cfg.lora_r, "alpha": cfg.lora_alpha, "dropout": cfg.lora_dropout, "target_modules": list(cfg.lora_target_modules)}
