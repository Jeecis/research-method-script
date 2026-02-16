"""
Results Analysis (CLI)
=======================
Reads output/results.csv and produces detailed analysis tables
and hypothesis evaluations.

Usage:
    uv run -m lost_in_the_middle.analyze
    uv run -m lost_in_the_middle.analyze --export   # Also export summary JSON
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .config import PLACEMENTS, OUTPUT_DIR
from .results_io import load_all_results

console = Console()


def _mean(values: list[int | float]) -> float:
    return sum(values) / len(values) if values else 0.0


def analyze(rows: list[dict]) -> dict:
    """Compute all analysis metrics."""
    acc = defaultdict(list)

    for r in rows:
        a = int(r["accuracy"])
        acc[("model_placement", r["model"], r["placement"])].append(a)
        acc[("model", r["model"])].append(a)
        acc[("size", r["model_size"])].append(a)
        acc[("type", r["model_type"])].append(a)
        acc[("placement", r["placement"])].append(a)
        acc[("size_placement", r["model_size"], r["placement"])].append(a)
        acc[("type_placement", r["model_type"], r["placement"])].append(a)
        acc[("overall",)].append(a)

    return acc


def print_analysis(acc: dict, rows: list[dict]) -> None:
    """Print all analysis tables and hypothesis evaluations."""
    console.print(
        Panel(
            f"[bold]Lost in the Middle — Results Analysis[/bold]\n"
            f"Total results: {len(rows)} | "
            f"Models: {len(set(r['model'] for r in rows))} | "
            f"Prompts: {len(set(r['prompt_id'] for r in rows))}",
            style="blue",
        )
    )

    # ---- Table 1: Model × Placement ----
    table1 = Table(title="1. Accuracy by Model × Placement", show_lines=True)
    table1.add_column("Model", style="cyan", min_width=32)
    table1.add_column("Size", justify="center")
    table1.add_column("Type", justify="center")
    for p in PLACEMENTS:
        table1.add_column(p.capitalize(), justify="center")
    table1.add_column("Overall", justify="center", style="bold")

    models = sorted(set(r["model"] for r in rows))
    for model in models:
        size = rows[[r["model"] for r in rows].index(model)]["model_size"]
        mtype = rows[[r["model"] for r in rows].index(model)]["model_type"]
        row_vals = [model, size, mtype.capitalize()]
        for p in PLACEMENTS:
            vals = acc.get(("model_placement", model, p), [])
            row_vals.append(
                f"{_mean(vals):.0%} ({sum(vals)}/{len(vals)})" if vals else "—"
            )
        overall = acc.get(("model", model), [])
        row_vals.append(f"{_mean(overall):.0%}" if overall else "—")
        table1.add_row(*row_vals)

    console.print(table1)

    # ---- Table 2: Size × Placement ----
    table2 = Table(title="2. Accuracy by Model Size × Placement", show_lines=True)
    table2.add_column("Size", style="cyan")
    for p in PLACEMENTS:
        table2.add_column(p.capitalize(), justify="center")
    table2.add_column("Overall", justify="center", style="bold")

    for size in ["8B", "30B", "235B"]:
        row_vals = [size]
        for p in PLACEMENTS:
            vals = acc.get(("size_placement", size, p), [])
            row_vals.append(
                f"{_mean(vals):.0%} ({sum(vals)}/{len(vals)})" if vals else "—"
            )
        overall = acc.get(("size", size), [])
        row_vals.append(f"{_mean(overall):.0%}" if overall else "—")
        table2.add_row(*row_vals)
    console.print(table2)

    # ---- Table 3: Type × Placement ----
    table3 = Table(title="3. Accuracy by Architecture × Placement", show_lines=True)
    table3.add_column("Architecture", style="cyan")
    for p in PLACEMENTS:
        table3.add_column(p.capitalize(), justify="center")
    table3.add_column("Overall", justify="center", style="bold")

    for t in ["instruct", "thinking"]:
        row_vals = [t.capitalize()]
        for p in PLACEMENTS:
            vals = acc.get(("type_placement", t, p), [])
            row_vals.append(
                f"{_mean(vals):.0%} ({sum(vals)}/{len(vals)})" if vals else "—"
            )
        overall = acc.get(("type", t), [])
        row_vals.append(f"{_mean(overall):.0%}" if overall else "—")
        table3.add_row(*row_vals)
    console.print(table3)

    # ---- Hypothesis Verdicts ----
    console.print()
    console.print("[bold underline]Hypothesis Evaluation[/bold underline]\n")

    # H1: Middle placement = worst accuracy
    placement_means = {p: _mean(acc.get(("placement", p), [])) for p in PLACEMENTS}
    worst_placement = min(placement_means, key=placement_means.get)
    h1_support = worst_placement == "middle"
    h1_icon = "✅" if h1_support else "❌"
    console.print(
        f"  {h1_icon} [bold]H1[/bold] (Middle = worst accuracy): "
        f"{'Supported' if h1_support else 'Not supported'}. "
        f"Start={placement_means['start']:.0%}, "
        f"Middle={placement_means['middle']:.0%}, "
        f"End={placement_means['end']:.0%}"
    )

    # H2: Larger models = better accuracy
    size_means = {s: _mean(acc.get(("size", s), [])) for s in ["8B", "30B", "235B"]}
    h2_support = (
        size_means.get("8B", 0) <= size_means.get("30B", 0) <= size_means.get("235B", 0)
    )
    h2_icon = "✅" if h2_support else "❌"
    console.print(
        f"  {h2_icon} [bold]H2[/bold] (Larger = better): "
        f"{'Supported' if h2_support else 'Not supported'}. "
        + ", ".join(f"{s}={v:.0%}" for s, v in size_means.items())
    )

    # H3: Thinking > Instruct overall
    type_means = {t: _mean(acc.get(("type", t), [])) for t in ["instruct", "thinking"]}
    h3_support = type_means.get("thinking", 0) > type_means.get("instruct", 0)
    h3_icon = "✅" if h3_support else "❌"
    console.print(
        f"  {h3_icon} [bold]H3[/bold] (Thinking > Instruct): "
        f"{'Supported' if h3_support else 'Not supported'}. "
        f"Instruct={type_means.get('instruct', 0):.0%}, "
        f"Thinking={type_means.get('thinking', 0):.0%}"
    )

    # H4: Thinking models more consistent (lower variance across placements)
    def placement_variance(model_type: str) -> float:
        vals = [_mean(acc.get(("type_placement", model_type, p), [])) for p in PLACEMENTS]
        m = _mean(vals)
        return _mean([(v - m) ** 2 for v in vals])

    var_instruct = placement_variance("instruct")
    var_thinking = placement_variance("thinking")
    h4_support = var_thinking < var_instruct
    h4_icon = "✅" if h4_support else "❌"
    console.print(
        f"  {h4_icon} [bold]H4[/bold] (Thinking = more consistent): "
        f"{'Supported' if h4_support else 'Not supported'}. "
        f"Instruct variance={var_instruct:.4f}, "
        f"Thinking variance={var_thinking:.4f}"
    )

    # ---- Per-prompt failures ----
    console.print()
    failed_prompts = defaultdict(list)
    for r in rows:
        if int(r["accuracy"]) == 0:
            failed_prompts[r["prompt_title"]].append(
                f"{r['model']} ({r['placement']})"
            )

    if failed_prompts:
        table_fail = Table(title="Failed Responses (Accuracy = 0)", show_lines=True)
        table_fail.add_column("Prompt", style="red")
        table_fail.add_column("Failed On", style="dim")
        for title, failures in sorted(failed_prompts.items()):
            table_fail.add_row(title, ", ".join(failures))
        console.print(table_fail)
    else:
        console.print("[green]All responses were accurate![/green]")


def export_summary(acc: dict, rows: list[dict]) -> None:
    """Export summary statistics to JSON."""
    summary = {
        "total_results": len(rows),
        "models": sorted(set(r["model"] for r in rows)),
        "by_placement": {
            p: {
                "accuracy": _mean(acc.get(("placement", p), [])),
                "n": len(acc.get(("placement", p), [])),
            }
            for p in PLACEMENTS
        },
        "by_size": {
            s: {
                "accuracy": _mean(acc.get(("size", s), [])),
                "n": len(acc.get(("size", s), [])),
            }
            for s in ["8B", "30B", "235B"]
        },
        "by_type": {
            t: {
                "accuracy": _mean(acc.get(("type", t), [])),
                "n": len(acc.get(("type", t), [])),
            }
            for t in ["instruct", "thinking"]
        },
    }

    out_path = OUTPUT_DIR / "results_summary.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    console.print(f"\n[green]Summary exported to {out_path}[/green]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze experiment results")
    parser.add_argument("--export", action="store_true", help="Export summary to JSON")
    args = parser.parse_args()

    rows = load_all_results()
    if not rows:
        console.print("[red]ERROR: No results found. Run the experiment first.[/red]")
        raise SystemExit(1)

    acc = analyze(rows)
    print_analysis(acc, rows)

    if args.export:
        export_summary(acc, rows)


if __name__ == "__main__":
    main()
