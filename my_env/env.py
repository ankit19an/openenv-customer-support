from __future__ import annotations

import random
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

    def _normalize_reward(self, reward: float) -> float:
        return min(max(float(reward), MIN_REWARD), MAX_REWARD)

    def _base_info(self) -> dict[str, Any]:
        return {
            "task_name": self.task_name,
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
            customer_message=customer_message,
            status=status,
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

    def _customer_response(self) -> str:
        if self.turn == 0:
            return self.task["message"]

        responses = [
            "Can you explain more?",
            "This is frustrating!",
            "Please resolve this quickly.",
            "What are you doing about it?",
        ]
        return random.choice(responses)

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

        if action.mark_resolved or self.turn >= self.max_turns:
            self.done = True

        customer_message = (
            self._observation.customer_message
            if self.done and self._observation is not None
            else self._customer_response()
        )
        self._snapshot(
            customer_message=customer_message,
            status="resolved" if self.done else "open",
            reward=reward,
            extra_info={"reward_breakdown": reward_breakdown.model_dump()},
        )
        return self._get_state()

    async def state(self):
        return self._get_state()

    async def close(self):
        pass

    @classmethod
    async def from_docker_image(cls, image_name):
        return cls()
