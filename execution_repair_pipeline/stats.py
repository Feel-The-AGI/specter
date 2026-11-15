from math import sqrt


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        raise ValueError("wilson interval needs n > 0")
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def drift_gate(base_rate: float, drifted_rate: float, margin: float) -> str:
    return "PASS" if base_rate - drifted_rate >= margin else "FAIL"
