"""
Results I/O
============
Reading and writing experiment results to/from CSV.
Supports resumption by tracking already-completed runs.
"""

import csv

from .config import RESULTS_FILE, CSV_HEADERS


def load_existing_results() -> set[tuple[str, int, str]]:
    """Load already-completed (model, prompt_id, placement) tuples for resumption."""
    completed = set()
    if RESULTS_FILE.exists():
        with open(RESULTS_FILE, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                completed.add((row["model"], int(row["prompt_id"]), row["placement"]))
    return completed


def append_result(row: dict) -> None:
    """Append a single result row to the CSV file."""
    file_exists = RESULTS_FILE.exists()
    with open(RESULTS_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def load_all_results() -> list[dict]:
    """Load all results from the CSV file."""
    if not RESULTS_FILE.exists():
        return []

    with open(RESULTS_FILE, "r", newline="") as f:
        return list(csv.DictReader(f))
