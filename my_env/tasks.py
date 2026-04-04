TASKS = {
    "easy": {
        "ticket_id": "T1",
        "message": "My order is delayed.",
        "ground_truth": {
            "intent": "delay",
            "resolution": "check_status"
        }
    },
    "medium": {
        "ticket_id": "T2",
        "message": "Wrong product received and delivery was late.",
        "ground_truth": {
            "intent": ["wrong_item", "delay"],
            "resolution": "replace_or_refund"
        }
    },
    "hard": {
        "ticket_id": "T3",
        "message": "I want refund, compensation and escalation NOW!",
        "ground_truth": {
            "intent": ["refund", "angry"],
            "resolution": "refund_escalation"
        }
    }
}