"""
Results I/O
============
Reading and writing experiment results to/from CSV.
Supports resumption by tracking already-completed runs.
Thread-safe append for parallel execution.
"""

import csv
import threading

from .config import RESULTS_FILE, CSV_HEADERS

_write_lock = threading.Lock()


def load_existing_results() -> set[tuple[str, str, str]]:
    """Load already-completed (model, context_file, depth) tuples for resumption."""
    completed = set()
    if RESULTS_FILE.exists():
        with open(RESULTS_FILE, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                completed.add((row["model"], row["context_file"], row["depth"]))
    return completed


def append_result(row: dict) -> None:
    """Append a single result row to the CSV file (thread-safe)."""
    with _write_lock:
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
