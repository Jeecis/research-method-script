"""Display experiment results."""


def print_results(results: list[dict]) -> None:
    """Print results in a formatted table."""
    if not results:
        print("No results to display.")
        return
    print(f"{'Phase':<25} {'Model':<20} {'Expected':<20} {'Correct':<8}")
    print("-" * 75)
    for r in results:
        phase = r.get("phase", "")
        model = r.get("model", "")
        expected = r.get("expected_answer", "")[:18]
        correct = "Yes" if r.get("is_correct") else "No"
        print(f"{phase:<25} {model:<20} {expected:<20} {correct:<8}")
    print("-" * 75)
    correct_count = sum(1 for r in results if r.get("is_correct"))
    print(f"Total: {correct_count}/{len(results)} correct")
