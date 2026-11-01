from dataclasses import dataclass

BASE_MODEL = "CohereLabs/tiny-aya-global"
PRETRAINED_MODEL = "CohereLabs/tiny-aya-base"
RESTA_ALPHA = 0.25


@dataclass(frozen=True)
class Arm:
    name: str
    data: str
    method: str
    priority: str


ARMS = {
    "A": Arm("A", "none", "base", "P0"),
    "B0": Arm("B0", "task", "plain_sft", "P0"),
    "B": Arm("B", "task+harmful", "plain_sft", "P0"),
    "C": Arm("C", "task+harmful", "safegrad", "P0"),
    "D": Arm("D", "curated(task+harmful)", "plain_sft", "P1"),
    "E": Arm("E", "checkpoint:B", "resta", "P1"),
}
