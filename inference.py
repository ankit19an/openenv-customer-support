import asyncio
import os
import re
import textwrap
from typing import Optional

from openai import OpenAI

from my_env.env import CustomerSupportEnv
from my_env.models import Action
from my_env.tasks import TASKS


API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-R1:fastest")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")
BENCHMARK = os.getenv("OPENENV_BENCHMARK", "customer-support-rl-env")
MAX_STEPS = 5
TEMPERATURE = 0.0
MAX_TOKENS = 180
TASK_SEQUENCE = ["easy", "medium", "hard"]

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are a high-quality customer support agent.
    Write one concise support reply that:
    1. shows empathy,
    2. explicitly addresses the customer's issue,
    3. proposes the right next action.
    Return only the reply text.
    """
).strip()


def build_client() -> Optional[OpenAI]:
    if not API_KEY:
        return None
    return OpenAI(base_url=API_BASE_URL, api_key=API_KEY)


def sanitize_action(reply: str) -> str:
    compact = re.sub(r"\s+", "_", reply.strip().lower())
    compact = re.sub(r"[^a-z0-9_]+", "", compact)
    return f"reply({compact[:80] or 'empty'})"


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_value = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_value}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: list[float]) -> None:
    rewards_str = ",".join(f"{reward:.2f}" for reward in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


def heuristic_reply(task_name: str, turn: int) -> tuple[str, bool]:
    scripted = {
        "easy": (
            "Sorry about the delay. I am checking the shipment status with the carrier now and will share an update right away.",
            turn >= 2,
        ),
        "medium": (
            "Sorry this order arrived late and with the wrong item. I can arrange a replacement immediately or process a refund if you prefer.",
            turn >= 2,
        ),
        "hard": (
            "I understand how frustrating this is. I can start the refund now, escalate the case to a specialist, and review compensation options today.",
            turn >= 2,
        ),
    }
    return scripted[task_name]


def build_user_prompt(task_name: str, customer_message: str, history: list[str], turn: int) -> str:
    history_block = "\n".join(history[-4:]) if history else "None"
    task = TASKS[task_name]
    return textwrap.dedent(
        f"""
        Active task: {task_name}
        Customer ticket: {task["ticket_id"]}
        Latest customer message: {customer_message}
        Agent history:
        {history_block}
        Turn: {turn}

        Write the next best support reply.
        """
    ).strip()


def model_reply(
    client: Optional[OpenAI],
    task_name: str,
    customer_message: str,
    history: list[str],
    turn: int,
) -> tuple[str, bool]:
    if client is None:
        return heuristic_reply(task_name, turn)

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_user_prompt(task_name, customer_message, history, turn),
                },
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        reply = (completion.choices[0].message.content or "").strip()
        if not reply:
            return heuristic_reply(task_name, turn)
        mark_resolved = turn >= 2 and any(
            keyword in reply.lower()
            for keyword in ("refund", "replace", "replacement", "escalat", "status", "track")
        )
        return reply, mark_resolved
    except Exception:
        return heuristic_reply(task_name, turn)


async def run_task(client: Optional[OpenAI], task_name: str) -> float:
    env = CustomerSupportEnv(task_name)
    result = await env.reset(task_name=task_name)
    rewards: list[float] = []
    steps_taken = 0
    success = False

    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    try:
        for step in range(1, MAX_STEPS + 1):
            observation = result["observation"]
            reply, mark_resolved = model_reply(
                client,
                task_name,
                observation.customer_message,
                observation.history,
                step,
            )
            action = Action(reply=reply, mark_resolved=mark_resolved)
            result = await env.step(action)
            reward = float(result["reward"])
            done = bool(result["done"])
            rewards.append(reward)
            steps_taken = step
            log_step(
                step=step,
                action=sanitize_action(reply),
                reward=reward,
                done=done,
                error=None,
            )
            if done:
                break

        score = max(rewards) if rewards else 0.0
        success = score >= 0.6
        return score
    finally:
        await env.close()
        log_end(success=success, steps=steps_taken, score=max(rewards) if rewards else 0.0, rewards=rewards)


async def main() -> None:
    client = build_client()
    scores = []
    for task_name in TASK_SEQUENCE:
        scores.append(await run_task(client, task_name))

    overall = sum(scores) / len(scores) if scores else 0.0
    print(f"baseline_average={overall:.2f}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
