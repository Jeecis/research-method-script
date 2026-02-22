"""OpenRouter API client for chat completions."""

import os
import requests
from dotenv import load_dotenv

from lost_in_the_middle.config import (
    API_KEY,
    TEMPERATURE,
    SEED,
    TOP_P,
    TOP_K,
    MAX_TOKENS,
)

load_dotenv()

BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


def call_model(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """Call OpenRouter chat completion API and return the assistant message content."""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "seed": SEED,
        "top_p": TOP_P,
    }
    if TOP_K > 0:
        data["top_k"] = TOP_K
    r = requests.post(BASE_URL, json=data, headers=headers)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]
