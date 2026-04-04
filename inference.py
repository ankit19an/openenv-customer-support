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


def run_inference(prompt: str) -> str:
    print("START")
    try:
        if client is None:
            raise RuntimeError("HF_TOKEN must be set before running inference.")

        print("STEP")
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""
    finally:
        print("END")


def main() -> None:
    prompt = " ".join(sys.argv[1:]).strip() or "Reply with one short helpful sentence."
    run_inference(prompt)


if __name__ == "__main__":
    main()
