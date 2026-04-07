import asyncio
import unittest

from my_env.env import CustomerSupportEnv
from my_env.graders import calculate_reward, score_reply
from my_env.models import Action


class TestCustomerSupportEnv(unittest.TestCase):
    def test_reset_can_switch_tasks(self):
        env = CustomerSupportEnv("easy")
        state = asyncio.run(env.reset(task_name="hard"))
        self.assertEqual(state["info"]["task_name"], "hard")
        self.assertEqual(state["observation"].ticket_id, "T3")

    def test_reward_prefers_ground_truth_alignment(self):
        ground_truth = {
            "intent": ["wrong_item", "delay"],
            "resolution": "replace_or_refund",
        }
        strong_reply = (
            "Sorry this was frustrating. I can see the wrong item and delay, "
            "so I will replace it today or process a refund right away."
        )
        weak_reply = "Thanks, noted."

        self.assertGreater(calculate_reward(strong_reply, ground_truth), calculate_reward(weak_reply, ground_truth))

    def test_step_marks_done_on_resolve(self):
        env = CustomerSupportEnv("easy")
        asyncio.run(env.reset())
        response = asyncio.run(
            env.step(Action(reply="Sorry, I will check status now.", mark_resolved=True))
        )
        self.assertTrue(response["done"])

    def test_reward_breakdown_includes_penalty_for_repetition(self):
        baseline = score_reply(
            "Sorry about the delay. I will check the shipment status right now.",
            {"intent": "delay", "resolution": "check_status"},
            [],
        )
        repeated = score_reply(
            "Sorry about the delay. I will check the shipment status right now.",
            {"intent": "delay", "resolution": "check_status"},
            ["Sorry about the delay. I will check the shipment status right now."],
        )
        self.assertLess(repeated.value, baseline.value)
        self.assertLess(repeated.penalties, 0.0)


if __name__ == "__main__":
    unittest.main()
