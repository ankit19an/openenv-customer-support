from fastapi import FastAPI, HTTPException
from my_env.env import CustomerSupportEnv
from my_env.models import Action
from my_env.tasks import TASKS

app = FastAPI(title="Customer Support RL Env")

env = CustomerSupportEnv("easy")


@app.get("/")
async def root():
    return {
        "name": "Customer Support RL Env",
        "docs": "/docs",
        "health": "/health",
        "tasks": "/tasks",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/reset")
async def reset(task_name: str | None = None):
    try:
        return await env.reset(task_name=task_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/step")
async def step(action: Action):
    return await env.step(action)


@app.get("/state")
async def state():
    return await env.state()


@app.get("/tasks")
async def tasks():
    return {"tasks": sorted(TASKS)}