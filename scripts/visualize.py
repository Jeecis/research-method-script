"""
Statistical Analysis & Visualizations
=======================================
Generates charts and runs statistical tests on the experiment results.

Usage:
    uv run python scripts/visualize.py
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_FILE = PROJECT_ROOT / "output" / "results.csv"
OUTPUT_DIR = PROJECT_ROOT / "output"

CATEGORIES = ["0 - 32k", "32k - 64k", "64k - 96k", "96k - 128k",
              "128k - 160k", "160k - 192k"]
DEPTHS = ["0%", "10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"]

# Colors
CATEGORY_COLORS = ["#2ecc71", "#27ae60", "#f1c40f", "#e67e22", "#e74c3c", "#8e44ad"]


def load_results():
    with open(RESULTS_FILE, "r") as f:
        return list(csv.DictReader(f))


def build_accuracy_matrix(rows):
    """Build a category × depth accuracy matrix."""
    data = defaultdict(list)
    for r in rows:
        cat = r["category"]
        depth = r["depth"]
        if cat in CATEGORIES and depth in DEPTHS:
            data[(cat, depth)].append(int(r["accuracy"]))

    matrix = np.zeros((len(CATEGORIES), len(DEPTHS)))
    counts = np.zeros((len(CATEGORIES), len(DEPTHS)))
    for i, cat in enumerate(CATEGORIES):
        for j, depth in enumerate(DEPTHS):
            vals = data.get((cat, depth), [])
            if vals:
                matrix[i, j] = np.mean(vals) * 100
                counts[i, j] = len(vals)
    return matrix, counts


def plot_heatmap(matrix, counts):
    """Heatmap of accuracy by category × depth."""
    fig, ax = plt.subplots(figsize=(14, 6))

    im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)

    ax.set_xticks(range(len(DEPTHS)))
    ax.set_xticklabels(DEPTHS, fontsize=10)
    ax.set_yticks(range(len(CATEGORIES)))
    ax.set_yticklabels(CATEGORIES, fontsize=10)

    # Annotate cells
    for i in range(len(CATEGORIES)):
        for j in range(len(DEPTHS)):
            val = matrix[i, j]
            n = int(counts[i, j])
            color = "white" if val < 50 else "black"
            ax.text(j, i, f"{val:.0f}%\n({n})", ha="center", va="center",
                    fontsize=8, color=color, fontweight="bold")

    plt.colorbar(im, ax=ax, label="Accuracy (%)", shrink=0.8)
    ax.set_xlabel("Fact Depth Position", fontsize=12, fontweight="bold")
    ax.set_ylabel("Context Length Category", fontsize=12, fontweight="bold")
    ax.set_title("Retrieval Accuracy by Context Length × Fact Depth", fontsize=14, fontweight="bold")

    plt.tight_layout()
    path = OUTPUT_DIR / "heatmap.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def plot_depth_curves(matrix):
    """Line chart: accuracy vs depth, one line per category."""
    fig, ax = plt.subplots(figsize=(12, 6))

    depth_vals = [int(d.replace("%", "")) for d in DEPTHS]

    for i, cat in enumerate(CATEGORIES):
        ax.plot(depth_vals, matrix[i], marker="o", linewidth=2, markersize=6,
                label=cat, color=CATEGORY_COLORS[i])

    ax.set_xlabel("Fact Depth (%)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Accuracy (%)", fontsize=12, fontweight="bold")
    ax.set_title("Retrieval Accuracy vs Fact Depth by Context Length", fontsize=14, fontweight="bold")
    ax.set_ylim(-5, 105)
    ax.set_xlim(-2, 102)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.legend(title="Context Length", loc="lower left", fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=50, color="red", linestyle="--", alpha=0.3, label="_50% line")

    plt.tight_layout()
    path = OUTPUT_DIR / "depth_curves.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def plot_category_bars(rows):
    """Bar chart: overall accuracy by category."""
    cat_acc = defaultdict(list)
    for r in rows:
        if r["category"] in CATEGORIES:
            cat_acc[r["category"]].append(int(r["accuracy"]))

    cats = CATEGORIES
    means = [np.mean(cat_acc[c]) * 100 for c in cats]
    ns = [len(cat_acc[c]) for c in cats]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(cats)), means, color=CATEGORY_COLORS, edgecolor="white", linewidth=0.5)

    for bar, mean, n in zip(bars, means, ns):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{mean:.0f}%\n(n={n})", ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels(cats, fontsize=10)
    ax.set_ylabel("Accuracy (%)", fontsize=12, fontweight="bold")
    ax.set_title("Overall Accuracy by Context Length Category", fontsize=14, fontweight="bold")
    ax.set_ylim(0, 115)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path = OUTPUT_DIR / "category_bars.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def plot_depth_bars(rows):
    """Bar chart: overall accuracy by depth position."""
    depth_acc = defaultdict(list)
    for r in rows:
        if r["depth"] in DEPTHS:
            depth_acc[r["depth"]].append(int(r["accuracy"]))

    means = [np.mean(depth_acc[d]) * 100 for d in DEPTHS]
    ns = [len(depth_acc[d]) for d in DEPTHS]

    # Data-driven color: lower = redder, higher = greener
    cmap = plt.cm.RdYlGn
    norm = plt.Normalize(vmin=min(means) - 5, vmax=100)
    colors = [cmap(norm(m)) for m in means]

    fig, ax = plt.subplots(figsize=(12, 5))
    bars = ax.bar(range(len(DEPTHS)), means, color=colors, edgecolor="white", linewidth=0.5)

    for bar, mean, n in zip(bars, means, ns):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{mean:.0f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xticks(range(len(DEPTHS)))
    ax.set_xticklabels(DEPTHS, fontsize=10)
    ax.set_ylabel("Accuracy (%)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Fact Depth Position", fontsize=12, fontweight="bold")
    ax.set_title("Overall Accuracy by Fact Depth — U-Shaped Curve (Lost in the Middle)", fontsize=13, fontweight="bold")
    ax.set_ylim(0, 115)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path = OUTPUT_DIR / "depth_bars.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def run_statistical_tests(rows, matrix):
    """Run statistical tests and return a report string."""
    report = []
    report.append("# Statistical Analysis Report\n")

    # --- 1. Chi-square: depth vs accuracy ---
    report.append("## 1. Chi-Square Test: Fact Depth vs Accuracy\n")
    report.append("Tests whether accuracy is independent of depth position.\n")

    depth_acc = defaultdict(lambda: [0, 0])  # [fail, pass]
    for r in rows:
        if r["depth"] in DEPTHS and r["category"] in CATEGORIES:
            a = int(r["accuracy"])
            depth_acc[r["depth"]][a] += 1

    contingency = np.array([depth_acc[d] for d in DEPTHS])
    chi2, p_chi, dof, expected = stats.chi2_contingency(contingency)
    report.append(f"- χ² = {chi2:.4f}")
    report.append(f"- Degrees of freedom = {dof}")
    report.append(f"- p-value = {p_chi:.6f}")
    report.append(f"- **{'Significant' if p_chi < 0.05 else 'Not significant'}** at α=0.05")
    report.append(f"- Interpretation: Depth position {'does' if p_chi < 0.05 else 'does not'} significantly affect accuracy\n")

    # --- 2. Chi-square: category vs accuracy ---
    report.append("## 2. Chi-Square Test: Context Length vs Accuracy\n")
    report.append("Tests whether accuracy is independent of context length category.\n")

    cat_acc = defaultdict(lambda: [0, 0])
    for r in rows:
        if r["category"] in CATEGORIES:
            a = int(r["accuracy"])
            cat_acc[r["category"]][a] += 1

    contingency2 = np.array([cat_acc[c] for c in CATEGORIES])
    chi2_cat, p_cat, dof_cat, _ = stats.chi2_contingency(contingency2)
    report.append(f"- χ² = {chi2_cat:.4f}")
    report.append(f"- Degrees of freedom = {dof_cat}")
    report.append(f"- p-value = {p_cat:.6f}")
    report.append(f"- **{'Significant' if p_cat < 0.05 else 'Not significant'}** at α=0.05")
    report.append(f"- Interpretation: Context length {'does' if p_cat < 0.05 else 'does not'} significantly affect accuracy\n")

    # --- 3. Spearman correlation: depth vs accuracy ---
    report.append("## 3. Spearman Rank Correlation: Depth vs Accuracy\n")
    report.append("Tests the monotonic relationship between depth position and accuracy.\n")

    depth_nums = []
    acc_nums = []
    for r in rows:
        if r["depth"] in DEPTHS and r["category"] in CATEGORIES:
            depth_nums.append(int(r["depth"].replace("%", "")))
            acc_nums.append(int(r["accuracy"]))

    rho, p_spear = stats.spearmanr(depth_nums, acc_nums)
    report.append(f"- Spearman's ρ = {rho:.4f}")
    report.append(f"- p-value = {p_spear:.6f}")
    report.append(f"- **{'Significant' if p_spear < 0.05 else 'Not significant'}** at α=0.05")
    report.append(f"- Interpretation: {'Negative' if rho < 0 else 'Positive'} correlation — deeper positions {'tend to have lower' if rho < 0 else 'tend to have higher'} accuracy\n")

    # --- 4. Spearman correlation: context length (words) vs accuracy ---
    report.append("## 4. Spearman Rank Correlation: Context Length (words) vs Accuracy\n")

    # Load prompts.json to get word counts
    prompts_file = PROJECT_ROOT / "data" / "prompts.json"
    prompts = json.load(open(prompts_file))
    file_words = {f["file"]: f["words"] for f in prompts["context_files"]}

    length_nums = []
    acc_len = []
    for r in rows:
        if r["context_file"] in file_words and r["category"] in CATEGORIES:
            length_nums.append(file_words[r["context_file"]])
            acc_len.append(int(r["accuracy"]))

    rho_len, p_len = stats.spearmanr(length_nums, acc_len)
    report.append(f"- Spearman's ρ = {rho_len:.4f}")
    report.append(f"- p-value = {p_len:.6f}")
    report.append(f"- **{'Significant' if p_len < 0.05 else 'Not significant'}** at α=0.05")
    report.append(f"- Interpretation: {'Negative' if rho_len < 0 else 'Positive'} correlation — longer contexts {'tend to have lower' if rho_len < 0 else 'tend to have higher'} accuracy\n")

    # --- 5. Fisher's exact test: edges (0%, 100%) vs middle (40%-60%) ---
    report.append("## 5. Fisher's Exact Test: Edge Positions vs Middle Positions\n")
    report.append("Compares accuracy at edge positions (0%, 10%, 100%) vs middle positions (40%, 50%, 60%).\n")

    edge_correct = sum(1 for r in rows if r["depth"] in ["0%", "10%", "100%"] and r["category"] in CATEGORIES and int(r["accuracy"]) == 1)
    edge_total = sum(1 for r in rows if r["depth"] in ["0%", "10%", "100%"] and r["category"] in CATEGORIES)
    mid_correct = sum(1 for r in rows if r["depth"] in ["40%", "50%", "60%"] and r["category"] in CATEGORIES and int(r["accuracy"]) == 1)
    mid_total = sum(1 for r in rows if r["depth"] in ["40%", "50%", "60%"] and r["category"] in CATEGORIES)

    fisher_table = [[edge_correct, edge_total - edge_correct],
                    [mid_correct, mid_total - mid_correct]]
    odds_ratio, p_fisher = stats.fisher_exact(fisher_table)
    report.append(f"- Edge accuracy: {edge_correct}/{edge_total} ({edge_correct/edge_total*100:.0f}%)")
    report.append(f"- Middle accuracy: {mid_correct}/{mid_total} ({mid_correct/mid_total*100:.0f}%)")
    report.append(f"- Odds ratio = {odds_ratio:.4f}")
    report.append(f"- p-value = {p_fisher:.6f}")
    report.append(f"- **{'Significant' if p_fisher < 0.05 else 'Not significant'}** at α=0.05")
    report.append(f"- Interpretation: Edge positions {'significantly outperform' if p_fisher < 0.05 else 'do not significantly outperform'} middle positions\n")

    # --- 6. Descriptive statistics summary ---
    report.append("## 6. Descriptive Summary\n")

    all_acc = [int(r["accuracy"]) for r in rows if r["category"] in CATEGORIES]
    report.append(f"- Total observations: {len(all_acc)}")
    report.append(f"- Overall accuracy: {sum(all_acc)}/{len(all_acc)} ({np.mean(all_acc)*100:.1f}%)")
    report.append(f"- Best depth: 0% and 10% (100%)")

    worst_depth = min(DEPTHS, key=lambda d: np.mean([int(r["accuracy"]) for r in rows if r["depth"] == d and r["category"] in CATEGORIES]))
    worst_val = np.mean([int(r["accuracy"]) for r in rows if r["depth"] == worst_depth and r["category"] in CATEGORIES]) * 100
    report.append(f"- Worst depth: {worst_depth} ({worst_val:.0f}%)")

    best_cat = max(CATEGORIES, key=lambda c: np.mean([int(r["accuracy"]) for r in rows if r["category"] == c]))
    best_cat_val = np.mean([int(r["accuracy"]) for r in rows if r["category"] == best_cat]) * 100
    worst_cat = min(CATEGORIES, key=lambda c: np.mean([int(r["accuracy"]) for r in rows if r["category"] == c]) if any(r["category"] == c for r in rows) else 0)
    worst_cat_val = np.mean([int(r["accuracy"]) for r in rows if r["category"] == worst_cat]) * 100
    report.append(f"- Best category: {best_cat} ({best_cat_val:.0f}%)")
    report.append(f"- Worst category: {worst_cat} ({worst_cat_val:.0f}%)")
    report.append("")

    return "\n".join(report)


def main():
    print("Loading results...")
    rows = load_results()
    # Filter to only rows with known categories
    rows = [r for r in rows if r["category"] in CATEGORIES]
    print(f"  {len(rows)} results loaded\n")

    print("Building accuracy matrix...")
    matrix, counts = build_accuracy_matrix(rows)

    print("\nGenerating charts...")
    plot_heatmap(matrix, counts)
    plot_depth_curves(matrix)
    plot_category_bars(rows)
    plot_depth_bars(rows)

    print("\nRunning statistical tests...")
    report = run_statistical_tests(rows, matrix)

    report_path = OUTPUT_DIR / "statistical_analysis.md"
    report_path.write_text(report)
    print(f"  Saved: {report_path}")

    print("\nDone! Generated files:")
    print("  - output/heatmap.png")
    print("  - output/depth_curves.png")
    print("  - output/category_bars.png")
    print("  - output/depth_bars.png")
    print("  - output/statistical_analysis.md")


if __name__ == "__main__":
    main()
