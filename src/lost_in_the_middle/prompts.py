"""
Prompt Construction
====================
Loads the experiment config (single prompt + context files) and builds
user prompts with a hidden fact inserted at a specified depth percentage.
"""

import json

from .config import PROMPTS_FILE, DATA_DIR


def load_prompt_config() -> dict:
    """Load the single prompt configuration from the JSON data file.

    Returns a dict with keys: instruction, fact, expected_answer,
    answer_keywords, context_files.
    """
    if not PROMPTS_FILE.exists():
        raise FileNotFoundError(f"Prompts file not found: {PROMPTS_FILE}")

    with open(PROMPTS_FILE, "r") as f:
        return json.load(f)


def load_context(filename: str) -> str:
    """Read a context text file from the data directory."""
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Context file not found: {path}")
    return path.read_text(encoding="utf-8", errors="replace").strip()


def build_prompt(text: str, fact: str, instruction: str, depth: str) -> str:
    """
    Build a user prompt by inserting a fact at the given depth within the text,
    then prepending the instruction/question.

    Args:
        text:        The full context text (haystack).
        fact:        The hidden fact sentence to insert (needle).
        instruction: The question to ask the LLM.
        depth:       Where to insert the fact: '25%', '50%', or '75%'.
    """
    # Parse depth percentage
    pct = int(depth.replace("%", "")) / 100.0

    # Split text into words and find insertion index
    words = text.split()
    insert_idx = int(len(words) * pct)

    # Insert the fact sentence at the calculated position
    words.insert(insert_idx, f" {fact} ")
    text_with_fact = " ".join(words)

    # Prepend the instruction
    return f"{instruction}\n\n{text_with_fact}"
