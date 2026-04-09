TASKS = {
    "easy": {
        "ticket_id": "T1",
        "title": "Delayed Anniversary Gift",
        "difficulty": "easy",
        "summary": "A worried Gold-tier customer needs a real shipment update, not a canned apology.",
        "message": (
            "Hi, my anniversary gift order #1048 was supposed to arrive on Tuesday and the "
            "tracking has not moved in two days. Can someone tell me where it is?"
        ),
        "customer_profile": {
            "tier": "Gold",
            "sentiment": "concerned",
            "order_value": "$84",
            "region": "Bengaluru",
        },
        "policy_hint": (
            "Check live carrier status, share the next update window, and avoid promising a "
            "refund before the shipment is investigated."
        ),
        "success_criteria": [
            "Acknowledge the delay empathetically.",
            "Offer to check tracking or carrier status.",
            "Give a concrete next-step or update window.",
        ],
        "max_turns": 4,
        "ground_truth": {
            "intent": ["delay"],
            "resolution": "check_status",
            "required_actions": ["track_package", "share_eta"],
            "policy_requirements": ["confirm_investigation", "share_next_update"],
            "forbidden_phrases": [
                "guarantee it arrives today",
                "instant refund right now",
                "nothing we can do",
            ],
            "needs_deescalation": False,
        },
        "follow_ups": {
            "strong": [
                "Thanks. Please send me the tracking update as soon as you have it.",
                "That helps. I will wait for the carrier update today.",
            ],
            "partial": [
                "Okay, but I still need to know when it will actually arrive.",
                "I understand. Can you confirm when I should expect the next update?",
            ],
            "weak": [
                "You did not actually tell me where the package is.",
                "This still sounds generic. I need a real status update.",
            ],
            "premature_resolve": "I still do not know where the parcel is, so please do not close this ticket yet.",
            "resolved": "Thanks for checking the shipment and setting expectations clearly.",
        },
    },
    "medium": {
        "ticket_id": "T2",
        "title": "Wrong Item And Delivery Delay",
        "difficulty": "medium",
        "summary": "A multi-issue case that requires diagnosis, logistics recovery, and return handling.",
        "message": (
            "My order finally arrived two days late, but it is the wrong size and color. "
            "I needed it for this weekend. What are you going to do about it?"
        ),
        "customer_profile": {
            "tier": "Standard",
            "sentiment": "frustrated",
            "order_value": "$129",
            "region": "Pune",
        },
        "policy_hint": (
            "Address both failures, offer replacement or refund, and explain the return path "
            "for the incorrect item."
        ),
        "success_criteria": [
            "Recognize both the late delivery and the wrong item.",
            "Offer replacement or refund clearly.",
            "Explain how the incorrect item will be returned or picked up.",
        ],
        "max_turns": 5,
        "ground_truth": {
            "intent": ["wrong_item", "delay"],
            "resolution": "replace_or_refund",
            "required_actions": ["replace_item", "offer_refund", "send_return_label"],
            "policy_requirements": ["confirm_investigation", "mention_return_path"],
            "forbidden_phrases": [
                "keep the wrong item and buy again",
                "we cannot help with that",
                "it is your fault",
            ],
            "needs_deescalation": True,
        },
        "follow_ups": {
            "strong": [
                "A replacement or refund works, but I need the return process to be easy.",
                "Okay, if you handle the return label and replacement quickly that would help.",
            ],
            "partial": [
                "You mentioned a refund, but what about the wrong item I received?",
                "I still need to know how I return this incorrect product.",
            ],
            "weak": [
                "You skipped half the problem. The order was late and wrong.",
                "This does not solve the wrong item issue at all.",
            ],
            "premature_resolve": "The wrong product is still with me and the order problem is not resolved yet.",
            "resolved": "Thanks for covering both the replacement or refund and the return steps clearly.",
        },
    },
    "hard": {
        "ticket_id": "T3",
        "title": "Refund, Compensation, And Executive Escalation",
        "difficulty": "hard",
        "summary": "A high-value angry customer needs de-escalation, ownership, and policy-safe recovery.",
        "message": (
            "This is my third contact about order #9912. The package was late, the item arrived "
            "damaged, and I want a refund, compensation, and this escalated right now."
        ),
        "customer_profile": {
            "tier": "Platinum",
            "sentiment": "angry",
            "order_value": "$420",
            "region": "Mumbai",
        },
        "policy_hint": (
            "Show strong ownership, start the refund path, escalate to a specialist, and frame "
            "compensation as a reviewed goodwill option rather than a guaranteed promise."
        ),
        "success_criteria": [
            "De-escalate and acknowledge repeated contact.",
            "Start refund and escalation language in the same reply.",
            "Handle compensation carefully without making an unapproved guarantee.",
        ],
        "max_turns": 5,
        "ground_truth": {
            "intent": ["refund", "angry", "compensation"],
            "resolution": "refund_escalation",
            "required_actions": ["offer_refund", "escalate_specialist", "review_compensation"],
            "policy_requirements": ["acknowledge_priority", "share_next_update"],
            "forbidden_phrases": [
                "guaranteed compensation",
                "i promise cash back today",
                "calm down",
            ],
            "needs_deescalation": True,
        },
        "follow_ups": {
            "strong": [
                "Fine. If you really start the refund and escalation today, send me the case details now.",
                "That is better. I need confirmation of the refund and specialist escalation today.",
            ],
            "partial": [
                "You mentioned a refund, but what about the escalation and compensation review?",
                "I still need confidence that someone senior is actually handling this.",
            ],
            "weak": [
                "This sounds like another generic reply. I have already heard that twice.",
                "You are not taking ownership here, and I still want escalation.",
            ],
            "premature_resolve": "This is definitely not resolved. I asked for refund, escalation, and compensation review.",
            "resolved": "I will watch for the refund confirmation and specialist follow-up today.",
        },
    },
}
