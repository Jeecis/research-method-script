"""
Prepare data: copy selected text files into the data/ folder
with category-prefixed names.

Usage:
    python scripts/prepare_data.py
"""

import json
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "large_data" / "archive" / "test" / "test"
DATA_DIR = PROJECT_ROOT / "data"
SELECTED = PROJECT_ROOT / "output" / "selected_files.json"


def main():
    with open(SELECTED) as f:
        files = json.load(f)

    for entry in files:
        category_prefix = entry["category"].replace(" ", "").replace("-", "-")
        new_name = f"{category_prefix}_{entry['file']}"
        src = SOURCE_DIR / entry["file"]
        dst = DATA_DIR / new_name

        if not src.exists():
            print(f"WARNING: {src} not found, skipping")
            continue

        shutil.copy2(src, dst)
        print(f"  {entry['file']} -> {new_name}  ({entry['words']} words)")

    print(f"\nDone. {len(files)} files copied to {DATA_DIR}")


if __name__ == "__main__":
    main()
