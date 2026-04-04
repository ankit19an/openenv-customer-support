import json
import os
from html import escape

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from my_env.env import CustomerSupportEnv
from my_env.models import Action
from my_env.tasks import TASKS

app = FastAPI(title="Customer Support RL Env")

env = CustomerSupportEnv("easy")


def render_homepage() -> str:
    sample_action = escape(
        json.dumps(
            {
                "reply": "Sorry about the delay. I am checking the shipment now and can arrange a replacement or refund if needed.",
                "mark_resolved": False,
            },
            indent=2,
        )
    )
    endpoint_rows = [
        ("GET", "/health", "Quick service status check."),
        ("POST", "/reset", "Start a fresh scenario, optionally with a specific task."),
        ("POST", "/step", "Submit the agent reply for the current ticket turn."),
        ("GET", "/state", "Inspect the current environment state."),
        ("GET", "/tasks", "List available scenario difficulties."),
        ("GET", "/docs", "Open the interactive Swagger interface."),
    ]
    task_themes = {
        "easy": ("Calm Delay", "linear-gradient(135deg, #34d399, #0f766e)"),
        "medium": ("Mixed Failure", "linear-gradient(135deg, #f59e0b, #c2410c)"),
        "hard": ("Escalation Risk", "linear-gradient(135deg, #fb7185, #be123c)"),
    }

    task_cards = []
    for task_name, task in TASKS.items():
        intents = task["ground_truth"]["intent"]
        if isinstance(intents, str):
            intents = [intents]
        label, accent = task_themes.get(
            task_name,
            ("Scenario", "linear-gradient(135deg, #60a5fa, #1d4ed8)"),
        )
        task_cards.append(
            f"""
            <article class="task-card">
              <div class="task-accent" style="background: {accent};"></div>
              <div class="task-header">
                <span class="task-level">{escape(task_name.title())}</span>
                <span class="task-label">{escape(label)}</span>
              </div>
              <p class="ticket-id">Ticket {escape(task["ticket_id"])}</p>
              <p class="task-message">{escape(task["message"])}</p>
              <div class="task-meta">
                <span>Intent: {escape(", ".join(intents))}</span>
                <span>Resolution: {escape(task["ground_truth"]["resolution"].replace("_", " "))}</span>
              </div>
              <code class="task-action">POST /reset?task_name={escape(task_name)}</code>
            </article>
            """
        )

    endpoint_cards = []
    for method, path, description in endpoint_rows:
        endpoint_cards.append(
            f"""
            <div class="endpoint-card">
              <span class="method {method.lower()}">{escape(method)}</span>
              <div>
                <div class="endpoint-path">{escape(path)}</div>
                <div class="endpoint-copy">{escape(description)}</div>
              </div>
            </div>
            """
        )

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Customer Support RL Env</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
    <style>
      :root {{
        --bg: #f6efe4;
        --ink: #1f2430;
        --muted: #596273;
        --panel: rgba(255, 251, 245, 0.9);
        --line: rgba(31, 36, 48, 0.1);
        --shadow: 0 24px 80px rgba(31, 36, 48, 0.12);
        --blue: #2563eb;
        --green: #0f766e;
      }}

      * {{
        box-sizing: border-box;
      }}

      body {{
        margin: 0;
        font-family: "Space Grotesk", "Segoe UI", sans-serif;
        color: var(--ink);
        background:
          radial-gradient(circle at top left, rgba(59, 130, 246, 0.18), transparent 30%),
          radial-gradient(circle at top right, rgba(16, 185, 129, 0.18), transparent 28%),
          linear-gradient(180deg, #fffaf3 0%, var(--bg) 100%);
      }}

      body::before {{
        content: "";
        position: fixed;
        inset: 0;
        background-image:
          linear-gradient(rgba(31, 36, 48, 0.04) 1px, transparent 1px),
          linear-gradient(90deg, rgba(31, 36, 48, 0.04) 1px, transparent 1px);
        background-size: 36px 36px;
        mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.25), transparent 75%);
        pointer-events: none;
      }}

      main {{
        width: min(1180px, calc(100vw - 32px));
        margin: 0 auto;
        padding: 28px 0 56px;
        position: relative;
      }}

      .topbar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 16px;
        margin-bottom: 22px;
        color: var(--muted);
      }}

      .brand {{
        display: inline-flex;
        align-items: center;
        gap: 12px;
        font-weight: 700;
        letter-spacing: 0.02em;
      }}

      .brand-mark {{
        width: 14px;
        height: 14px;
        border-radius: 999px;
        background: linear-gradient(135deg, #0ea5e9, #10b981);
        box-shadow: 0 0 0 8px rgba(14, 165, 233, 0.12);
      }}

      .top-links {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }}

      .top-links a,
      .hero-actions a {{
        text-decoration: none;
        color: inherit;
      }}

      .chip {{
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.7);
        padding: 10px 14px;
        border-radius: 999px;
        transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
      }}

      .chip:hover {{
        transform: translateY(-1px);
        border-color: rgba(37, 99, 235, 0.28);
        background: rgba(255, 255, 255, 0.95);
      }}

      .hero {{
        display: grid;
        grid-template-columns: minmax(0, 1.5fr) minmax(320px, 0.95fr);
        gap: 22px;
        align-items: stretch;
        margin-bottom: 22px;
      }}

      .hero-copy,
      .hero-panel,
      .section {{
        position: relative;
        overflow: hidden;
        border: 1px solid var(--line);
        border-radius: 28px;
        background: var(--panel);
        box-shadow: var(--shadow);
        backdrop-filter: blur(10px);
      }}

      .hero-copy {{
        padding: 34px;
      }}

      .hero-copy::after {{
        content: "";
        position: absolute;
        right: -60px;
        top: -60px;
        width: 240px;
        height: 240px;
        border-radius: 999px;
        background: radial-gradient(circle, rgba(37, 99, 235, 0.16), transparent 70%);
      }}

      .eyebrow {{
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 8px 12px;
        border-radius: 999px;
        background: rgba(15, 118, 110, 0.1);
        color: var(--green);
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-size: 0.78rem;
      }}

      h1 {{
        margin: 18px 0 14px;
        font-size: clamp(2.4rem, 6vw, 4.8rem);
        line-height: 0.94;
        letter-spacing: -0.06em;
        max-width: 10ch;
      }}

      .lead {{
        margin: 0;
        max-width: 56ch;
        font-size: 1.06rem;
        line-height: 1.75;
        color: var(--muted);
      }}

      .hero-stats {{
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin: 26px 0;
      }}

      .stat {{
        min-width: 150px;
        padding: 14px 16px;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid var(--line);
      }}

      .stat strong {{
        display: block;
        font-size: 1.5rem;
        margin-bottom: 4px;
      }}

      .stat span {{
        color: var(--muted);
        font-size: 0.92rem;
      }}

      .hero-actions {{
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
      }}

      .button {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        padding: 14px 18px;
        border-radius: 16px;
        font-weight: 700;
      }}

      .button.primary {{
        background: linear-gradient(135deg, #2563eb, #0f766e);
        color: #fff;
        box-shadow: 0 16px 36px rgba(37, 99, 235, 0.24);
      }}

      .button.secondary {{
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.72);
      }}

      .hero-panel {{
        padding: 26px;
        background:
          linear-gradient(160deg, rgba(37, 99, 235, 0.12), transparent 38%),
          linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(255, 251, 245, 0.9));
      }}

      .panel-title {{
        margin: 0 0 8px;
        font-size: 1.3rem;
      }}

      .panel-copy {{
        margin: 0 0 18px;
        color: var(--muted);
        line-height: 1.65;
      }}

      .code-block {{
        margin: 0;
        padding: 18px;
        border-radius: 22px;
        background: #1e293b;
        color: #e2e8f0;
        font-family: "IBM Plex Mono", "Cascadia Code", monospace;
        font-size: 0.88rem;
        line-height: 1.7;
        overflow-x: auto;
      }}

      .section {{
        padding: 24px;
        margin-bottom: 22px;
      }}

      .section-head {{
        display: flex;
        justify-content: space-between;
        align-items: end;
        gap: 16px;
        margin-bottom: 18px;
      }}

      .section h2 {{
        margin: 0;
        font-size: clamp(1.5rem, 3vw, 2.2rem);
        letter-spacing: -0.04em;
      }}

      .section p {{
        margin: 6px 0 0;
        color: var(--muted);
        max-width: 58ch;
        line-height: 1.7;
      }}

      .task-grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 16px;
      }}

      .task-card {{
        position: relative;
        padding: 20px;
        border-radius: 24px;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.82);
        min-height: 230px;
        transition: transform 180ms ease, box-shadow 180ms ease;
      }}

      .task-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 18px 34px rgba(31, 36, 48, 0.12);
      }}

      .task-accent {{
        width: 54px;
        height: 7px;
        border-radius: 999px;
        margin-bottom: 16px;
      }}

      .task-header {{
        display: flex;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 8px;
      }}

      .task-level {{
        font-weight: 700;
        font-size: 1.1rem;
      }}

      .task-label {{
        color: var(--muted);
        font-size: 0.92rem;
      }}

      .ticket-id,
      .task-message,
      .task-meta,
      .task-action,
      .endpoint-copy {{
        color: var(--muted);
      }}

      .ticket-id {{
        margin: 0 0 10px;
        font-family: "IBM Plex Mono", monospace;
        font-size: 0.9rem;
      }}

      .task-message {{
        margin: 0 0 16px;
        font-size: 1rem;
        line-height: 1.7;
      }}

      .task-meta {{
        display: grid;
        gap: 6px;
        font-size: 0.92rem;
      }}

      .task-action {{
        display: inline-block;
        margin-top: 16px;
        padding: 10px 12px;
        border-radius: 14px;
        background: rgba(31, 36, 48, 0.05);
        font-family: "IBM Plex Mono", monospace;
      }}

      .endpoint-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px;
      }}

      .endpoint-card {{
        display: flex;
        gap: 14px;
        align-items: start;
        padding: 18px;
        border-radius: 20px;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.78);
      }}

      .method {{
        min-width: 58px;
        padding: 7px 10px;
        border-radius: 999px;
        text-align: center;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.04em;
      }}

      .method.get {{
        background: rgba(37, 99, 235, 0.12);
        color: #1d4ed8;
      }}

      .method.post {{
        background: rgba(16, 185, 129, 0.14);
        color: #047857;
      }}

      .endpoint-path {{
        font-family: "IBM Plex Mono", monospace;
        font-size: 1rem;
        margin-bottom: 6px;
      }}

      .footer-note {{
        text-align: center;
        color: var(--muted);
        font-size: 0.94rem;
        padding-top: 8px;
      }}

      @media (max-width: 980px) {{
        .hero,
        .task-grid,
        .endpoint-grid {{
          grid-template-columns: 1fr;
        }}

        .hero-copy,
        .hero-panel,
        .section {{
          border-radius: 24px;
        }}

        h1 {{
          max-width: none;
        }}
      }}

      @media (max-width: 640px) {{
        main {{
          width: min(100vw - 20px, 100%);
          padding-top: 16px;
        }}

        .topbar,
        .section-head,
        .task-header {{
          align-items: start;
          flex-direction: column;
        }}

        .hero-copy,
        .hero-panel,
        .section {{
          padding: 20px;
        }}
      }}
    </style>
  </head>
  <body>
    <main>
      <div class="topbar">
        <div class="brand">
          <span class="brand-mark"></span>
          <span>OpenEnv Demo Space</span>
        </div>
        <div class="top-links">
          <a class="chip" href="/docs">Swagger Docs</a>
          <a class="chip" href="/openapi.json">OpenAPI JSON</a>
          <a class="chip" href="/health">Live Health</a>
        </div>
      </div>

      <section class="hero">
        <div class="hero-copy">
          <span class="eyebrow">Live Environment</span>
          <h1>Customer Support RL Env</h1>
          <p class="lead">
            Practice support-agent behavior against escalating customer tickets with a lightweight environment API.
            Use the interactive docs for direct testing, or start with a scenario below and walk through a support turn from reset to resolution.
          </p>
          <div class="hero-stats">
            <div class="stat">
              <strong>{len(TASKS)}</strong>
              <span>built-in scenarios</span>
            </div>
            <div class="stat">
              <strong>5</strong>
              <span>max turns per episode</span>
            </div>
            <div class="stat">
              <strong>FastAPI</strong>
              <span>live Swagger + JSON schema</span>
            </div>
          </div>
          <div class="hero-actions">
            <a class="button primary" href="/docs">Launch Docs</a>
            <a class="button secondary" href="/tasks">View Tasks JSON</a>
            <a class="button secondary" href="/health">Check Health</a>
          </div>
        </div>

        <aside class="hero-panel">
          <h2 class="panel-title">Quick Start</h2>
          <p class="panel-copy">
            Reset a scenario, submit a reply, and inspect state transitions without leaving the browser.
          </p>
          <pre class="code-block">curl -X POST "/reset?task_name=medium"

curl -X POST "/step" \
  -H "content-type: application/json" \
  -d '{sample_action}'</pre>
        </aside>
      </section>

      <section class="section">
        <div class="section-head">
          <div>
            <h2>Scenario Deck</h2>
            <p>Each task increases the pressure: simple shipping delay, mixed delivery error, then an angry refund-and-escalation case.</p>
          </div>
        </div>
        <div class="task-grid">
          {"".join(task_cards)}
        </div>
      </section>

      <section class="section">
        <div class="section-head">
          <div>
            <h2>API Surface</h2>
            <p>The homepage is for orientation. The actual API remains unchanged and fully available through the same endpoints you already deployed.</p>
          </div>
        </div>
        <div class="endpoint-grid">
          {"".join(endpoint_cards)}
        </div>
      </section>

      <p class="footer-note">Built for fast experimentation, reviewer-friendly docs, and cleaner first impressions on Hugging Face Spaces.</p>
    </main>
  </body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(render_homepage())


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


def main() -> None:
    import uvicorn

    uvicorn.run(
        "server:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "7860")),
    )
