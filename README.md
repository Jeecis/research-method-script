# Lost in the Middle — Semantic & Structured Retrieval Variant

This repository implements a modified experimental design that investigates the **Lost in the Middle** phenomenon (Liu et al., 2023) under resource constraints. Rather than replicating the original large-scale Gutenberg experiment, this branch explores whether retrieval degradation can be observed through *structured semantic competition* and *token-aware needle insertion* at moderate context lengths.

---

## 1. Research Motivation

The original **Lost in the Middle** paradigm (Liu et al., 2023) demonstrated that language models perform poorly when relevant information is placed in the middle of long contexts, producing a U-shaped accuracy curve: best at the start (primacy) and end (recency), worst in the middle. Large-scale experiments using Gutenberg-derived corpora and needle-in-haystack-style evaluations operate at **100k–192k word** context windows.

**Budget constraints** prevent replication at that scale. This branch therefore investigates whether the Lost-in-the-Middle effect can be observed using alternative mechanisms:

- **Structured semantic distractors** — competing facts embedded in coherent prose
- **Token-aware midpoint insertion** — precise needle placement relative to model tokenization
- **Multi-decoy competition** — multiple plausible answers to increase retrieval difficulty
- **Event-based retrieval** — factual questions over narrative rather than simple keyword retrieval

This branch tests whether structured semantic interference can serve as an alternative stressor to extreme context length in inducing retrieval degradation.

---

## 2. Key Design Differences From Original Experiment

| Aspect | Original Version | This Version |
|--------|------------------|--------------|
| Insertion unit | Word-level | Token-level |
| Needle type | Plain fact sentence | Semantically embedded needle |
| Competition | Single hidden fact | Multi-decoy structured competition |
| Evaluation | Keyword ("cyan") | Strict exact-match |
| Corpus | Large corpus sampling | Handcrafted long-form policy narrative |
| Depth positions | 0–100% in 10% increments | 3 primary phases (start/middle/end) |
| Context scale | 100k–192k words (~130k–250k tokens) | 6k–30k tokens (~4k–22k words) |

This variant should be interpreted as a methodological stress-test of retrieval under semantic competition rather than a direct replication of the large-scale Gutenberg-based paradigm. The goal is to probe retrieval dynamics under controlled structural manipulation, not to claim equivalence with 100k–192k word context experiments.

---

## 3. Experimental Variables

### Independent variables

- **Context length** — measured in tokens (via tiktoken)
- **Fact depth** — 0%, 50%, or 100% of token midpoint (via `context_start`, `context_middle`, `context_end`)

### Controlled variables

- **Model(s)** — `qwen/qwen3-vl-8b-instruct` and `qwen/qwen3-vl-8b-thinking`
- **Deterministic parameters** — `temperature=0`, `seed=42`, `top_p=1`, `top_k=0`
- **Fixed instruction** — same instruction text for all phases
- **Strict evaluation** — `STRICT_MATCH=1` (exact match only)

All primary experiments were conducted with deterministic decoding (temperature=0), meaning reported failures reflect retrieval errors rather than sampling variance.

### Dependent variable

- **Accuracy** — binary exact match (response equals expected answer)

---

## 4. Token-Aware Needle Insertion

Word-level insertion is imprecise because models operate on tokens rather than words. Token boundaries vary by encoding and model; a word index may not align with the actual attention span. This version uses **token midpoint insertion** for methodological precision.

### Implementation

- **Encoding:** `tiktoken` with `TOKENIZER_ENCODING=cl100k_base` (configurable via `.env`)
- **Logging:** Each result records `insertion_token_index` and `story_token_count` for reproducibility and debugging.

### Pseudocode

```python
def insert_needle(story: str, needle: str, phase: str) -> tuple[str, int, int]:
    tokens = enc.encode(story)
    N = len(tokens)

    if phase == "context_start":
        full_context = needle + "\n\n" + story
        insertion_token_index = 0
    elif phase == "context_middle":
        midpoint = N // 2
        left = enc.decode(tokens[:midpoint])
        right = enc.decode(tokens[midpoint:])
        full_context = left + "\n\n" + needle + "\n\n" + right
        insertion_token_index = midpoint
    elif phase == "context_end":
        full_context = story + "\n\n" + needle
        insertion_token_index = N

    return full_context, insertion_token_index, N
```

The instruction is fixed at the end of the prompt, after a `---` separator:

```
{context}

---

Instruction: {instruction}
```

---

## 5. Structured Decoy Design

The design evolved to increase retrieval competition without artificially signaling the correct answer:

| Phase | Design description |
|-------|---------------------|
| **Phase 1** | Simple "Final Update" marker — single authoritative update at end |
| **Phase 2** | Archived Log decoys — multiple dated entries with conflicting information |
| **Phase 3** | Semantic decoys embedded in prose — competing facts woven into narrative |
| **Phase 4** | Near-miss event decoys — e.g., March vs April hearing dates to test temporal discrimination |

**Goal:** Increase retrieval competition so that models must disambiguate among plausible alternatives without surface cues that favor the correct answer.

