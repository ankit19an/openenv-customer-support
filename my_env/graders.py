from __future__ import annotations

from collections.abc import Iterable

from my_env.models import Reward


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


def score_reply(reply: str, ground_truth: dict, previous_history: Iterable[str] | None = None) -> Reward:
    """Return a normalized reward breakdown for a customer-support reply."""

    text = reply.lower()
    history = [item.lower() for item in (previous_history or [])]
    empathy = 0.0
    intent_coverage = 0.0
    resolution_quality = 0.0
    clarity = 0.0
    penalties = 0.0

    # Baseline empathy signal
    if any(word in text for word in ("sorry", "apolog", "understand")):
        empathy = 0.2

    # Intent coverage based on task metadata
    intents = _as_list(ground_truth.get("intent", []))
    if intents:
        matched_intents = sum(
            1
            for intent in intents
            if any(keyword in text for keyword in INTENT_KEYWORDS.get(intent, {intent}))
        )
        intent_coverage = 0.4 * (matched_intents / len(intents))

    # Resolution strategy coverage
    resolution = ground_truth.get("resolution")
    if resolution:
        if any(keyword in text for keyword in RESOLUTION_KEYWORDS.get(resolution, {resolution})):
            resolution_quality = 0.3

    # Longer, concrete replies are usually better than one-liners
    if len(reply.split()) >= 10:
        clarity = 0.1

    # Penalize vague filler that gives no operational value
    if any(phrase in text for phrase in ("thanks, noted", "noted", "okay", "k")):
        penalties -= 0.15

    # Penalize exact repetition to discourage loop-like behavior
    if history and text == history[-1]:
        penalties -= 0.2

    value = min(max(empathy + intent_coverage + resolution_quality + clarity + penalties, 0.0), 1.0)
    return Reward(
        value=value,
        empathy=empathy,
        intent_coverage=intent_coverage,
        resolution_quality=resolution_quality,
        clarity=clarity,
        penalties=penalties,
    )


def calculate_reward(reply: str, ground_truth: dict) -> float:
    return score_reply(reply, ground_truth).value
