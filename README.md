---
title: OpenEnv Customer Support
emoji: "🚀"
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
tags:
  - openenv
  - customer-support
  - fastapi
---

# OpenEnv Customer Support

A customer-support simulation environment for training and evaluating agent behavior under escalating ticket pressure.

## Motivation

Customer support is a real operational workflow that frontier agents still struggle with: they need to calm the user, identify the root issue, choose the right recovery path, and avoid repetitive or unhelpful responses. This environment is built to make those behaviors measurable in a compact, reproducible benchmark.

## Features

- FastAPI environment API with `/reset`, `/step`, `/state`, `/tasks`, and `/health` endpoints.
- Live in-browser playground on the homepage so reviewers can test scenarios without touching curl.
- Three escalating ticket difficulties: `easy`, `medium`, `hard`.
- Reward function that scores empathy, intent coverage, and resolution quality.
- OpenEnv-compatible repo layout with `uv.lock`, `pyproject.toml`, and `openenv.yaml`.

## Observation Space

`Observation` contains:

- `ticket_id`: the active customer-support case id
- `customer_message`: the latest customer utterance
- `status`: `open` or `resolved`
- `history`: the running list of prior agent replies

## Action Space

`Action` contains:

- `reply`: the support agent response for the current turn
- `mark_resolved`: whether the agent considers the ticket resolved

## Reward Design

Each `step()` returns a normalized reward in `[0.0, 1.0]`. The grader provides dense feedback instead of only end-of-episode success.

- `0.20` empathy signal
- `0.40` intent coverage
- `0.30` resolution quality
- `0.10` clarity bonus
- negative penalties for vague filler and repeated replies

The reward breakdown is included in `info.reward_breakdown`.

## Tasks

- `easy` — **Delayed Order**
  One-issue support case. The agent should acknowledge the delay and move toward shipment tracking or status checking.
- `medium` — **Wrong Item And Delay**
  Multi-issue support case. The agent needs to cover both the wrong product and the delivery delay, then propose replacement or refund.
- `hard` — **Refund And Escalation**
  High-friction support case. The agent should de-escalate, recognize urgency, and choose refund/escalation language appropriately.

## Run locally

```bash
pip install -r requirements.txt
uvicorn server.app:app --reload
```

## API quickstart

Reset with a specific task:

```bash
curl -X POST 'http://127.0.0.1:8000/reset?task_name=medium'
```

Submit an agent reply:

```bash
curl -X POST 'http://127.0.0.1:8000/step' \
  -H 'content-type: application/json' \
  -d '{"reply": "Sorry about the delay. I will check shipment status and arrange a replacement or refund immediately.", "mark_resolved": false}'
```

List available tasks:

```bash
curl 'http://127.0.0.1:8000/tasks'
```

## Demo flow

1. Open the Space root page.
2. Launch a scenario from the **Live Agent Arena**.
3. Respond as the support agent and watch reward + turn state update in real time.
4. Use `/docs` if you want direct API inspection afterward.

## Baseline Inference

The root-level `inference.py` runs all three tasks in sequence, uses the OpenAI client for model-backed replies when credentials are available, and emits structured stdout logs in `[START]`, `[STEP]`, and `[END]` format for each episode.

Required environment variables:

- `API_BASE_URL`
- `MODEL_NAME`
- `HF_TOKEN` or `OPENAI_API_KEY`
- `LOCAL_IMAGE_NAME` (optional)

Run it with:

```bash
uv run python inference.py
```

### Current Baseline Scores

- `easy`: `0.75`
- `medium`: `0.90`
- `hard`: `0.90`
- `average`: `0.85`

## Deploy on Hugging Face Spaces

Use a **Docker Space** for this repository.

1. Create a new Space and choose **Docker** as the SDK.
2. Push this repository as-is (the included `Dockerfile` listens on port `7860`, which Spaces expects).
3. Ensure these files are present and non-empty:
   - `Dockerfile`
   - `requirements.txt`
   - `server/app.py`
   - `pyproject.toml`
   - `uv.lock`
4. After build completes, open:
   - `https://<your-space>.hf.space/` for the interactive homepage
   - `https://<your-space>.hf.space/health` for health check
   - `https://<your-space>.hf.space/docs` for Swagger UI

If build fails, check the Space build logs first; dependency issues are usually caused by missing or empty `requirements.txt`.

## Run checks

```bash
python -m py_compile server/app.py my_env/*.py tests/test_env.py tests/test_server.py
python -m unittest discover -s tests
uv run openenv validate
uv run python inference.py
```
