# Lost in the Middle — Experiment

> Investigates how **context length** and **fact position (depth)** affect a language model's
> ability to retrieve a hidden fact embedded within large text documents.

## Research Summary

### Background

The "Lost in the Middle" phenomenon describes how large language models (LLMs) struggle to retrieve information placed in the middle of their context window, performing better when relevant information is near the beginning or end of the input. This experiment measures this effect systematically across varying context lengths and fact positions.

### Variables

| Variable | Type | Description |
|---|---|---|
| **Context length** | Independent | Word count of the surrounding text document, categorized into 6 groups: 0–32k, 32k–64k, 64k–96k, 96k–128k, 128k–160k, 160k–192k |
| **Fact depth** | Independent | Position (0%–100% in 10% increments) at which the hidden fact is inserted into the text, measured by word index |
| **Accuracy** | Dependent | Binary (0 or 1) — whether the model's response contains the correct answer keyword |
| **Model** | Controlled | Qwen 3 VL 8B Instruct (`qwen/qwen3-vl-8b-instruct`) via OpenRouter API |
| **Instruction** | Controlled | Fixed question: *"What kind of socks Jeffrey wore at his party?"* |
| **Hidden fact** | Controlled | Fixed sentence: *"Jefferey wore cyan colored socks with a yellow smiley face at his birthday party."* |
| **Generation parameters** | Controlled | temperature=0, seed=42, top_p=1, top_k=0, max_tokens=200 |

### Why These Categories?

Context length categories were chosen in **32k-word increments** to provide even coverage from short texts (~2.5k words) up to the model's practical context window limit (~192k words / ~262k tokens). Each category contains **5 text documents** selected from Project Gutenberg's public domain corpus, with word counts spread across the range to avoid clustering.

The 11 depth positions (0% to 100%) provide granular coverage of the entire text, going beyond the traditional start/middle/end trichotomy to reveal the precise shape of the retrieval accuracy curve.

### Procedure

1. **Data preparation**: 30 plain-text documents were selected from the Project Gutenberg test and train sets across 6 length categories (5 per category)
2. **Prompt construction**: For each document, the hidden fact sentence is inserted at a calculated word-level position corresponding to the target depth percentage (0%–100%). The fixed instruction is prepended to form the complete prompt
3. **API calls**: Each prompt is sent to the Qwen 3 VL 8B model via OpenRouter with deterministic generation parameters (temperature=0, seed=42). Requests run in parallel with 10 concurrent workers
4. **Evaluation**: The model's response is checked for the presence of the keyword "cyan". A match scores accuracy=1, a miss scores accuracy=0
5. **Total test cases**: 30 documents × 11 depths = **330 API calls**

### Findings

#### Overall accuracy: 91%

The model answered correctly in 301 out of 330 test cases.

#### H1: Middle positions have the lowest accuracy — ✅ Supported

Accuracy follows a clear U-shaped curve across depth positions:

| Depth | 0% | 10% | 20% | 30% | 40% | 50% | 60% | 70% | 80% | 90% | 100% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Accuracy** | 100% | 100% | 100% | 97% | 97% | **80%** | 83% | 83% | 87% | **80%** | 97% |

The model achieves perfect accuracy when the fact is at the very beginning (0%–20%) or very end (100%), but drops to 80% at the 50% and 90% positions. This confirms the Lost in the Middle effect — information placed near the center of the context is hardest for the model to retrieve.

#### H4: Longer context reduces accuracy — ✅ Supported

| Category | 0–32k | 32k–64k | 64k–96k | 96k–128k | 128k–160k | 160k–192k |
|---|---|---|---|---|---|---|
| **Accuracy** | 100% | 100% | 100% | 85% | 85% | 76% |

The model maintains perfect accuracy up to 96k words. Beyond that, performance degrades steadily — from 100% to 85% at 96k–160k, and down to 76% at 160k–192k. The degradation is most severe in the middle depth positions: at 160k–192k, 50%-depth accuracy drops to just **20%** (1/5).

#### Key Observations

- **Short contexts are trivial**: Documents under 96k words (~0–96k) showed 100% accuracy regardless of depth — the model handles these effortlessly
- **The breaking point begins at ~96k words**: This is where the first failures appear and the Lost in the Middle effect becomes observable
- **0% and 100% depth are resilient**: Even in the longest texts (160k–192k words), accuracy remains 100% when the fact is at the very start or very end
- **The middle-depth penalty worsens with length**: At 96k–128k, 50%-depth is 80%; at 160k–192k, it plummets to 20%

---

## Project Structure

```
├── data/
│   ├── prompts.json              # Experiment config (question, fact, context files)
│   ├── 0-32k_*.txt               # Context texts: 0-32k word category (5 files)
│   ├── 32k-64k_*.txt             # Context texts: 32k-64k word category (5 files)
│   ├── 64k-96k_*.txt             # Context texts: 64k-96k word category (5 files)
│   ├── 96k-128k_*.txt            # Context texts: 96k-128k word category (5 files)
│   ├── 128k-160k_*.txt           # Context texts: 128k-160k word category (5 files)
│   └── 160k-192k_*.txt           # Context texts: 160k-192k word category (5 files)
├── output/                       # (gitignored) experiment results
│   ├── results.csv
│   ├── results_analysis.md
│   └── results_summary.json
├── scripts/
│   ├── prepare_data.py           # Copy & rename texts from archive
│   └── train_word_count.py       # Word count scanner for train set
├── src/
│   └── lost_in_the_middle/       # Main Python package
│       ├── config.py             # All configuration & constants
│       ├── prompts.py            # Prompt loading & fact insertion
│       ├── api_client.py         # OpenRouter API client (async + sync)
│       ├── evaluation.py         # Accuracy scoring & model classification
│       ├── results_io.py         # CSV reading / writing / resumption
│       ├── display.py            # Rich summary tables
│       ├── experiment.py         # CLI — run the experiment
│       └── analyze.py            # CLI — analyse results & export markdown
├── .env.example                  # Template for environment variables
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
# Full run (parallel, 10 workers)
uv run -m lost_in_the_middle.experiment

# Custom concurrency
uv run -m lost_in_the_middle.experiment --workers 20

# Dry run — validate prompts & config without calling the API
uv run -m lost_in_the_middle.experiment --dry-run

# Print summary of existing results only
uv run -m lost_in_the_middle.experiment --summary-only
```

The experiment supports **automatic resumption** — if interrupted, re-running skips already-completed calls.

### Analyse results

```bash
# Print analysis tables & hypothesis evaluation
uv run -m lost_in_the_middle.analyze

# Also export summary JSON + markdown tables
uv run -m lost_in_the_middle.analyze --export
```

## Configuration

All tunable parameters are set via environment variables (see `.env.example`):

| Variable             | Default | Description                        |
| -------------------- | ------- | ---------------------------------- |
| `OPENROUTER_API_KEY` | —       | Your OpenRouter API key (required) |
| `MODELS`             | Qwen3 VL 8B | Comma-separated model IDs     |
| `TEMPERATURE`        | `0`     | Sampling temperature               |
| `SEED`               | `42`    | Random seed                        |
| `TOP_P`              | `1`     | Nucleus sampling                   |
| `TOP_K`              | `0`     | Top-k sampling                     |
| `MAX_TOKENS`         | `200`   | Max response tokens                |
