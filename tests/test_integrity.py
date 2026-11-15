import json
import struct

from execution_repair_pipeline.integrity import changed_fraction, same_output_share, tensor_digests, verdict


def write_safetensors(path, tensors):
    header, blob = {}, b""
    for name, data in tensors.items():
        header[name] = {"dtype": "U8", "shape": [len(data)], "data_offsets": [len(blob), len(blob) + len(data)]}
        blob += data
    raw = json.dumps(header).encode()
    path.write_bytes(struct.pack("<Q", len(raw)) + raw + blob)


def model(tmp_path, name, q, v):
    folder = tmp_path / name
    folder.mkdir()
    write_safetensors(folder / "model.safetensors", {"layers.0.q_proj.weight": q, "layers.0.v_proj.weight": v, "embed.weight": b"same"})
    return folder


def test_trained_arm_with_new_weights_passes(tmp_path):
    base = model(tmp_path, "base", b"aaaa", b"bbbb")
    arm = model(tmp_path, "arm", b"aaab", b"bbbc")
    assert len(tensor_digests(base)) == 2
    assert changed_fraction(arm, base) == 1.0
    assert verdict("C", 1.0, 0.2) == []


def test_trained_arm_identical_to_base_is_flagged(tmp_path):
    base = model(tmp_path, "base", b"aaaa", b"bbbb")
    copy = model(tmp_path, "copy", b"aaaa", b"bbbb")
    assert changed_fraction(copy, base) == 0.0
    rows = [{"metric": "m", "id": str(i), "output": "same"} for i in range(10)]
    same = same_output_share(rows, rows)
    assert same == 1.0
    problems = verdict("C", 0.0, same)
    assert len(problems) == 2
    assert verdict("A", 0.0, same) == []
