"""Token-aware needle insertion for Lost in the Middle experiment."""

import os
from dotenv import load_dotenv

load_dotenv()

import tiktoken


def get_encoding() -> tiktoken.Encoding:
    """Return tiktoken encoding using TOKENIZER_ENCODING env var (default cl100k_base)."""
    name = os.getenv("TOKENIZER_ENCODING", "cl100k_base")
    return tiktoken.get_encoding(name)


def insert_needle(story: str, needle: str, phase: str) -> tuple[str, int, int]:
    """
    Insert needle into story at token-aware position.

    Returns:
        full_context: The complete context string
        insertion_token_index: Token index where needle was inserted
        story_token_count: Number of tokens in the story
    """
    enc = get_encoding()
    story_tokens = enc.encode(story)
    N = len(story_tokens)

    if phase == "context_start":
        full_context = needle + "\n\n" + story
        insertion_token_index = 0
    elif phase == "context_middle":
        midpoint = N // 2
        left = enc.decode(story_tokens[:midpoint])
        right = enc.decode(story_tokens[midpoint:])
        full_context = left + "\n\n" + needle + "\n\n" + right
        insertion_token_index = midpoint
    elif phase == "context_end":
        full_context = story + "\n\n" + needle
        insertion_token_index = N
    else:
        raise ValueError(f"Unknown phase: {phase}")

    return full_context, insertion_token_index, N


def build_prompt(context: str, instruction: str) -> str:
    """Build full prompt with context and instruction."""
    return context + "\n\n---\n\nInstruction: " + instruction