---

## 6. Long-Context Escalation

Context length was progressively increased to evaluate whether structured semantic competition could induce degradation without extreme scaling.

- **~6k tokens:** Perfect retrieval across all depth positions.
- **~30k tokens:** First observable retrieval failures under specific conditions (notably in start-position trials with high decoy density).
- **Classic U-shaped curve:** Not consistently observed at this scale.

These results suggest that, for 8B-class models, moderate context lengths (≤30k tokens) are generally insufficient to induce stable middle-position degradation, even under adversarial semantic competition. This is consistent with prior large-scale findings suggesting that degradation becomes more pronounced at substantially larger context windows.

---

## 7. Observations & Findings

Summarizing findings from runs to date:

- **Small models (e.g., 1.2B):** Show recency overwrite effects; earlier information can be overwritten by later context.
- **8B models:** Remain robust up to ~30k tokens; middle degradation is rare.
- **Start-position vulnerability:** Can occur due to decoy overwrite — the instruct model occasionally returned a competing decoy code when the needle was positioned at the start, suggesting interference from competing decoy content under long-context exposure.
- **Middle degradation:** Requires significantly larger context windows than tested here.

**Interpretation:** The results suggest that model capacity and effective attention span scaling play a dominant role at moderate context sizes. The classic U-shaped pattern appears most reliably under extreme context lengths.

### 7.1 Deterministic vs Probabilistic Effects

Because decoding was deterministic, observed errors reflect systematic retrieval degradation rather than sampling instability. Future extensions may explore temperature > 0 to measure probabilistic retrieval collapse under long-context competition.

---

## 8. Limitations

- **Budget constraints** limited testing above ~30k tokens.
- **Limited repetition** per depth (e.g., 3 runs per phase in recent experiments).
- **Single model family** — only Qwen 8B (instruct and thinking) tested.
- **Single handcrafted document** — `story1.txt` (Aurendale Water Allocation Crisis narrative) used in structured tests.

---

## 9. Future Work

- **Multi-story semantic corpus** — diverse narratives to reduce document-specific bias.
- **50k–100k token scaling** — test whether degradation emerges at moderate-high scale.
- **Multiple model families** — extend beyond Qwen family.
- **Probabilistic multi-run evaluation** — more repetitions and statistical reporting.
- **Attention weight analysis** — optional extension to inspect where models attend.

---

## 10. Repository Structure (Modified)

| Addition | Description |
|----------|-------------|
| `data/story1.txt` | Handcrafted long-form policy narrative (~30k tokens) |
| Structured semantic decoy injection | Design for multi-decoy competition (see Section 5) |
| Strict evaluation mode | `STRICT_MATCH=1` in `.env` for exact-match scoring |
| Token-aware insertion logging | `insertion_token_index` and `story_token_count` in results |

---

## 11. Conclusion

This branch demonstrates that:

1. **Moderate-length contexts (~30k tokens)** were insufficient to induce strong Lost-in-the-Middle effects in the tested 8B models under the current experimental conditions.
2. **Retrieval degradation** begins to appear under heavy distractor load and long context.
3. **Consistent U-shaped degradation patterns** likely require substantially larger context windows than those tested in this branch.

This branch explores **retrieval stress-testing via structured semantic competition** rather than pure length scaling.

---

## Installation & Usage

### Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - **Windows:** `venv\Scripts\activate`
   - **Unix/macOS:** `source venv/bin/activate`

3. Install the package in editable mode:
   ```bash
   pip install -e .
   ```

4. Copy the environment template and add your API key:
   - **Windows:** `copy .env.example .env`
   - **Unix/macOS:** `cp .env.example .env`

5. Edit `.env` and set your `OPENROUTER_API_KEY`. Configure `MODELS`, `STRICT_MATCH`, and `TOKENIZER_ENCODING` as needed.

### Run the experiment

```bash
python -m lost_in_the_middle.experiment
```

### Dry run (no API calls)

```bash
python -m lost_in_the_middle.experiment --dry-run
```

### Multiple repetitions

```bash
python -m lost_in_the_middle.experiment --repetitions 5
```

### Analyze results

```bash
python -m lost_in_the_middle.analyze
```

By default this loads from `output/results.json`. You can pass a custom path as an argument.

### Configuration

Key variables in `.env`:

- `MODELS` — Comma-separated list of model names (e.g., `qwen/qwen3-vl-8b-instruct,qwen/qwen3-vl-8b-thinking`)
- `TEMPERATURE` — Sampling temperature (0 for deterministic)
- `SEED` — Random seed for reproducibility
- `STRICT_MATCH` — 1 for exact match, 0 for contains match
- `TOKENIZER_ENCODING` — tiktoken encoding (default: `cl100k_base`)

---

## Reference

Liu, N. F., Lin, K., Hewitt, J., Paranjape, O., Bevilacqua, M., Petroni, F., & Liang, P. (2023). Lost in the Middle: How Language Models Use Long Contexts. *arXiv:2307.03172*.
