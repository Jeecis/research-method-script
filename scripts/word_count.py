"""
Count words in every .txt file under a given directory, categorize by size,
and save results to JSON.

Usage:
    python scripts/word_count.py
    python scripts/word_count.py --dir /path/to/txt/files
"""

import json
import sys
from pathlib import Path

DEFAULT_DIR = Path(__file__).resolve().parents[1] / "large_data" / "archive" / "test" / "test"
OUTPUT_FILE = Path(__file__).resolve().parents[1] / "output" / "word_counts.json"

CATEGORIES = [
    ("0 - 32k",    0,      32_000),
    ("32k - 64k",  32_000, 64_000),
    ("64k - 96k",  64_000, 96_000),
    ("96k - 128k+", 96_000, float("inf")),
]


def categorize(word_count: int) -> str:
    for label, lo, hi in CATEGORIES:
        if lo <= word_count < hi:
            return label
    return CATEGORIES[-1][0]


def count_words(directory: Path) -> dict:
    counts = {}
    for txt_file in sorted(directory.glob("*.txt")):
        text = txt_file.read_text(encoding="utf-8", errors="replace")
        counts[txt_file.name] = len(text.split())
    return counts


def build_output(counts: dict) -> dict:
    categorized = {label: [] for label, _, _ in CATEGORIES}

    for filename, wc in counts.items():
        cat = categorize(wc)
        categorized[cat].append({"file": filename, "words": wc})

    # Sort each category by word count
    for cat in categorized:
        categorized[cat].sort(key=lambda x: x["words"])

    return {
        "total_files": len(counts),
        "categories": {
            cat: {"count": len(files), "files": files}
            for cat, files in categorized.items()
        },
    }


def main():
    target = Path(sys.argv[sys.argv.index("--dir") + 1]) if "--dir" in sys.argv else DEFAULT_DIR

    if not target.is_dir():
        print(f"Error: {target} is not a directory", file=sys.stderr)
        sys.exit(1)

    counts = count_words(target)
    output = build_output(counts)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(output, indent=2))
    print(f"Saved to {OUTPUT_FILE}")

    # Print summary
    for cat, data in output["categories"].items():
        print(f"  {cat}: {data['count']} files")


if __name__ == "__main__":
    main()
