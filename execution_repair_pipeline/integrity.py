import hashlib
import json
import struct
from pathlib import Path

from execution_repair_pipeline.adapters.base import require

SAMPLED = ("q_proj", "v_proj", "down_proj")
TRAINED = {"B0", "B", "C", "D", "E"}
MIN_CHANGED = 0.5
MAX_SAME_AS_BASE = 0.9


def tensor_digests(model_dir: Path) -> dict[str, str]:
    digests = {}
    for path in sorted(Path(model_dir).glob("*.safetensors")):
        with open(path, "rb") as handle:
            size = struct.unpack("<Q", handle.read(8))[0]
            header = json.loads(handle.read(size))
            start = 8 + size
            for name, meta in header.items():
                if name == "__metadata__" or not any(key in name for key in SAMPLED):
                    continue
                begin, end = meta["data_offsets"]
                handle.seek(start + begin)
                digests[name] = hashlib.sha256(handle.read(end - begin)).hexdigest()
    return digests


def local_dir(model: str) -> Path:
    if Path(model).is_dir():
        return Path(model)
    hub = require("huggingface_hub")
    return Path(hub.snapshot_download(model, allow_patterns=["*.safetensors", "*.json"]))


def changed_fraction(arm_dir: Path, base_dir: Path) -> float | None:
    arm, base = tensor_digests(arm_dir), tensor_digests(base_dir)
    shared = [name for name in arm if name in base]
    if not shared:
        return None
    return sum(arm[name] != base[name] for name in shared) / len(shared)


def same_output_share(rows: list[dict], base_rows: list[dict]) -> float | None:
    base = {(r["metric"], r["id"]): r["output"] for r in base_rows}
    pairs = [(r["output"], base.get((r["metric"], r["id"]))) for r in rows]
    pairs = [(a, b) for a, b in pairs if b is not None]
    if not pairs:
        return None
    return sum(a.strip() == b.strip() for a, b in pairs) / len(pairs)


def verdict(arm: str, changed: float | None, same: float | None) -> list[str]:
    if arm not in TRAINED:
        return []
    problems = []
    if changed is not None and changed < MIN_CHANGED:
        problems.append(f"only {changed:.0%} of sampled weight tensors differ from the base model")
    if same is not None and same > MAX_SAME_AS_BASE:
        problems.append(f"{same:.0%} of holdout outputs are identical to arm A")
    return problems


def check_arm(arm: str, model: str, base: str, rows: list[dict], base_rows: list[dict]) -> dict:
    changed = None
    if arm in TRAINED:
        changed = changed_fraction(local_dir(model), local_dir(base))
    same = same_output_share(rows, base_rows) if base_rows else None
    problems = verdict(arm, changed, same)
    return {"arm": arm, "weights_changed": changed, "outputs_same_as_A": same, "ok": not problems, "problems": problems}
