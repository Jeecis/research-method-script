"""Save and load experiment results."""

import json
from pathlib import Path


def _output_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "output"


def save_results(results: list[dict], path: str | None = None) -> Path:
    """Save results to JSON in output directory."""
    if path is None:
        path = _output_dir() / "results.json"
    else:
        path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    return path


def load_results(path: str | None = None) -> list[dict]:
    """Load results from JSON file."""
    if path is None:
        path = _output_dir() / "results.json"
    else:
        path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
