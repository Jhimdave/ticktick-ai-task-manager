
# AI Change Log

This file records meaningful AI-assisted code changes. The newest entry belongs at the top.

## 2026-10-21 — Scheduler priority and prompt tightening

**Summary:** Adjusted schedule ordering to prioritize short/easy tasks before work tasks and long personal automation tasks, while preserving fixed appointment slots and reserving short break gaps without creating explicit break tasks. Reduced AI prompt length to keep task generation more stable on long user inputs.

**Files changed:**
- `app/services/scheduler_service.py` — Added scheduling category sorting for easy → work → personal automation, and inserted short automatic break gaps between batches of tasks instead of creating a visible break task.
- `app/clients/ai_client.py` — Shortened the task-breakdown prompt to keep it concise and less likely to hallucinate on longer inputs while preserving project/date constraints.
- `docs/AI_CHANGELOG.md` — Added the change log entry documenting the behavioral shift and validation notes.

**Behavioral impact:** The scheduler now prefers lower-effort tasks earlier in the day, keeps protected appointments fixed, and leaves small gaps for rest without surfacing a fake “Break” task. Longer personal automation tasks are pushed later while work/client tasks remain in the middle.

**Tests:** `python -m compileall -q app scripts`

**Risks or follow-up:** This is heuristic scheduling, so task classification is based on title/content keywords and estimated duration rather than a user-defined project taxonomy. Longer-term improvements could include explicit tags or project categories for more precise automation.
Read .github/copilot-instructions.md and inspect my existing Python/FastAPI project.

Do not create, edit, move or delete files yet.

Report:

1. The project's purpose and application entry point.
2. The current folder and file structure, excluding virtual environments and generated files.
3. How a request flows through FastAPI, business logic and external API calls.
4. Where task creation currently happens and which files are responsible.
5. Problems with the current architecture, duplicated logic or tightly coupled code.
6. How well the code follows OOP and my compact formatting preferences.
7. The dependencies, required environment variables and available test commands.
8. A proposed target structure mapping existing files to their recommended locations.

For every recommended change, briefly explain why it is needed and what behavior might be affected.

Separate confirmed findings from assumptions. Recommend the smallest practical improvements first. Wait for my approval before changing the project.