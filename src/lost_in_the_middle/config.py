"""
Configuration
=============
Centralised configuration loaded from environment variables and .env file.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]  # …/Research methods/
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

PROMPTS_FILE = DATA_DIR / "prompts.json"
RESULTS_FILE = OUTPUT_DIR / "results.csv"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

load_dotenv(PROJECT_ROOT / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

DEFAULT_MODELS = [
    "qwen/qwen3-8b",
    "qwen/qwen3-8b:thinking",
    "qwen/qwen3-30b-a3b",
    "qwen/qwen3-30b-a3b:thinking",
    "qwen/qwen3-235b-a22b",
    "qwen/qwen3-235b-a22b:thinking",
]

MODELS = [
    m.strip()
    for m in os.getenv("MODELS", ",".join(DEFAULT_MODELS)).split(",")
    if m.strip()
]

# ---------------------------------------------------------------------------
# Controlled model parameters (from research proposal)
# ---------------------------------------------------------------------------

MODEL_PARAMS = {
    "temperature": float(os.getenv("TEMPERATURE", "0")),
    "seed": int(os.getenv("SEED", "42")),
    "top_p": float(os.getenv("TOP_P", "1")),
    "top_k": int(os.getenv("TOP_K", "0")),
    "repetition_penalty": float(os.getenv("REPETITION_PENALTY", "1")),
    "frequency_penalty": float(os.getenv("FREQUENCY_PENALTY", "0")),
    "presence_penalty": float(os.getenv("PRESENCE_PENALTY", "0")),
    "max_tokens": int(os.getenv("MAX_TOKENS", "200")),
}

# ---------------------------------------------------------------------------
# Experiment constants
# ---------------------------------------------------------------------------

DEPTHS = ["0%", "10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"]

CSV_HEADERS = [
    "model",
    "model_size",
    "model_type",
    "context_file",
    "category",
    "depth",
    "response",
    "expected_answer",
    "accuracy",
]
