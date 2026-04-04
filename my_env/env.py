import random
from my_env.models import Observation, Action
from my_env.tasks import TASKS
from my_env.graders import calculate_reward

class CustomerSupportEnv:

    def __init__(self, task_name="easy"):
        self.task_name = task_name
        self.task = TASKS[task_name]
        self.history = []
        self.turn = 0
        self.max_turns = 5
        self.done = False

    async def reset(self):
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
                history=self.history
            ),
            "reward": 0.0,
            "done": self.done
        }

    def _customer_response(self):
        if self.turn == 0:
            return self.task["message"]

        responses = [
            "Can you explain more?",
            "This is frustrating!",
            "Please resolve this quickly.",
            "What are you doing about it?"
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
                history=self.history
            ),
            "reward": reward,
            "done": self.done,
            "info": {}
        }

    async def state(self):
        return self._get_state()

    async def close(self):
        pass

    @classmethod
    async def from_docker_image(cls, image_name):
        return cls()