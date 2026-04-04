import random

from my_env.graders import calculate_reward
from my_env.models import Action, Observation
from my_env.tasks import TASKS


class CustomerSupportEnv:
    def __init__(self, task_name: str = "easy"):
        self.max_turns = 5
        self.task_name = ""
        self.task = {}
        self.history: list[str] = []
        self.turn = 0
        self.done = False
        self.set_task(task_name)

    def set_task(self, task_name: str) -> None:
        if task_name not in TASKS:
            supported = ", ".join(sorted(TASKS))
            raise ValueError(f"Unknown task '{task_name}'. Supported tasks: {supported}")

        self.task_name = task_name
        self.task = TASKS[task_name]

    async def reset(self, task_name: str | None = None):
        if task_name:
            self.set_task(task_name)

        self.history = []
        self.turn = 0
        self.done = False
        return self._get_state()

    def _get_state(self):
        return {
            "observation": Observation(
                ticket_id=self.task["ticket_id"],
                customer_message=self._customer_response(),
                status="open",
                history=list(self.history),
            ),
            "reward": 0.0,
            "done": self.done,
            "info": {
                "task_name": self.task_name,
                "turn": self.turn,
                "max_turns": self.max_turns,
            },
        }

    def _customer_response(self):
        if self.turn == 0:
            return self.task["message"]

        responses = [
            "Can you explain more?",
            "This is frustrating!",
            "Please resolve this quickly.",
            "What are you doing about it?",
        ]
        return random.choice(responses)

    async def step(self, action: Action):
        if self.done:
            return self._get_state()

        self.turn += 1
        self.history.append(action.reply)

        reward = calculate_reward(action.reply, self.task["ground_truth"])

        if action.mark_resolved or self.turn >= self.max_turns:
            self.done = True

        return {
            "observation": Observation(
                ticket_id=self.task["ticket_id"],
                customer_message=self._customer_response(),
                status="resolved" if self.done else "open",
                history=list(self.history),
            ),
            "reward": reward,
            "done": self.done,
            "info": {
                "task_name": self.task_name,
                "turn": self.turn,
                "max_turns": self.max_turns,
            },
        }

    async def state(self):
        return self._get_state()

    async def close(self):
        pass

    @classmethod
    async def from_docker_image(cls, image_name):
        return cls()
