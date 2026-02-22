"""Analyze saved experiment results."""

import argparse
import pandas as pd

from lost_in_the_middle.results_io import load_results
from lost_in_the_middle.display import print_results


def analyze_results(results_path: str | None = None) -> None:
    """Load results, compute accuracy by phase and model, print summary."""
    results = load_results(results_path)
    if not results:
        print("No results to analyze.")
        return

    print("=== Full Results ===\n")
    print_results(results)

    df = pd.DataFrame(results)
    if "repetition" in df.columns:
        print("\n=== Accuracy by Repetition ===")
        rep_acc = df.groupby("repetition")["is_correct"].agg(["mean", "sum", "count"])
        rep_acc.columns = ["accuracy", "correct", "total"]
        rep_acc["accuracy"] = (rep_acc["accuracy"] * 100).round(1)
        print(rep_acc.to_string())

    print("\n=== Accuracy by Phase ===")
    phase_acc = df.groupby("phase")["is_correct"].agg(["mean", "sum", "count"])
    phase_acc.columns = ["accuracy", "correct", "total"]
    phase_acc["accuracy"] = (phase_acc["accuracy"] * 100).round(1)
    print(phase_acc.to_string())

    print("\n=== Accuracy by Model ===")
    model_acc = df.groupby("model")["is_correct"].agg(["mean", "sum", "count"])
    model_acc.columns = ["accuracy", "correct", "total"]
    model_acc["accuracy"] = (model_acc["accuracy"] * 100).round(1)
    print(model_acc.to_string())


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Lost in the Middle results")
    parser.add_argument(
        "results_path",
        nargs="?",
        default=None,
        help="Path to results JSON (default: output/results.json)",
    )
    args = parser.parse_args()
    analyze_results(args.results_path)


if __name__ == "__main__":
    main()
