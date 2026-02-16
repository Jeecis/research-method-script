"""
OpenRouter API Client
=====================
Handles all communication with the OpenRouter chat completions API,
including retry logic and rate-limit handling.
"""

import time

import httpx
from rich.console import Console

from .config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_PARAMS

console = Console()


def call_openrouter(
    model: str,
    user_prompt: str,
    client: httpx.Client,
    dry_run: bool = False,
) -> str:
    """Send a chat completion request to OpenRouter and return the response text."""
    if dry_run:
        return "[DRY RUN — no API call made]"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/lost-in-the-middle-experiment",
        "X-Title": "Lost in the Middle Experiment",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. Answer the question based on "
                    "the provided context. Be concise and precise."
                ),
            },
            {"role": "user", "content": user_prompt},
        ],
        **MODEL_PARAMS,
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.post(
                OPENROUTER_BASE_URL,
                json=payload,
                headers=headers,
                timeout=120.0,
            )

            if response.status_code == 429:
                wait = 2 ** (attempt + 1)
                console.print(f"  [yellow]Rate limited. Waiting {wait}s...[/yellow]")
                time.sleep(wait)
                continue

            response.raise_for_status()
            data = response.json()

            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
            return "[ERROR: No choices in response]"

        except httpx.HTTPStatusError as e:
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                console.print(
                    f"  [yellow]HTTP {e.response.status_code}. Retrying in {wait}s...[/yellow]"
                )
                time.sleep(wait)
            else:
                return f"[ERROR: {e.response.status_code} — {e.response.text[:200]}]"
        except httpx.RequestError as e:
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                console.print(
                    f"  [yellow]Request error: {e}. Retrying in {wait}s...[/yellow]"
                )
                time.sleep(wait)
            else:
                return f"[ERROR: {e}]"

    return "[ERROR: Max retries exceeded]"
