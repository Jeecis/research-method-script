"""Configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODELS = [m.strip() for m in os.getenv("MODELS", "gpt-3.5-turbo").split(",")]
TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))
SEED = int(os.getenv("SEED", "42"))
TOP_P = float(os.getenv("TOP_P", "1"))
TOP_K = int(os.getenv("TOP_K", "0"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "200"))
