import asyncio
import unittest

from my_env.env import CustomerSupportEnv, MAX_REWARD, MIN_REWARD
from my_env.graders import calculate_reward, score_reply
from my_env.models import Action
from my_env.tasks import TASKS


class TestCustomerSupportEnv(unittest.TestCase):
    def test_reset_can_switch_tasks(self):
        env = CustomerSupportEnv("easy")
        state = asyncio.run(env.reset(task_name="hard"))
        self.assertEqual(state["info"]["task_name"], "hard")
        self.assertEqual(state["observation"].ticket_id, "T3")

    def test_reset_rewards_stay_in_strict_open_interval_for_all_tasks(self):
        for task_name in TASKS:
            with self.subTest(task_name=task_name):
                env = CustomerSupportEnv(task_name)
                state = asyncio.run(env.reset())
                self.assertGreater(state["reward"], 0.0)
                self.assertLess(state["reward"], 1.0)

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

        self.assertGreater(
            calculate_reward(strong_reply, ground_truth),
            calculate_reward(weak_reply, ground_truth),
        )

    def test_reward_normalization_avoids_closed_interval_edges(self):
        env = CustomerSupportEnv("easy")
        self.assertEqual(env._normalize_reward(0.0), MIN_REWARD)
        self.assertEqual(env._normalize_reward(1.0), MAX_REWARD)

    def test_grader_scores_stay_in_strict_open_interval_at_extremes(self):
        ground_truth = {
            "intent": ["wrong_item", "delay"],
            "resolution": "replace_or_refund",
        }
        weak_reply = "Thanks, noted."
        strong_reply = (
            "Sorry this was frustrating. I can see the wrong item and delay, "
            "so I will replace it today or process a refund right away."
        )

        self.assertEqual(calculate_reward(weak_reply, ground_truth), MIN_REWARD)
        self.assertEqual(calculate_reward(strong_reply, ground_truth), MAX_REWARD)

    def test_step_marks_done_on_resolve(self):
        env = CustomerSupportEnv("easy")
        asyncio.run(env.reset())
        response = asyncio.run(
            env.step(Action(reply="Sorry, I will check status now.", mark_resolved=True))
        )
        self.assertTrue(response["done"])
        self.assertEqual(response["observation"].status, "resolved")
        self.assertGreater(response["reward"], 0.0)
        self.assertLess(response["reward"], 1.0)

    def test_terminal_snapshot_stays_stable_after_done(self):
        env = CustomerSupportEnv("medium")
        asyncio.run(env.reset())
        terminal = asyncio.run(
            env.step(
                Action(
                    reply=(
                        "Sorry this arrived late and with the wrong item. "
                        "I can replace it immediately or issue a refund today."
                    ),
                    mark_resolved=True,
                )
            )
        )

        state_after_done = asyncio.run(env.state())
        repeated_step = asyncio.run(
            env.step(Action(reply="Following up again.", mark_resolved=False))
        )

        for snapshot in (state_after_done, repeated_step):
            self.assertTrue(snapshot["done"])
            self.assertEqual(snapshot["observation"].status, "resolved")
            self.assertEqual(snapshot["reward"], terminal["reward"])
            self.assertEqual(snapshot["observation"].history, terminal["observation"].history)
            self.assertEqual(snapshot["info"], terminal["info"])

    def test_non_terminal_state_is_stable_between_reads(self):
        env = CustomerSupportEnv("easy")
        asyncio.run(env.reset())
        step_state = asyncio.run(
            env.step(
                Action(
                    reply="Sorry about the delay. I am checking the shipment status now.",
                    mark_resolved=False,
                )
            )
        )
        current_state = asyncio.run(env.state())

        self.assertFalse(step_state["done"])
        self.assertEqual(current_state["reward"], step_state["reward"])
        self.assertEqual(
            current_state["observation"].customer_message,
            step_state["observation"].customer_message,
        )
        self.assertEqual(current_state["observation"].history, step_state["observation"].history)

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
