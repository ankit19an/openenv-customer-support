---
title: OpenEnv Customer Support
emoji: "🚀"
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# OpenEnv Customer Support

A customer-support simulation environment for training and evaluating agent behavior under escalating ticket pressure.

## Features

- FastAPI environment API with `/reset`, `/step`, `/state`, `/tasks`, and `/health` endpoints.
- Live in-browser playground on the homepage so reviewers can test scenarios without touching curl.
- Three escalating ticket difficulties: `easy`, `medium`, `hard`.
- Reward function that scores empathy, intent coverage, and resolution quality.
- OpenEnv-compatible repo layout with `uv.lock`, `pyproject.toml`, and `openenv.yaml`.

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
```
