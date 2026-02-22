"""
Results Analysis (CLI)
=======================
Reads output/results.csv and produces detailed analysis tables
and hypothesis evaluations. Exports to markdown and/or JSON.

Usage:
    uv run -m lost_in_the_middle.analyze
    uv run -m lost_in_the_middle.analyze --export   # Also export summary JSON + markdown
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .config import DEPTHS, OUTPUT_DIR
from .results_io import load_all_results

console = Console()

CATEGORIES = ["0 - 32k", "32k - 64k", "64k - 96k", "96k - 128k",
              "128k - 160k", "160k - 192k", "192k - 224k"]


def _mean(values: list[int | float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _fmt(values: list[int]) -> str:
    """Format accuracy as percentage with count."""
    if not values:
        return "—"
    return f"{_mean(values):.0%} ({sum(values)}/{len(values)})"


def _fmt_pct(values: list[int]) -> str:
    """Format as plain percentage."""
    if not values:
        return "—"
    return f"{_mean(values):.0%}"


def analyze(rows: list[dict]) -> dict:
    """Compute all analysis metrics."""
    acc = defaultdict(list)

    for r in rows:
        a = int(r["accuracy"])
        acc[("model_depth", r["model"], r["depth"])].append(a)
        acc[("model", r["model"])].append(a)
        acc[("size", r["model_size"])].append(a)
        acc[("type", r["model_type"])].append(a)
        acc[("depth", r["depth"])].append(a)
        acc[("category", r["category"])].append(a)
        acc[("size_depth", r["model_size"], r["depth"])].append(a)
        acc[("type_depth", r["model_type"], r["depth"])].append(a)
        acc[("category_depth", r["category"], r["depth"])].append(a)
        acc[("overall",)].append(a)

    return acc


def _build_markdown(acc: dict, rows: list[dict]) -> str:
    """Build the full analysis as a markdown string."""
    lines = []
    lines.append("# Lost in the Middle — Results Analysis\n")
    lines.append(f"**Total results:** {len(rows)} | "
                 f"**Models:** {len(set(r['model'] for r in rows))} | "
                 f"**Context files:** {len(set(r['context_file'] for r in rows))}\n")

    # ---- Table 1: Model × Depth ----
    lines.append("## 1. Accuracy by Model × Depth\n")
    header = "| Model | Size | Type | " + " | ".join(DEPTHS) + " | Overall |"
    sep = "|" + "|".join(["---"] * (4 + len(DEPTHS))) + "|"
    lines.append(header)
    lines.append(sep)

    models = sorted(set(r["model"] for r in rows))
    for model in models:
        size = rows[[r["model"] for r in rows].index(model)]["model_size"]
        mtype = rows[[r["model"] for r in rows].index(model)]["model_type"].capitalize()
        cells = [model, size, mtype]
        for d in DEPTHS:
            cells.append(_fmt(acc.get(("model_depth", model, d), [])))
        cells.append(_fmt_pct(acc.get(("model", model), [])))
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")

    # ---- Table 2: Size × Depth ----
    lines.append("## 2. Accuracy by Model Size × Depth\n")
    header = "| Size | " + " | ".join(DEPTHS) + " | Overall |"
    sep = "|" + "|".join(["---"] * (2 + len(DEPTHS))) + "|"
    lines.append(header)
    lines.append(sep)

    for size in ["8B", "30B", "235B"]:
        cells = [size]
        for d in DEPTHS:
            cells.append(_fmt(acc.get(("size_depth", size, d), [])))
        cells.append(_fmt_pct(acc.get(("size", size), [])))
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")

    # ---- Table 3: Type × Depth ----
    lines.append("## 3. Accuracy by Architecture × Depth\n")
    header = "| Architecture | " + " | ".join(DEPTHS) + " | Overall |"
    sep = "|" + "|".join(["---"] * (2 + len(DEPTHS))) + "|"
    lines.append(header)
    lines.append(sep)

    for t in ["instruct", "thinking"]:
        cells = [t.capitalize()]
        for d in DEPTHS:
            cells.append(_fmt(acc.get(("type_depth", t, d), [])))
        cells.append(_fmt_pct(acc.get(("type", t), [])))
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")

    # ---- Table 4: Category × Depth ----
    lines.append("## 4. Accuracy by Context Length Category × Depth\n")
    header = "| Category | " + " | ".join(DEPTHS) + " | Overall |"
    sep = "|" + "|".join(["---"] * (2 + len(DEPTHS))) + "|"
    lines.append(header)
    lines.append(sep)

    for cat in CATEGORIES:
        cells = [cat]
        for d in DEPTHS:
            cells.append(_fmt(acc.get(("category_depth", cat, d), [])))
        cells.append(_fmt_pct(acc.get(("category", cat), [])))
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")

    # ---- Hypothesis Verdicts ----
    lines.append("## Hypothesis Evaluation\n")

    depth_means = {d: _mean(acc.get(("depth", d), [])) for d in DEPTHS}
    worst_depth = min(depth_means, key=depth_means.get)
    h1 = worst_depth == "50%"
    lines.append(f"- {'✅' if h1 else '❌'} **H1** (50% depth = worst accuracy): "
                 f"{'Supported' if h1 else 'Not supported'}. "
                 + ", ".join(f"{d}={v:.0%}" for d, v in depth_means.items()))

    size_means = {s: _mean(acc.get(("size", s), [])) for s in ["8B", "30B", "235B"]}
    h2 = size_means.get("8B", 0) <= size_means.get("30B", 0) <= size_means.get("235B", 0)
    lines.append(f"- {'✅' if h2 else '❌'} **H2** (Larger = better): "
                 f"{'Supported' if h2 else 'Not supported'}. "
                 + ", ".join(f"{s}={v:.0%}" for s, v in size_means.items()))

    type_means = {t: _mean(acc.get(("type", t), [])) for t in ["instruct", "thinking"]}
    h3 = type_means.get("thinking", 0) > type_means.get("instruct", 0)
    lines.append(f"- {'✅' if h3 else '❌'} **H3** (Thinking > Instruct): "
                 f"{'Supported' if h3 else 'Not supported'}. "
                 f"Instruct={type_means.get('instruct', 0):.0%}, "
                 f"Thinking={type_means.get('thinking', 0):.0%}")

    cat_means = {c: _mean(acc.get(("category", c), [])) for c in CATEGORIES}
    cat_values = list(cat_means.values())
    h4 = all(cat_values[i] >= cat_values[i + 1] for i in range(len(cat_values) - 1))
    lines.append(f"- {'✅' if h4 else '❌'} **H4** (Longer context = lower accuracy): "
                 f"{'Supported' if h4 else 'Not supported'}. "
                 + ", ".join(f"{c}={v:.0%}" for c, v in cat_means.items()))
    lines.append("")

    # ---- Per-file failures ----
    failed_files = defaultdict(list)
    for r in rows:
        if int(r["accuracy"]) == 0:
            failed_files[r["context_file"]].append(f"{r['model']} ({r['depth']})")

    if failed_files:
        lines.append("## Failed Responses (Accuracy = 0)\n")
        lines.append("| Context File | Failed On |")
        lines.append("|---|---|")
        for fname, failures in sorted(failed_files.items()):
            lines.append(f"| {fname} | {', '.join(failures)} |")
    else:
        lines.append("✅ **All responses were accurate!**")
    lines.append("")

    return "\n".join(lines)


def print_analysis(acc: dict, rows: list[dict]) -> None:
    """Print all analysis tables and hypothesis evaluations to console."""
    console.print(
        Panel(
            f"[bold]Lost in the Middle — Results Analysis[/bold]\n"
            f"Total results: {len(rows)} | "
            f"Models: {len(set(r['model'] for r in rows))} | "
            f"Context files: {len(set(r['context_file'] for r in rows))}",
            style="blue",
        )
    )

    # ---- Table 1: Model × Depth ----
    table1 = Table(title="1. Accuracy by Model × Depth", show_lines=True)
    table1.add_column("Model", style="cyan", min_width=32)
    table1.add_column("Size", justify="center")
    table1.add_column("Type", justify="center")
    for d in DEPTHS:
        table1.add_column(d, justify="center")
    table1.add_column("Overall", justify="center", style="bold")

    models = sorted(set(r["model"] for r in rows))
    for model in models:
        size = rows[[r["model"] for r in rows].index(model)]["model_size"]
        mtype = rows[[r["model"] for r in rows].index(model)]["model_type"]
        row_vals = [model, size, mtype.capitalize()]
        for d in DEPTHS:
            vals = acc.get(("model_depth", model, d), [])
            row_vals.append(_fmt(vals))
        row_vals.append(_fmt_pct(acc.get(("model", model), [])))
        table1.add_row(*row_vals)
    console.print(table1)

    # ---- Table 2: Size × Depth ----
    table2 = Table(title="2. Accuracy by Model Size × Depth", show_lines=True)
    table2.add_column("Size", style="cyan")
    for d in DEPTHS:
        table2.add_column(d, justify="center")
    table2.add_column("Overall", justify="center", style="bold")

    for size in ["8B", "30B", "235B"]:
        row_vals = [size]
        for d in DEPTHS:
            row_vals.append(_fmt(acc.get(("size_depth", size, d), [])))
        row_vals.append(_fmt_pct(acc.get(("size", size), [])))
        table2.add_row(*row_vals)
    console.print(table2)

    # ---- Table 3: Type × Depth ----
    table3 = Table(title="3. Accuracy by Architecture × Depth", show_lines=True)
    table3.add_column("Architecture", style="cyan")
    for d in DEPTHS:
        table3.add_column(d, justify="center")
    table3.add_column("Overall", justify="center", style="bold")

    for t in ["instruct", "thinking"]:
        row_vals = [t.capitalize()]
        for d in DEPTHS:
            row_vals.append(_fmt(acc.get(("type_depth", t, d), [])))
        row_vals.append(_fmt_pct(acc.get(("type", t), [])))
        table3.add_row(*row_vals)
    console.print(table3)

    # ---- Table 4: Category × Depth ----
    table4 = Table(title="4. Accuracy by Context Length Category × Depth", show_lines=True)
    table4.add_column("Category", style="cyan")
    for d in DEPTHS:
        table4.add_column(d, justify="center")
    table4.add_column("Overall", justify="center", style="bold")

    for cat in CATEGORIES:
        row_vals = [cat]
        for d in DEPTHS:
            row_vals.append(_fmt(acc.get(("category_depth", cat, d), [])))
        row_vals.append(_fmt_pct(acc.get(("category", cat), [])))
        table4.add_row(*row_vals)
    console.print(table4)

    # ---- Hypothesis Verdicts ----
    console.print()
    console.print("[bold underline]Hypothesis Evaluation[/bold underline]\n")

    depth_means = {d: _mean(acc.get(("depth", d), [])) for d in DEPTHS}
    worst_depth = min(depth_means, key=depth_means.get)
    h1_support = worst_depth == "50%"
    h1_icon = "✅" if h1_support else "❌"
    console.print(
        f"  {h1_icon} [bold]H1[/bold] (50% depth = worst accuracy): "
        f"{'Supported' if h1_support else 'Not supported'}. "
        + ", ".join(f"{d}={v:.0%}" for d, v in depth_means.items())
    )

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

    type_means = {t: _mean(acc.get(("type", t), [])) for t in ["instruct", "thinking"]}
    h3_support = type_means.get("thinking", 0) > type_means.get("instruct", 0)
    h3_icon = "✅" if h3_support else "❌"
    console.print(
        f"  {h3_icon} [bold]H3[/bold] (Thinking > Instruct): "
        f"{'Supported' if h3_support else 'Not supported'}. "
        f"Instruct={type_means.get('instruct', 0):.0%}, "
        f"Thinking={type_means.get('thinking', 0):.0%}"
    )

    cat_means = {c: _mean(acc.get(("category", c), [])) for c in CATEGORIES}
    cat_values = list(cat_means.values())
    h4_support = all(cat_values[i] >= cat_values[i + 1] for i in range(len(cat_values) - 1))
    h4_icon = "✅" if h4_support else "❌"
    console.print(
        f"  {h4_icon} [bold]H4[/bold] (Longer context = lower accuracy): "
        f"{'Supported' if h4_support else 'Not supported'}. "
        + ", ".join(f"{c}={v:.0%}" for c, v in cat_means.items())
    )

    # ---- Per-file failures ----
    console.print()
    failed_files = defaultdict(list)
    for r in rows:
        if int(r["accuracy"]) == 0:
            failed_files[r["context_file"]].append(
                f"{r['model']} ({r['depth']})"
            )

    if failed_files:
        table_fail = Table(title="Failed Responses (Accuracy = 0)", show_lines=True)
        table_fail.add_column("Context File", style="red")
        table_fail.add_column("Failed On", style="dim")
        for fname, failures in sorted(failed_files.items()):
            table_fail.add_row(fname, ", ".join(failures))
        console.print(table_fail)
    else:
        console.print("[green]All responses were accurate![/green]")


def export_summary(acc: dict, rows: list[dict]) -> None:
    """Export summary statistics to JSON."""
    summary = {
        "total_results": len(rows),
        "models": sorted(set(r["model"] for r in rows)),
        "by_depth": {
            d: {
                "accuracy": _mean(acc.get(("depth", d), [])),
                "n": len(acc.get(("depth", d), [])),
            }
            for d in DEPTHS
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
        "by_category": {
            c: {
                "accuracy": _mean(acc.get(("category", c), [])),
                "n": len(acc.get(("category", c), [])),
            }
            for c in CATEGORIES
        },
    }

    json_path = OUTPUT_DIR / "results_summary.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    console.print(f"[green]JSON summary exported to {json_path}[/green]")


def export_markdown(acc: dict, rows: list[dict]) -> None:
    """Export all analysis tables as a markdown file."""
    md_path = OUTPUT_DIR / "results_analysis.md"
    md_content = _build_markdown(acc, rows)
    md_path.write_text(md_content)
    console.print(f"[green]Markdown analysis exported to {md_path}[/green]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze experiment results")
    parser.add_argument("--export", action="store_true", help="Export summary to JSON and markdown")
    args = parser.parse_args()

    rows = load_all_results()
    if not rows:
        console.print("[red]ERROR: No results found. Run the experiment first.[/red]")
        raise SystemExit(1)

    acc = analyze(rows)
    print_analysis(acc, rows)

    if args.export:
        export_summary(acc, rows)
        export_markdown(acc, rows)


if __name__ == "__main__":
    main()
