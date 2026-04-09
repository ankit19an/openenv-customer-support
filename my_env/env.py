from __future__ import annotations

from typing import Any

from my_env.graders import MAX_REWARD, MIN_REWARD, score_reply
from my_env.models import Action, Observation
from my_env.tasks import TASKS


class CustomerSupportEnv:
    def __init__(self, task_name: str = "easy"):
        self.max_turns = 5
        self.task_name = ""
        self.task: dict[str, Any] = {}
        self.history: list[str] = []
        self.turn = 0
        self.done = False
        self._observation: Observation | None = None
        self._reward = self._normalize_reward(0.0)
        self._info: dict[str, Any] = {}
        self.set_task(task_name)
        self._snapshot(customer_message=self.task["message"], status="open", reward=0.0)

    def set_task(self, task_name: str) -> None:
        if task_name not in TASKS:
            supported = ", ".join(sorted(TASKS))
            raise ValueError(f"Unknown task '{task_name}'. Supported tasks: {supported}")

        self.task_name = task_name
        self.task = TASKS[task_name]
        self.max_turns = int(self.task.get("max_turns", 5))

    def _normalize_reward(self, reward: float) -> float:
        return min(max(float(reward), MIN_REWARD), MAX_REWARD)

    def _base_info(self) -> dict[str, Any]:
        return {
            "task_name": self.task_name,
            "difficulty": self.task["difficulty"],
            "title": self.task["title"],
            "turn": self.turn,
            "max_turns": self.max_turns,
        }

    def _snapshot(
        self,
        *,
        customer_message: str,
        status: str,
        reward: float,
        extra_info: dict[str, Any] | None = None,
    ) -> None:
        info = self._base_info()
        if extra_info:
            info.update(extra_info)

        self._observation = Observation(
            ticket_id=self.task["ticket_id"],
            task_name=self.task_name,
            difficulty=self.task["difficulty"],
            customer_message=customer_message,
            status=status,
            customer_profile=dict(self.task.get("customer_profile", {})),
            policy_hint=self.task["policy_hint"],
            success_criteria=list(self.task.get("success_criteria", [])),
            history=list(self.history),
        )
        self._reward = self._normalize_reward(reward)
        self._info = info

    def _get_state(self) -> dict[str, Any]:
        if self._observation is None:
            self._snapshot(customer_message=self.task["message"], status="open", reward=0.0)

        return {
            "observation": self._observation.model_copy(deep=True),
            "reward": self._reward,
            "done": self.done,
            "info": dict(self._info),
        }

    def _quality_band(self, reward: float, resolution_quality: float) -> str:
        if reward >= 0.72 and resolution_quality >= 0.10:
            return "strong"
        if reward >= 0.42:
            return "partial"
        return "weak"

    def _resolution_ready(self, reward_breakdown) -> bool:
        needs_deescalation = bool(self.task["ground_truth"].get("needs_deescalation"))
        if reward_breakdown.intent_coverage < 0.12:
            return False
        if reward_breakdown.resolution_quality < 0.10:
            return False
        if reward_breakdown.policy_compliance < 0.07:
            return False
        if needs_deescalation and reward_breakdown.deescalation < 0.08:
            return False
        return True

    def _follow_up_message(self, band: str, *, resolved: bool = False, premature: bool = False) -> str:
        follow_ups = self.task["follow_ups"]
        if premature:
            return follow_ups["premature_resolve"]
        if resolved:
            return follow_ups["resolved"]

        messages = follow_ups[band]
        index = min(max(self.turn - 1, 0), len(messages) - 1)
        return messages[index]

    async def reset(self, task_name: str | None = None):
        if task_name is not None:
            self.set_task(task_name)

        self.history = []
        self.turn = 0
        self.done = False
        self._snapshot(customer_message=self.task["message"], status="open", reward=0.0)
        return self._get_state()

    async def step(self, action: Action):
        if self.done:
            return self._get_state()

        self.turn += 1
        previous_history = list(self.history)
        self.history.append(action.reply)

        reward_breakdown = score_reply(action.reply, self.task["ground_truth"], previous_history)
        reward = self._normalize_reward(reward_breakdown.value)
        resolution_ready = self._resolution_ready(reward_breakdown)
        quality_band = self._quality_band(reward, reward_breakdown.resolution_quality)
        premature_resolution = False
        status = "open"

        if action.mark_resolved and resolution_ready:
            self.done = True
            status = "resolved"
            customer_message = self._follow_up_message(quality_band, resolved=True)
        elif action.mark_resolved:
            premature_resolution = True
            reward = self._normalize_reward(reward - 0.14)
            customer_message = self._follow_up_message(quality_band, premature=True)
        elif self.turn >= self.max_turns:
            self.done = True
            if resolution_ready:
                status = "resolved"
                customer_message = self._follow_up_message(quality_band, resolved=True)
            else:
                status = "escalated"
                reward = self._normalize_reward(reward - 0.08)
                customer_message = self.task["follow_ups"]["weak"][-1]
        else:
            customer_message = self._follow_up_message(quality_band)

        self._snapshot(
            customer_message=customer_message,
            status=status,
            reward=reward,
            extra_info={
                "quality_band": quality_band,
                "resolution_ready": resolution_ready,
                "premature_resolution": premature_resolution,
                "reward_breakdown": reward_breakdown.model_dump(),
            },
        )
        return self._get_state()

    async def state(self):
        return self._get_state()

    async def close(self):
        pass

    @classmethod
    async def from_docker_image(cls, image_name):
        return cls()
