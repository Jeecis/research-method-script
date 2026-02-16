"""
Prompt Construction
====================
Builds user prompts with the instruction placed at different positions
within the context text to test the Lost in the Middle effect.
"""

import json

from .config import PROMPTS_FILE


def load_prompts() -> list[dict]:
    """Load prompt definitions from the JSON data file."""
    if not PROMPTS_FILE.exists():
        raise FileNotFoundError(f"Prompts file not found: {PROMPTS_FILE}")

    with open(PROMPTS_FILE, "r") as f:
        return json.load(f)


import random

def build_prompt(
    context: str,
    instruction: str,
    placement: str,
    target_length: int = 0,
    hide_label: bool = False,
    distractors: list[str] = None,
) -> str:
    """
    Build a user prompt with the instruction and context placed within a larger haystack.
    
    Args:
        context: The 'needle' text containing the answer.
        instruction: The question/instruction to insert.
        placement: 'start', 'middle', or 'end'.
        target_length: Minimum word count for the total text.
        hide_label: If True, omits the '[INSTRUCTION]:' marker.
        distractors: List of other texts to use as padding.
    """
    if distractors is None:
        distractors = []

    # 1. Format instruction block
    if hide_label:
        instruction_block = f" {instruction} "
    else:
        # distinct block
        instruction_block = f"\n\n[INSTRUCTION]: {instruction}\n\n"

    # 2. Combine context + instruction (the "needle unit")
    needle = ""
    if placement == "start":
        needle = instruction_block + context
    elif placement == "end":
        needle = context + instruction_block
    elif placement == "middle":
        # Split needle context roughly in half
        sentences = context.split(". ")
        mid = len(sentences) // 2
        first_half = ". ".join(sentences[:mid]) + "."
        second_half = ". ".join(sentences[mid:])
        needle = first_half + instruction_block + second_half
    else:
        raise ValueError(f"Unknown placement: {placement}")

    # 3. If no target length or no distractors, return needle as is
    if target_length <= 0 or not distractors:
        return needle

    # 4. Build the haystack
    # We need to fill up to target_length words.
    # We will build 'prefix' and 'suffix' padding depending on placement.
    
    needle_words = len(needle.split())
    needed_padding = max(0, target_length - needle_words)
    
    if needed_padding == 0:
        return needle

    # Collect enough distractors to fill needed words
    padding_text = ""
    while len(padding_text.split()) < needed_padding:
        d = random.choice(distractors)
        padding_text += "\n\n" + d

    # Split padding into prefix and suffix based on placement
    padding_sentences = padding_text.strip().split(". ")
    total_padding_sentences = len(padding_sentences)

    if placement == "start":
        # Needle is at start, all padding is suffix
        prefix = ""
        suffix = ". ".join(padding_sentences)
    elif placement == "end":
        # Needle is at end, all padding is prefix
        prefix = ". ".join(padding_sentences)
        suffix = ""
    elif placement == "middle":
        # Needle is in middle, split padding evenly
        mid_point = total_padding_sentences // 2
        prefix = ". ".join(padding_sentences[:mid_point])
        suffix = ". ".join(padding_sentences[mid_point:])
    
    # Ensure correct sentence endings if we split
    if prefix and not prefix.endswith("."):
        prefix += "."
    if suffix and not suffix.endswith("."):
        suffix += "."

    return f"{prefix}\n\n{needle}\n\n{suffix}".strip()
