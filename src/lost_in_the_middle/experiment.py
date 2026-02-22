"""
Experiment Runner (CLI)
========================
Runs the Lost in the Middle experiment across all configured models,
context files, and depth placements — with parallel API requests.

Usage:
    uv run -m lost_in_the_middle.experiment              # Run full experiment
    uv run -m lost_in_the_middle.experiment --dry-run    # Validate without API calls
    uv run -m lost_in_the_middle.experiment --summary-only
    uv run -m lost_in_the_middle.experiment --workers 20  # Set concurrency
"""

import argparse
import asyncio
import sys

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn

from .config import OPENROUTER_API_KEY, MODELS, MODEL_PARAMS, DEPTHS
from .prompts import load_prompt_config, load_context, build_prompt
from .api_client import call_openrouter_async
from .evaluation import evaluate_accuracy, classify_model
from .results_io import load_existing_results, append_result
from .display import print_summary

console = Console()

DEFAULT_WORKERS = 10


async def run_experiment(args, config: dict) -> None:
    """Run the full experiment with parallel API calls."""
    instruction = config["instruction"]
    fact = config["fact"]
    expected = config["expected_answer"]
    keywords = config["answer_keywords"]
    context_files = config["context_files"]

    completed = load_existing_results()
    if completed:
        console.print(
            f"\n  [yellow]Resuming: {len(completed)} results already recorded.[/yellow]"
        )

    # Pre-load all context texts
    contexts = {}
    for ctx_entry in context_files:
        contexts[ctx_entry["file"]] = load_context(ctx_entry["file"])

    # Build list of jobs to run
    jobs = []
    for model in MODELS:
        model_size, model_type = classify_model(model)
        for ctx_entry in context_files:
            ctx_file = ctx_entry["file"]
            category = ctx_entry["category"]
            for depth in DEPTHS:
                if (model, ctx_file, depth) in completed:
                    continue
                jobs.append({
                    "model": model,
                    "model_size": model_size,
                    "model_type": model_type,
                    "ctx_file": ctx_file,
                    "category": category,
                    "depth": depth,
                })

    total = len(MODELS) * len(context_files) * len(DEPTHS)
    skipped = total - len(jobs)

    if skipped:
        console.print(f"  [yellow]Skipping {skipped} already-completed calls.[/yellow]")

    if not jobs:
        console.print("[green]All calls already completed![/green]")
        print_summary()
        return

    console.print(f"  [bold]Running {len(jobs)} remaining API calls with {args.workers} workers...[/bold]\n")

    semaphore = asyncio.Semaphore(args.workers)

    async with httpx.AsyncClient() as client:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Running experiment...", total=len(jobs))

            async def process_job(job: dict) -> None:
                async with semaphore:
                    model = job["model"]
                    ctx_file = job["ctx_file"]
                    depth = job["depth"]

                    progress.update(
                        task,
                        description=(
                            f"[cyan]{model}[/cyan] | "
                            f"{ctx_file} | {depth}"
                        ),
                    )

                    text = contexts[ctx_file]
                    user_prompt = build_prompt(text, fact, instruction, depth)
                    response_text = await call_openrouter_async(
                        model, user_prompt, client, dry_run=args.dry_run
                    )
                    accuracy = evaluate_accuracy(response_text, keywords)

                    result = {
                        "model": model,
                        "model_size": job["model_size"],
                        "model_type": job["model_type"],
                        "context_file": ctx_file,
                        "category": job["category"],
                        "depth": depth,
                        "response": response_text,
                        "expected_answer": expected,
                        "accuracy": accuracy,
                    }

                    append_result(result)
                    progress.advance(task)

            await asyncio.gather(*[process_job(job) for job in jobs])

    console.print("\n[green]Experiment complete![/green]")
    console.print(f"Results saved to: output/results.csv\n")
    print_summary()


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
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Number of parallel API requests (default: {DEFAULT_WORKERS})",
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
    # Load prompt config
    # ------------------------------------------------------------------
    try:
        config = load_prompt_config()
    except FileNotFoundError as e:
        console.print(f"[red]ERROR: {e}[/red]")
        sys.exit(1)

    context_files = config["context_files"]

    # ------------------------------------------------------------------
    # Print experiment overview
    # ------------------------------------------------------------------
    console.print(f"\n[bold]Lost in the Middle Experiment[/bold]")
    console.print(f"  Models: {len(MODELS)}")
    console.print(f"  Context files: {len(context_files)}")
    console.print(f"  Depths: {', '.join(DEPTHS)}")
    console.print(
        f"  Total API calls: {len(MODELS) * len(context_files) * len(DEPTHS)}"
    )
    console.print(f"  Workers: {args.workers}")
    console.print(f"  Parameters: {MODEL_PARAMS}")
    console.print(f"  Question: {config['instruction']}")
    console.print(f"  Hidden fact: {config['fact']}")

    # ------------------------------------------------------------------
    # Dry-run mode
    # ------------------------------------------------------------------
    if args.dry_run:
        console.print("\n[yellow]--- DRY RUN MODE ---[/yellow]\n")
        sample = context_files[0]
        text = load_context(sample["file"])
        word_count = len(text.split())

        for depth in DEPTHS:
            prompt_text = build_prompt(text, config["fact"], config["instruction"], depth)
            pct = int(depth.replace("%", ""))
            fact_pos = int(word_count * pct / 100)

            console.print(f"[bold]File: {sample['file']} | Depth: {depth}[/bold]")
            console.print(f"  Text words: {word_count}")
            console.print(f"  Fact inserted at word ~{fact_pos}")
            console.print(f"  Prompt length: {len(prompt_text)} chars")
            console.print(f"  First 200 chars: {prompt_text[:200]}...")
            console.print(f"  Last 200 chars: ...{prompt_text[-200:]}")
            console.print()
        console.print("[green]Dry run complete. Configuration looks good![/green]")
        return

    # ------------------------------------------------------------------
    # Run experiment (async)
    # ------------------------------------------------------------------
    asyncio.run(run_experiment(args, config))


if __name__ == "__main__":
    main()
