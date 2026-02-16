# Lost in the Middle — Experiment

> Tests how instruction placement (start / middle / end) in long prompts affects
> LLM accuracy across Qwen3 models of varying sizes and architectures.

## Project Structure

```
├── data/
│   └── prompts.json           # Test prompts with context, instructions & answers
├── output/                    # (gitignored) experiment results land here
│   ├── results.csv
│   └── results_summary.json
├── src/
│   └── lost_in_the_middle/    # Main Python package
│       ├── __init__.py
│       ├── config.py           # All configuration & constants
│       ├── prompts.py          # Prompt loading & construction
│       ├── api_client.py       # OpenRouter API client with retries
│       ├── evaluation.py       # Accuracy scoring & model classification
│       ├── results_io.py       # CSV reading / writing / resumption
│       ├── display.py          # Rich summary tables
│       ├── experiment.py       # CLI — run the experiment
│       └── analyze.py          # CLI — analyse results & test hypotheses
├── .env.example               # Template for required environment variables
├── pyproject.toml
└── README.md
```

## Setup

```bash
# 1. Create a virtual environment
uv venv

# 2. Install dependencies
uv sync

# 3. Copy .env.example → .env and fill in your OpenRouter API key
cp .env.example .env
```

## Usage

### Run the experiment

```bash
# Full run
uv run -m lost_in_the_middle.experiment

# Dry run — validate prompts & config without calling the API
uv run -m lost_in_the_middle.experiment --dry-run

# Print summary of existing results only
uv run -m lost_in_the_middle.experiment --summary-only
```

### Analyse results

```bash
# Print analysis tables & hypothesis evaluation
uv run -m lost_in_the_middle.analyze

# Also export a summary JSON
uv run -m lost_in_the_middle.analyze --export
```

## Configuration

All tunable parameters are set via environment variables (see `.env.example`):

| Variable             | Default | Description                        |
| -------------------- | ------- | ---------------------------------- |
| `OPENROUTER_API_KEY` | —       | Your OpenRouter API key (required) |
| `MODELS`             | 6 Qwen3 | Comma-separated model IDs         |
| `TEMPERATURE`        | `0`     | Sampling temperature               |
| `SEED`               | `42`    | Random seed                        |
| `TOP_P`              | `1`     | Nucleus sampling                   |
| `TOP_K`              | `0`     | Top-k sampling                     |
| `MAX_TOKENS`         | `200`   | Max response tokens                |
