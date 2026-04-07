import os
import sys
from typing import Optional

from openai import OpenAI


API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-R1:fastest")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

client: Optional[OpenAI] = (
    OpenAI(
        base_url=API_BASE_URL,
        api_key=HF_TOKEN,
    )
    if HF_TOKEN
    else None
)


def emit_event(event: str, **fields: object) -> None:
    details = " ".join(f"{key}={value}" for key, value in fields.items())
    line = f"[{event}]"
    if details:
        line = f"{line} {details}"
    print(line, flush=True)


def run_inference(prompt: str) -> str:
    task_name = os.getenv("TASK_NAME", "customer-support")
    steps = 1
    score = 0.0
    reward = 0.0

    emit_event("START", task=task_name, model=MODEL_NAME)
    emit_event("STEP", step=steps, reward=reward)

    response_text = ""
    if client is not None:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = response.choices[0].message.content or ""
        score = 1.0 if response_text else 0.0

    emit_event("END", task=task_name, score=score, steps=steps)
    return response_text


def main() -> None:
    prompt = " ".join(sys.argv[1:]).strip() or "Reply with one short helpful sentence."
    run_inference(prompt)


if __name__ == "__main__":
    main()
