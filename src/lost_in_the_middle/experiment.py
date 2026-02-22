"""Main experiment: run prompts across models and context placements."""

import argparse

from lost_in_the_middle.prompts import load_prompts, load_story
from lost_in_the_middle.context_builder import insert_needle, build_prompt
from lost_in_the_middle.api_client import call_model
from lost_in_the_middle.evaluation import score_response
from lost_in_the_middle.config import MODELS
from lost_in_the_middle.results_io import save_results
from lost_in_the_middle.display import print_results


def _excerpt_around_needle(full_context: str, needle: str, chars: int = 200) -> str:
    """Return ~chars before and after where needle appears in full_context."""
    idx = full_context.find(needle)
    if idx < 0:
        return "(needle not found in context)"
    start = max(0, idx - chars)
    end = min(len(full_context), idx + len(needle) + chars)
    return full_context[start:end]


def run_experiment(dry_run: bool = False, repetitions: int = 1) -> list[dict]:
    """Run the Lost in the Middle experiment across all prompts, phases, and models."""
    prompts = load_prompts()
    results = []
    phases = ["context_start", "context_middle", "context_end"]

    for repetition in range(1, repetitions + 1):
        if repetitions > 1:
            print(f"\n--- Repetition {repetition}/{repetitions} ---")
        verbose_dry = dry_run and (repetition == 1 or repetitions == 1)

        for example in prompts:
            story = load_story(example["story_file"])
            for phase in phases:
                context, insert_idx, story_tokens = insert_needle(
                    story, example["needle"], phase
                )
                prompt_text = build_prompt(context, example["instruction"])

                if dry_run:
                    if verbose_dry:
                        print(
                            f"[DRY RUN] phase={phase} story_tokens={story_tokens} insert_token_index={insert_idx}"
                        )
                        if phase == "context_middle":
                            excerpt = _excerpt_around_needle(context, example["needle"])
                            print(f"  Excerpt around needle: ...{excerpt}...")
                    for model in MODELS:
                        results.append({
                            "repetition": repetition,
                            "phase": phase,
                            "model": model,
                            "expected_answer": example["expected_answer"],
                            "response": "[DRY-RUN]",
                            "is_correct": True,
                            "insertion_token_index": insert_idx,
                            "story_token_count": story_tokens,
                        })
                else:
                    for model in MODELS:
                        response = call_model(prompt_text, model=model)
                        is_correct = score_response(response, example["expected_answer"])
                        results.append({
                            "repetition": repetition,
                            "phase": phase,
                            "model": model,
                            "expected_answer": example["expected_answer"],
                            "response": response,
                            "is_correct": is_correct,
                            "insertion_token_index": insert_idx,
                            "story_token_count": story_tokens,
                        })

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Lost in the Middle experiment")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip API calls, use mock responses",
    )
    parser.add_argument(
        "--repetitions", "-n",
        type=int,
        default=1,
        help="Number of times to run the experiment (default: 1)",
    )
    args = parser.parse_args()

    results = run_experiment(dry_run=args.dry_run, repetitions=args.repetitions)
    print_results(results)
    path = save_results(results)
    print(f"\nResults saved to {path}")


if __name__ == "__main__":
    main()