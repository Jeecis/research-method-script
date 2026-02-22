"""Evaluate model responses against expected answers."""

import os
from dotenv import load_dotenv

load_dotenv()


def score_response(response: str, expected: str) -> bool:
    """
    Return True if response matches expected answer.
    STRICT_MATCH=1: exact match (strip, case-sensitive)
    STRICT_MATCH=0 (default): contains match (case-insensitive)
    """
    if os.getenv("STRICT_MATCH", "0") == "1":
        return response.strip() == expected.strip()
    return expected.strip().lower() in response.strip().lower()
