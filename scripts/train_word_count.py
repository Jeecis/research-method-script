"""
Find train files in the 128k-160k and 160k-192k word ranges.
Uses file size to pre-filter, only counts words on likely candidates.

Usage:
    python scripts/train_word_count.py
"""

import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAIN_DIR = PROJECT_ROOT / "large_data" / "archive" / "train" / "train"
OUTPUT_FILE = PROJECT_ROOT / "output" / "train_word_counts.json"

# Only the 2 categories we need
CATEGORIES = [
    ("128k - 160k", 128_000, 160_000),
    ("160k - 192k", 160_000, 192_000),
]

# File size filter: ~5-6 bytes/word, so 128k-192k words ≈ 600KB-1.2MB
MIN_BYTES = 600_000
MAX_BYTES = 1_300_000


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    results = {label: [] for label, _, _ in CATEGORIES}

    # Pre-filter by file size
    candidates = [
        f for f in sorted(TRAIN_DIR.glob("*.txt"))
        if MIN_BYTES <= f.stat().st_size <= MAX_BYTES
    ]
    print(f"Pre-filtered to {len(candidates)} candidates (by file size {MIN_BYTES//1000}KB-{MAX_BYTES//1000}KB)")

    for i, fpath in enumerate(candidates, 1):
        wc = int(subprocess.run(
            ["wc", "-w", str(fpath)], capture_output=True, text=True
        ).stdout.split()[0])

        for label, lo, hi in CATEGORIES:
            if lo <= wc < hi:
                results[label].append({"file": fpath.name, "words": wc})
                print(f"  [{i}/{len(candidates)}] {fpath.name:15s} {wc:>8,}  [{label}]")
                break
        else:
            print(f"  [{i}/{len(candidates)}] {fpath.name:15s} {wc:>8,}  (outside range)")

        # Save every 10 files
        if i % 10 == 0 or i == len(candidates):
            for cat in results:
                results[cat].sort(key=lambda x: x["words"])
            OUTPUT_FILE.write_text(json.dumps(
                {cat: {"count": len(files), "files": files} for cat, files in results.items()},
                indent=2
            ))

    print(f"\nDone. Saved to {OUTPUT_FILE}")
    for label, _, _ in CATEGORIES:
        print(f"  {label}: {len(results[label])} files")


if __name__ == "__main__":
    main()
