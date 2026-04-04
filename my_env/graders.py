from __future__ import annotations

from collections.abc import Iterable


INTENT_KEYWORDS = {
    "delay": {"delay", "late", "shipping", "status", "track"},
    "wrong_item": {"wrong", "incorrect", "mix-up", "replace"},
    "refund": {"refund", "money back", "reimburse"},
    "angry": {"understand", "frustrating", "urgent", "priority"},
}

RESOLUTION_KEYWORDS = {
    "check_status": {"track", "status", "carrier", "update"},
    "replace_or_refund": {"replace", "replacement", "refund", "return"},
    "refund_escalation": {"refund", "escalate", "manager", "specialist"},
}


def _as_list(value: str | Iterable[str]) -> list[str]:
    if isinstance(value, str):
        return [value]
    return list(value)


def calculate_reward(reply: str, ground_truth: dict) -> float:
    """Score reply quality from 0.0 to 1.0 against task ground truth."""

    score = 0.0
    text = reply.lower()

    # Baseline empathy signal
    if any(word in text for word in ("sorry", "apolog", "understand")):
        score += 0.2

    # Intent coverage based on task metadata
    intents = _as_list(ground_truth.get("intent", []))
    if intents:
        matched_intents = sum(
            1
            for intent in intents
            if any(keyword in text for keyword in INTENT_KEYWORDS.get(intent, {intent}))
        )
        score += 0.4 * (matched_intents / len(intents))

    # Resolution strategy coverage
    resolution = ground_truth.get("resolution")
    if resolution:
        if any(keyword in text for keyword in RESOLUTION_KEYWORDS.get(resolution, {resolution})):
            score += 0.3

    # Longer, concrete replies are usually better than one-liners
    if len(reply.split()) >= 10:
        score += 0.1

    return min(score, 1.0)
