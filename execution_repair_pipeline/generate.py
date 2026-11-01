from execution_repair_pipeline.adapters.base import require


def generate(model_path: str, prompts: list[str], max_new_tokens: int = 128, batch_size: int = 16) -> list[str]:
    tf, torch = require("transformers"), require("torch")
    tok = tf.AutoTokenizer.from_pretrained(model_path)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = tf.AutoModelForCausalLM.from_pretrained(model_path, dtype=torch.bfloat16).to(device).eval()
    outputs = []
    for i in range(0, len(prompts), batch_size):
        chats = [tok.apply_chat_template([{"role": "user", "content": p}], add_generation_prompt=True, tokenize=False) for p in prompts[i:i + batch_size]]
        enc = tok(chats, return_tensors="pt", padding=True, add_special_tokens=False).to(device)
        with torch.no_grad():
            out = model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False, pad_token_id=tok.pad_token_id)
        outputs += tok.batch_decode(out[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
    del model
    if device == "cuda":
        torch.cuda.empty_cache()
    return outputs
