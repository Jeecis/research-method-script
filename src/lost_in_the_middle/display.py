"""
Display
========
Quick summary table printed after an experiment run completes.
"""

from collections import defaultdict

from rich.console import Console
from rich.table import Table

from .config import DEPTHS
from .results_io import load_all_results

console = Console()

CATEGORIES = ["0 - 32k", "32k - 64k", "64k - 96k", "96k - 128k",
              "128k - 160k", "160k - 192k", "192k - 224k"]


def _mean(values: list[int | float]) -> float:
    return sum(values) / len(values) if values else 0.0


def print_summary() -> None:
    """Print a quick summary table of results."""
    rows = load_all_results()
    if not rows:
        console.print("[yellow]No results yet.[/yellow]")
        return

    console.print(f"\n[bold]Results Summary[/bold]  ({len(rows)} total)\n")

    # ---- Accuracy by Model × Depth ----
    acc = defaultdict(list)
    for r in rows:
        a = int(r["accuracy"])
        acc[("model_depth", r["model"], r["depth"])].append(a)
        acc[("model", r["model"])].append(a)
        acc[("depth", r["depth"])].append(a)
        acc[("category", r["category"])].append(a)
        acc[("category_depth", r["category"], r["depth"])].append(a)

    table = Table(title="Accuracy by Model × Depth", show_lines=True)
    table.add_column("Model", style="cyan", min_width=32)
    for d in DEPTHS:
        table.add_column(d, justify="center")
    table.add_column("Overall", justify="center", style="bold")

    models = sorted(set(r["model"] for r in rows))
    for model in models:
        row_vals = [model]
        for d in DEPTHS:
            vals = acc.get(("model_depth", model, d), [])
            row_vals.append(
                f"{_mean(vals):.0%} ({sum(vals)}/{len(vals)})" if vals else "—"
            )
        overall = acc.get(("model", model), [])
        row_vals.append(f"{_mean(overall):.0%}" if overall else "—")
        table.add_row(*row_vals)

    console.print(table)

    # ---- Accuracy by Category × Depth ----
    table2 = Table(title="Accuracy by Category × Depth", show_lines=True)
    table2.add_column("Category", style="cyan")
    for d in DEPTHS:
        table2.add_column(d, justify="center")
    table2.add_column("Overall", justify="center", style="bold")

    for cat in CATEGORIES:
        row_vals = [cat]
        for d in DEPTHS:
            vals = acc.get(("category_depth", cat, d), [])
            row_vals.append(
                f"{_mean(vals):.0%} ({sum(vals)}/{len(vals)})" if vals else "—"
            )
        overall = acc.get(("category", cat), [])
        row_vals.append(f"{_mean(overall):.0%}" if overall else "—")
        table2.add_row(*row_vals)

    console.print(table2)
