def calculate_reward(reply: str, ground_truth):
    score = 0.0
    text = reply.lower()

    # empathy
    if "sorry" in text:
        score += 0.2

    # resolution
    if "refund" in text or "replace" in text:
        score += 0.4

    # escalation
    if "escalate" in text:
        score += 0.2

    # good length response
    if len(reply.split()) > 8:
        score += 0.2

    return min(score, 1.0)