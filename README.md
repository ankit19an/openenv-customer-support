# OpenEnv Customer Support

A lightweight reinforcement-learning style environment for customer-support response training.

## Features

- FastAPI server with `/reset`, `/step`, `/state`, `/tasks`, and `/health` endpoints.
- Three built-in task difficulties: `easy`, `medium`, `hard`.
- Reward function that scores empathy + intent handling + resolution quality.

## Run locally

```bash
pip install -r requirements.txt
uvicorn server:app --reload
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

## Deploy on Hugging Face Spaces

Use a **Docker Space** for this repository.

1. Create a new Space and choose **Docker** as the SDK.
2. Push this repository as-is (the included `Dockerfile` listens on port `7860`, which Spaces expects).
3. Ensure these files are present and non-empty:
   - `Dockerfile`
   - `requirements.txt`
   - `server.py`
4. After build completes, open:
   - `https://<your-space>.hf.space/health` for health check
   - `https://<your-space>.hf.space/docs` for interactive Swagger UI

If build fails, check the Space build logs first; dependency issues are usually caused by missing or empty `requirements.txt`.

## Run checks

```bash
python -m py_compile server.py my_env/*.py tests/test_env.py
python -m unittest discover -s tests
```
