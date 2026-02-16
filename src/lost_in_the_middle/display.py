"""
Display / Summary
==================
Rich-formatted summary tables for experiment results.
"""

from collections import defaultdict

from rich.console import Console
from rich.table import Table

from .config import PLACEMENTS
from .results_io import load_all_results

console = Console()


def _mean(values: list[int | float]) -> float:
    return sum(values) / len(values) if values else 0.0


def print_summary() -> None:
    """Print summary tables of results grouped by model × placement."""
    rows = load_all_results()

    if not rows:
        console.print("[red]No results to summarize.[/red]")
        return

    # Accumulate metrics
    acc_by_model_placement: dict[tuple, list] = defaultdict(list)
    acc_by_model: dict[str, list] = defaultdict(list)
    acc_by_size: dict[str, list] = defaultdict(list)
    acc_by_type: dict[str, list] = defaultdict(list)
    acc_by_placement: dict[str, list] = defaultdict(list)

    for r in rows:
        acc = int(r["accuracy"])
        acc_by_model_placement[(r["model"], r["placement"])].append(acc)
        acc_by_model[r["model"]].append(acc)
        acc_by_size[r["model_size"]].append(acc)
        acc_by_type[r["model_type"]].append(acc)
        acc_by_placement[r["placement"]].append(acc)

    # --- Table 1: Model × Placement ---
    table = Table(title="Accuracy by Model × Placement", show_lines=True)
    table.add_column("Model", style="cyan", min_width=30)
    for p in PLACEMENTS:
        table.add_column(p.capitalize(), justify="center", min_width=10)
    table.add_column("Overall", justify="center", style="bold", min_width=10)

    models_seen = sorted(set(r["model"] for r in rows))
    for model in models_seen:
        row_vals = [model]
        for p in PLACEMENTS:
            vals = acc_by_model_placement.get((model, p), [])
            if vals:
                m = _mean(vals)
                row_vals.append(f"{m:.1%} ({sum(vals)}/{len(vals)})")
            else:
                row_vals.append("—")
        overall = acc_by_model.get(model, [])
        row_vals.append(f"{_mean(overall):.1%}" if overall else "—")
        table.add_row(*row_vals)

    console.print()
    console.print(table)

    # --- Table 2: By Size ---
    table2 = Table(title="Accuracy by Model Size", show_lines=True)
    table2.add_column("Size", style="cyan")
    table2.add_column("Accuracy", justify="center")
    table2.add_column("N", justify="center")
    for size in ["8B", "30B", "235B"]:
        vals = acc_by_size.get(size, [])
        if vals:
            table2.add_row(size, f"{_mean(vals):.1%}", str(len(vals)))
    console.print(table2)

    # --- Table 3: By Type ---
    table3 = Table(title="Accuracy by Architecture", show_lines=True)
    table3.add_column("Type", style="cyan")
    table3.add_column("Accuracy", justify="center")
    table3.add_column("N", justify="center")
    for t in ["instruct", "thinking"]:
        vals = acc_by_type.get(t, [])
        if vals:
            table3.add_row(t.capitalize(), f"{_mean(vals):.1%}", str(len(vals)))
    console.print(table3)

    # --- Table 4: By Placement ---
    table4 = Table(title="Accuracy by Placement", show_lines=True)
    table4.add_column("Placement", style="cyan")
    table4.add_column("Accuracy", justify="center")
    table4.add_column("N", justify="center")
    for p in PLACEMENTS:
        vals = acc_by_placement.get(p, [])
        if vals:
            table4.add_row(p.capitalize(), f"{_mean(vals):.1%}", str(len(vals)))
    console.print(table4)
