"""
Accuracy Evaluation
====================
Binary accuracy scoring and model classification utilities.
"""


def evaluate_accuracy(response: str, answer_keywords: list[str]) -> int:
    """
    Binary accuracy: 1 if ANY of the answer keywords appear in the response,
    0 otherwise. Case-insensitive matching.
    """
    response_lower = response.lower()
    for keyword in answer_keywords:
        if keyword.lower() in response_lower:
            return 1
    return 0


def classify_model(model_id: str) -> tuple[str, str]:
    """
    Extract model size category and type (thinking vs instruct) from model ID.

    Returns:
        (model_size, model_type) — e.g. ("8B", "thinking")
    """
    model_lower = model_id.lower()

    # Determine type
    if "thinking" in model_lower or ":thinking" in model_lower:
        model_type = "thinking"
    else:
        model_type = "instruct"

    # Determine size
    if "235b" in model_lower:
        model_size = "235B"
    elif "30b" in model_lower or "32b" in model_lower:
        model_size = "30B"
    elif "8b" in model_lower or "7b" in model_lower:
        model_size = "8B"
    else:
        model_size = "unknown"

    return model_size, model_type
