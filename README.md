---
title: OpenEnv Customer Support
emoji: ":rocket:"
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

A customer-support simulation environment for training and evaluating agents on realistic service operations: shipment delays, returns recovery, and high-stakes escalation handling.

## Motivation

Many agent benchmarks reward surface-level politeness. Real support work is harder: the agent has to identify the real failure mode, stay inside policy, calm the user down, and choose an operationally valid next step. This environment is designed to measure those behaviors with dense reward and deterministic graders.

## What makes this benchmark stronger

- Real-world support domain instead of a toy task.
- Three escalating scenarios with distinct operational pressures.
- Policy-aware reward shaping that scores more than generic keyword overlap.
- Deterministic follow-up messages so trajectories are reproducible.
- Live Hugging Face Space homepage for reviewers plus standard OpenEnv endpoints for agents.

## Observation Space

`Observation` includes:

- `ticket_id`: active support case id
- `task_name`: task id for the current scenario
- `difficulty`: easy, medium, or hard
- `customer_message`: latest customer-facing message
- `status`: current ticket status
- `customer_profile`: structured context such as tier, sentiment, and order value
- `policy_hint`: operational constraint the agent should respect
- `success_criteria`: checklist of what a strong reply should accomplish
- `history`: prior agent replies in the current episode

## Action Space

`Action` includes:

- `reply`: the support-agent response
- `mark_resolved`: whether the agent claims the ticket is resolved

## Reward Design

Each `step()` returns a normalized reward in the open interval `(0, 1)`. The reward is dense, trajectory-aware, and intentionally shaped to reflect real service quality.

Reward breakdown:

- `0.15` empathy
- `0.25` issue diagnosis / intent coverage
- `0.20` recovery plan quality
- `0.15` policy compliance
- `0.10` de-escalation
- `0.10` ownership language
- `0.05` clarity
- negative penalties for vague filler, repetition, blame, or risky promises

The full reward breakdown is returned in `info.reward_breakdown`.

## Tasks

- `easy` - **Delayed Anniversary Gift**
  Gold-tier customer with a delayed order. The agent should acknowledge the delay, check carrier status, and set a clear update window without overpromising.
- `medium` - **Wrong Item And Delivery Delay**
  Multi-issue logistics case. The agent must address both the late delivery and the wrong item, then explain replacement or refund plus the return path.
- `hard` - **Refund, Compensation, And Executive Escalation**
  High-value angry customer after repeated contacts. The agent needs to de-escalate, take ownership, begin refund handling, escalate appropriately, and discuss compensation safely.

## Environment behavior

- `reset()` starts a clean scenario state and returns the initial observation.
- `step(action)` grades the reply, updates the conversation, and returns `observation`, `reward`, `done`, and `info`.
- Customer follow-ups depend on reply quality, so stronger replies calm the case while weak replies increase pressure.
- Prematurely marking a ticket as resolved is penalized and keeps the episode open.

## Run locally

```bash
pip install -r requirements.txt
uvicorn server.app:app --reload
```

## API quickstart

Reset with a specific task:

```bash
curl -X POST "http://127.0.0.1:8000/reset?task_name=medium"
```

Submit an agent reply:

```bash
curl -X POST "http://127.0.0.1:8000/step" \
  -H "content-type: application/json" \
  -d '{"reply": "Sorry this order arrived late and with the wrong item. I can arrange a replacement or refund and send the return label today.", "mark_resolved": false}'
```

List available tasks:

```bash
curl "http://127.0.0.1:8000/tasks"
```

## Baseline inference

The root-level `inference.py` runs all three tasks in sequence, uses the OpenAI client when credentials are available, and emits the required structured stdout logs:

- `[START] task=... env=... model=...`
- `[STEP] step=... action=... reward=... done=... error=...`
- `[END] success=... steps=... score=... rewards=...`

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

- `easy`: `0.77`
- `medium`: `0.93`
- `hard`: `0.85`
- `average`: `0.85`

## Deploy on Hugging Face Spaces

Use a Docker Space for this repository.

1. Create a new Space and choose Docker as the SDK.
2. Push this repository as-is.
3. Open:
   - `https://<your-space>.hf.space/` for the interactive homepage
   - `https://<your-space>.hf.space/health` for health check
   - `https://<your-space>.hf.space/docs` for the API docs

## Validation commands

```bash
python -m py_compile server/app.py my_env/*.py tests/test_env.py tests/test_server.py
python -m unittest discover -s tests
uv run openenv validate
uv run python inference.py
```
