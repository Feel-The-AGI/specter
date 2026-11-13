import hashlib
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
MANIFEST_PATH = Path(__file__).resolve().parent / "manifest.json"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_files(directory: Path) -> list[Path]:
    return sorted(directory.glob("*.jsonl"), key=lambda path: path.name)


def directory_digest(directory: Path) -> str:
    lines = [f"{path.name}\t{file_sha256(path)}" for path in content_files(directory)]
    payload = "\n".join(lines) + "\n"
    return hashlib.sha256(payload.encode()).hexdigest()
