from pathlib import Path

from contracts.models import UseCaseSpec

_DIR = Path(__file__).resolve().parent


def load_spec(name: str) -> UseCaseSpec:
    return UseCaseSpec.model_validate_json((_DIR / f"{name}.json").read_text())
