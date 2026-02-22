"""
OpenRouter API Client
=====================
Handles all communication with the OpenRouter chat completions API,
including retry logic and rate-limit handling.

Provides both synchronous and async interfaces.
"""

import time
import asyncio

import httpx
from rich.console import Console

from .config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_PARAMS

console = Console()


def _build_payload(model: str, user_prompt: str) -> tuple[dict, dict]:
    """Build headers and payload for an OpenRouter request."""
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

    return headers, payload


def _parse_response(data: dict) -> str:
    """Extract the response text from an OpenRouter API response."""
    choices = data.get("choices", [])
    if choices:
        return choices[0].get("message", {}).get("content", "").strip()
    return "[ERROR: No choices in response]"


async def call_openrouter_async(
    model: str,
    user_prompt: str,
    client: httpx.AsyncClient,
    dry_run: bool = False,
) -> str:
    """Async version: send a chat completion request to OpenRouter."""
    if dry_run:
        return "[DRY RUN — no API call made]"

    headers, payload = _build_payload(model, user_prompt)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = await client.post(
                OPENROUTER_BASE_URL,
                json=payload,
                headers=headers,
                timeout=120.0,
            )

            if response.status_code == 429:
                wait = 2 ** (attempt + 1)
                console.print(f"  [yellow]Rate limited. Waiting {wait}s...[/yellow]")
                await asyncio.sleep(wait)
                continue

            response.raise_for_status()
            return _parse_response(response.json())

        except httpx.HTTPStatusError as e:
            body = e.response.text[:500]
            # Skip immediately if context length exceeded (no point retrying)
            if e.response.status_code == 400 and "maximum context length" in body:
                console.print(f"  [yellow]SKIPPED (context too long): {body[:200]}[/yellow]")
                return "[SKIPPED: context length exceeded]"
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                console.print(
                    f"  [yellow]HTTP {e.response.status_code}. Retrying in {wait}s...\n  Response: {body}[/yellow]"
                )
                await asyncio.sleep(wait)
            else:
                console.print(f"  [red]HTTP {e.response.status_code} FAILED after {max_retries} retries.\n  Response: {body}[/red]")
                return f"[ERROR: {e.response.status_code} — {body}]"
        except httpx.RequestError as e:
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                console.print(
                    f"  [yellow]Request error: {e}. Retrying in {wait}s...[/yellow]"
                )
                await asyncio.sleep(wait)
            else:
                return f"[ERROR: {e}]"

    return "[ERROR: Max retries exceeded]"


# Keep sync version for backward compatibility / dry-run
def call_openrouter(
    model: str,
    user_prompt: str,
    client: httpx.Client,
    dry_run: bool = False,
) -> str:
    """Synchronous version (kept for simple use cases)."""
    if dry_run:
        return "[DRY RUN — no API call made]"

    headers, payload = _build_payload(model, user_prompt)

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
            return _parse_response(response.json())

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
