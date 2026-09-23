import json

from google import genai
from google.genai import types as genai_types
from groq import Groq

from app.config import settings

RETRYABLE_MARKERS = (
    "rate limit",
    "429",
    "quota",
    "unavailable",
    "timeout",
    "503",
    "502",
    "model not found",
    "does not exist",
    "access to it",
    "not available",
)


class AIProviderError(Exception):
    """Raised on provider failure. retryable=True means the caller should fail over."""

    def __init__(self, message: str, retryable: bool = True):
        super().__init__(message)
        self.retryable = retryable


class GroqClient:
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model

    def complete_json(self, system: str, user: str) -> dict:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            retryable = any(k in str(e).lower() for k in RETRYABLE_MARKERS)
            raise AIProviderError(f"Groq error: {e}", retryable=retryable) from e


class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model

    def complete_json(self, system: str, user: str) -> dict:
        try:
            resp = self.client.models.generate_content(
                model=self.model,
                contents=f"{system}\n\n{user}",
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json", temperature=0
                ),
            )
            return json.loads(resp.text)
        except Exception as e:
            raise AIProviderError(f"Gemini error: {e}", retryable=False) from e


class AIService:
    """Single interface used by the rest of the app. Tries Groq first, fails
    over to Gemini on retryable (rate-limit/unavailable) errors only."""

    def __init__(self, groq: "GroqClient" = None, gemini: "GeminiClient" = None):
        self.groq = groq or GroqClient()
        self.gemini = gemini or GeminiClient()

    def complete_json(self, system: str, user: str) -> dict:
        try:
            return self.groq.complete_json(system, user)
        except AIProviderError as e:
            if not e.retryable:
                raise
            return self.gemini.complete_json(system, user)

    def estimate_duration(
        self,
        task_title: str,
        task_content: str,
        priority: int,
        min_minutes: int,
        max_minutes: int,
        enhance_content: bool = False,
    ) -> dict:
        enhancement = (
            "Also improve the title and write a concise, actionable description. "
            "Return them as enhanced_title and description."
            if enhance_content
            else ""
        )
        output = (
            '{"difficulty": int, "duration_minutes": int, "enhanced_title": str, "description": str}'
            if enhance_content
            else '{"difficulty": int, "duration_minutes": int}'
        )
        system = (
            "You are a task-planning assistant. Estimate difficulty (1-5) and duration in minutes "
            f"(between {min_minutes} and {max_minutes}) needed to complete the task. {enhancement} "
            f"Respond ONLY with JSON: {output}"
        )
        user = json.dumps(
            {
                "task_title": task_title,
                "task_description": task_content,
                "priority": priority,
            }
        )
        return self.complete_json(system, user)

    def break_down_task(
        self, text: str, current_date: str, timezone: str
    ) -> list[dict]:
        system = (
            "You are a task-planning and scheduling assistant. Break the user's text into the "
            "smallest useful set of independent TickTick tasks. Create a clear action-oriented "
            "title and concise description for every task. Extract dates and times when stated. "
            "Use the supplied current date to resolve relative dates such as tomorrow, Tuesday, "
            "or September 3. If no date is stated, set date to the current date. If no time is "
            "stated, set preferred_time to null so the application can assign an available slot. "
            'Return ONLY JSON with this shape: {"tasks": [{"title": str, '
            '"description": str, "date": "YYYY-MM-DD", "preferred_time": '
            '"HH:MM" or null, "duration_minutes": int, "priority": int}]}'
        )
        result = self.complete_json(
            system,
            json.dumps(
                {
                    "text": text,
                    "current_date": current_date,
                    "timezone": timezone,
                }
            ),
        )
        tasks = result.get("tasks")

        if not isinstance(tasks, list):
            raise ValueError("AI response must contain a tasks list")

        return [task for task in tasks if isinstance(task, dict)]
