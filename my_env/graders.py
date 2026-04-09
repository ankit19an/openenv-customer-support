from __future__ import annotations

from collections.abc import Iterable

from my_env.models import Reward

MIN_REWARD = 1e-6
MAX_REWARD = 1.0 - 1e-6


INTENT_KEYWORDS = {
    "delay": {"delay", "late", "shipping", "shipment", "track", "tracking", "carrier", "status"},
    "wrong_item": {
        "wrong item",
        "wrong size",
        "wrong color",
        "wrong product",
        "incorrect item",
        "incorrect product",
        "mix-up",
    },
    "refund": {"refund", "money back", "reimburse", "refunded"},
    "angry": {"understand", "frustrating", "sorry", "priority", "urgent", "third contact"},
    "compensation": {"compensation", "credit", "coupon", "goodwill", "gesture"},
}

ACTION_KEYWORDS = {
    "track_package": {"track", "tracking", "carrier", "shipment", "status", "scan"},
    "share_eta": {"eta", "delivery window", "update", "timeline", "arrival", "today", "within"},
    "replace_item": {"replace", "replacement", "ship the correct", "send a new", "exchange"},
    "offer_refund": {"refund", "money back", "refunded", "refund today"},
    "send_return_label": {"return label", "pickup", "courier pickup", "send it back", "return process"},
    "escalate_specialist": {"escalate", "specialist", "supervisor", "manager", "senior support"},
    "review_compensation": {"compensation", "goodwill", "credit", "coupon", "gesture"},
}

POLICY_KEYWORDS = {
    "confirm_investigation": {"check", "investigate", "review", "look into", "track"},
    "share_next_update": {"update", "follow up", "confirmation", "today", "within", "next"},
    "mention_return_path": {"return label", "pickup", "courier", "send it back", "return process"},
    "acknowledge_priority": {"priority", "urgent", "personally", "expedite", "third contact", "today"},
}

RESOLUTION_TO_ACTIONS = {
    "check_status": ["track_package", "share_eta"],
    "replace_or_refund": ["replace_item", "offer_refund", "send_return_label"],
    "refund_escalation": ["offer_refund", "escalate_specialist", "review_compensation"],
}

EMPATHY_KEYWORDS = {"sorry", "apolog", "understand", "frustrating", "inconvenience"}
DEESCALATION_KEYWORDS = {
    "understand",
    "sorry",
    "frustrating",
    "priority",
    "urgent",
    "take care",
    "personally",
    "help",
}
OWNERSHIP_KEYWORDS = {"i will", "i can", "i am", "i'll", "let me", "i have", "i'm going to"}
VAGUE_PHRASES = {
    "thanks, noted",
    "noted",
    "okay",
    "ok",
    "k",
    "we will check",
    "please wait",
}
BLAME_PHRASES = {"you should have", "you ordered", "your mistake", "your fault"}


def _as_list(value: str | Iterable[str]) -> list[str]:
    if isinstance(value, str):
        return [value]
    return list(value)


def _normalize_reward(value: float) -> float:
    return min(max(float(value), MIN_REWARD), MAX_REWARD)


def _keyword_fraction(text: str, labels: Iterable[str], mapping: dict[str, set[str]]) -> float:
    items = list(labels)
    if not items:
        return 0.0

    matched = 0
    for label in items:
        keywords = mapping.get(label, {label.replace("_", " ")})
        if any(keyword in text for keyword in keywords):
            matched += 1
    return matched / len(items)


def score_reply(reply: str, ground_truth: dict, previous_history: Iterable[str] | None = None) -> Reward:
    """Return a normalized reward breakdown for a customer-support reply."""

    text = " ".join(reply.lower().split())
    history = [" ".join(item.lower().split()) for item in (previous_history or [])]

    empathy = 0.0
    intent_coverage = 0.0
    resolution_quality = 0.0
    policy_compliance = 0.0
    deescalation = 0.0
    ownership = 0.0
    clarity = 0.0
    penalties = 0.0

    if any(word in text for word in EMPATHY_KEYWORDS):
        empathy = 0.15

    intents = _as_list(ground_truth.get("intent", []))
    if intents:
        intent_coverage = 0.25 * _keyword_fraction(text, intents, INTENT_KEYWORDS)

    required_actions = ground_truth.get("required_actions")
    if not required_actions and ground_truth.get("resolution"):
        required_actions = RESOLUTION_TO_ACTIONS.get(ground_truth["resolution"], [])
    required_actions = _as_list(required_actions or [])
    if required_actions:
        resolution_quality = 0.20 * _keyword_fraction(text, required_actions, ACTION_KEYWORDS)

    policy_requirements = _as_list(ground_truth.get("policy_requirements", []))
    if policy_requirements:
        policy_compliance = 0.15 * _keyword_fraction(text, policy_requirements, POLICY_KEYWORDS)

    if ground_truth.get("needs_deescalation"):
        if any(word in text for word in DEESCALATION_KEYWORDS):
            deescalation = 0.10
    elif empathy > 0.0:
        deescalation = 0.05

    if any(keyword in text for keyword in OWNERSHIP_KEYWORDS):
        ownership = 0.10

    word_count = len(reply.split())
    if 12 <= word_count <= 70:
        clarity = 0.05

    if any(phrase in text for phrase in VAGUE_PHRASES):
        penalties -= 0.18

    if history and text == history[-1]:
        penalties -= 0.12

    if word_count < 6:
        penalties -= 0.12

    forbidden_phrases = _as_list(ground_truth.get("forbidden_phrases", []))
    if any(phrase in text for phrase in forbidden_phrases):
        penalties -= 0.25

    if any(phrase in text for phrase in BLAME_PHRASES):
        penalties -= 0.25

    value = _normalize_reward(
        empathy
        + intent_coverage
        + resolution_quality
        + policy_compliance
        + deescalation
        + ownership
        + clarity
        + penalties
    )
    return Reward(
        value=value,
        empathy=empathy,
        intent_coverage=intent_coverage,
        resolution_quality=resolution_quality,
        policy_compliance=policy_compliance,
        deescalation=deescalation,
        ownership=ownership,
        clarity=clarity,
        penalties=penalties,
    )


def calculate_reward(reply: str, ground_truth: dict) -> float:
    return score_reply(reply, ground_truth).value
