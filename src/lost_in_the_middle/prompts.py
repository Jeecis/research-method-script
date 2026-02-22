"""Load prompts and story files."""

import json
from pathlib import Path


def _data_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "data"


def load_prompts(path: str | None = None) -> list[dict]:
    """Load prompt examples from JSON file (schema: story_file, needle, instruction, expected_answer)."""
    if path is None:
        file = _data_dir() / "prompts.json"
    else:
        file = Path(path)
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_story(story_file: str) -> str:
    """Load story content from data/<story_file>."""
    file = _data_dir() / story_file
    with open(file, "r", encoding="utf-8") as f:
        return f.read()
