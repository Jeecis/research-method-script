"""
Experiment Runner (CLI)
========================
Runs the Lost in the Middle experiment across all configured models,
prompts, and placements.

Usage:
    uv run -m lost_in_the_middle.experiment              # Run full experiment
    uv run -m lost_in_the_middle.experiment --dry-run    # Validate without API calls
    uv run -m lost_in_the_middle.experiment --summary-only
"""

import argparse
import sys
import time

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn

from .config import OPENROUTER_API_KEY, MODELS, MODEL_PARAMS, PLACEMENTS
from .prompts import load_prompts, build_prompt
from .api_client import call_openrouter
from .evaluation import evaluate_accuracy, classify_model
from .results_io import load_existing_results, append_result
from .display import print_summary

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Lost in the Middle Experiment Runner",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration and prompt construction without making API calls",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only print the summary of existing results",
    )
    parser.add_argument(
        "--target-length",
        type=int,
        default=0,
        help="Target length in words for the context (paws via repetition)",
    )
    parser.add_argument(
        "--hide-label",
        action="store_true",
        help="Hide the [INSTRUCTION] label to make the task harder",
    )
    args = parser.parse_args()

    # ------------------------------------------------------------------
    # Summary-only mode
    # ------------------------------------------------------------------
    if args.summary_only:
        print_summary()
        return

    # ------------------------------------------------------------------
    # Validate API key
    # ------------------------------------------------------------------
    if not args.dry_run and (
        not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "sk-or-v1-your-key-here"
    ):
        console.print(
            "[red]ERROR: Please set OPENROUTER_API_KEY in your .env file.[/red]"
        )
        sys.exit(1)

    # ------------------------------------------------------------------
    # Load prompts
    # ------------------------------------------------------------------
    try:
        prompts = load_prompts()
    except FileNotFoundError as e:
        console.print(f"[red]ERROR: {e}[/red]")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Print experiment overview
    # ------------------------------------------------------------------
    console.print(f"\n[bold]Lost in the Middle Experiment[/bold]")
    console.print(f"  Models: {len(MODELS)}")
    console.print(f"  Prompts: {len(prompts)}")
    console.print(f"  Placements: {', '.join(PLACEMENTS)}")
    console.print(
        f"  Total API calls: {len(MODELS) * len(prompts) * len(PLACEMENTS)}"
    )
    console.print(f"  Parameters: {MODEL_PARAMS}")

    # ------------------------------------------------------------------
    # Prepare distractors
    # ------------------------------------------------------------------
    all_contexts = [p["context"] for p in prompts]

    # ------------------------------------------------------------------
    # Dry-run mode
    # ------------------------------------------------------------------
    if args.dry_run:
        console.print("\n[yellow]--- DRY RUN MODE ---[/yellow]\n")
        sample = prompts[0]
        # Use other contexts as distractors
        sample_distractors = [c for c in all_contexts if c != sample["context"]]
        
        for placement in PLACEMENTS:
            prompt_text = build_prompt(
                sample["context"],
                sample["instruction"],
                placement,
                target_length=args.target_length,
                hide_label=args.hide_label,
                distractors=sample_distractors,
            )
            console.print(f"[bold]Placement: {placement}[/bold]")
            console.print(f"  Prompt length: {len(prompt_text)} chars")
            console.print(f"  First 200 chars: {prompt_text[:200]}...")
            console.print(f"  Last 200 chars: ...{prompt_text[-200:]}")
            console.print()
        console.print("[green]Dry run complete. Configuration looks good![/green]")
        return

    # ------------------------------------------------------------------
    # Run experiment
    # ------------------------------------------------------------------
    completed = load_existing_results()
    if completed:
        console.print(
            f"\n  [yellow]Resuming: {len(completed)} results already recorded.[/yellow]"
        )

    total = len(MODELS) * len(prompts) * len(PLACEMENTS)
    skipped = 0

    with httpx.Client() as client:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Running experiment...", total=total)

            for model in MODELS:
                model_size, model_type = classify_model(model)

                for prompt_data in prompts:
                    prompt_id = prompt_data["id"]
                    title = prompt_data["title"]
                    context = prompt_data["context"]
                    instruction = prompt_data["instruction"]
                    expected = prompt_data["expected_answer"]
                    keywords = prompt_data["answer_keywords"]

                    for placement in PLACEMENTS:
                        # Skip if already done (resumption support)
                        if (model, prompt_id, placement) in completed:
                            skipped += 1
                            progress.advance(task)
                            continue

                        progress.update(
                            task,
                            description=(
                                f"[cyan]{model}[/cyan] | "
                                f"P{prompt_id} | "
                                f"{placement}"
                            ),
                        )

                        # Prepare distractors for this specific prompt
                        current_distractors = [c for c in all_contexts if c != context]

                        user_prompt = build_prompt(
                            context,
                            instruction,
                            placement,
                            target_length=args.target_length,
                            hide_label=args.hide_label,
                            distractors=current_distractors,
                        )
                        response_text = call_openrouter(
                            model, user_prompt, client, dry_run=args.dry_run
                        )
                        accuracy = evaluate_accuracy(response_text, keywords)

                        result = {
                            "model": model,
                            "model_size": model_size,
                            "model_type": model_type,
                            "prompt_id": prompt_id,
                            "prompt_title": title,
                            "placement": placement,
                            "response": response_text,
                            "expected_answer": expected,
                            "accuracy": accuracy,
                        }

                        append_result(result)
                        progress.advance(task)

                        # Small delay to avoid rate limiting
                        time.sleep(0.5)

    if skipped:
        console.print(f"\n[yellow]Skipped {skipped} already-completed calls.[/yellow]")

    console.print("\n[green]Experiment complete![/green]")
    console.print(f"Results saved to: output/results.csv\n")

    print_summary()


if __name__ == "__main__":
    main()
