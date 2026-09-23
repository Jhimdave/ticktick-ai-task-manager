# AI TickTick Task Manager

Milestones 2–3 of the PRD: an AI-assisted daily scheduler and task breakdown
API for TickTick, built with Python + FastAPI. Groq is the primary AI provider;
Gemini is an automatic fallback when Groq hits a rate/quota limit or is
unavailable. Milestones 3–4 (reschedule API, voice-to-task) are out of scope.

## Architecture

```
  models.py                Pydantic request/response contracts
  clients/
    ticktick_client.py     TickTick OpenAPI HTTP wrapper
    ai_client.py            GroqClient, GeminiClient, AIService (failover)
  services/
    scheduler_service.py    Milestone 2 — today's schedule around appointments
  routers/
    scheduler.py             POST /schedule
    tasks.py                 POST /tasks/breakdown
  main.py                   FastAPI app
scripts/get_ticktick_token.py  one-time OAuth code → access token helper
```

Business rules (protected projects, working hours, overlap prevention, and
duration clamping) are deterministic in Python. AI estimates task duration and
enhances tasks that have no description.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

### Get a TickTick access token

TickTick's OpenAPI uses OAuth 2.0. Register an app at
https://developer.ticktick.com to get a client id/secret, then:

1. Open in a browser:
   `https://ticktick.com/oauth/authorize?client_id=<ID>&redirect_uri=<URI>&response_type=code&scope=tasks:write%20tasks:read`
2. Copy the `code` query param from the redirect.
3. Run:
   `python scripts/get_ticktick_token.py <client_id> <client_secret> <redirect_uri> <code>`
4. Put the returned `access_token` into `.env` as `TICKTICK_ACCESS_TOKEN`.

### Configure

Fill in `.env`: `GROQ_API_KEY`, `GEMINI_API_KEY`, working hours,
`PROTECTED_PROJECTS` (comma-separated, e.g. `Appointment`), and
min/max task duration.

## Run

```bash
uvicorn app.main:app --reload
```

- `POST /schedule` — build today's schedule around fixed Appointment tasks.
- `POST /tasks/breakdown` — review one task message with AI and create multiple
  TickTick tasks in `TICKTICK_DEFAULT_PROJECT_ID`.
- `GET /health` — liveness check.

### Break down a task

```json
{
  "text": "Buy groceries tomorrow at 5 PM then create the Cherajim website in September 3 and start the project logs on Tuesday"
}
```

Send this JSON to `POST /tasks/breakdown`. The AI creates titles, descriptions,
dates, and durations. Missing dates default to today; missing times are assigned
to free working-hour slots without overlap. Set `TICKTICK_DEFAULT_PROJECT_ID`
to the TickTick project where the generated tasks should be created.

## Validate

```bash
python -m compileall -q app scripts
python -c "from app.main import app; print(app.title)"
```

The validation commands do not require live credentials. Use `pytest` after
adding tests under `tests/`.

## Docker

```bash
docker build -t ticktick-ai-manager .
docker run --env-file .env -p 8000:8000 ticktick-ai-manager
```
