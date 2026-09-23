from datetime import datetime, timezone

import httpx

from app.config import settings


class TickTickClient:
    """Thin wrapper over the TickTick OpenAPI."""

    def __init__(self, access_token: str = None, base_url: str = None):
        self.access_token = access_token or settings.ticktick_access_token
        self.base_url = base_url or settings.ticktick_base_url

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _normalize_datetime(value):
        if value is None:
            return None

        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)

            return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+0000")

        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))

                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)

                return parsed.astimezone(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S+0000"
                )

            except ValueError:
                return value

        return value

    def _normalize_payload(
        self, task: dict | str, project_id: str | None = None, **fields
    ) -> tuple[str, dict]:
        if isinstance(task, str):
            task_id = task
            payload = {}
        else:
            payload = dict(task)

            if "id" not in payload:
                raise ValueError("task payload must include an id")

            task_id = payload.pop("id")

        if project_id is not None:
            payload["projectId"] = project_id

        payload.update(fields)

        for key in ("startDate", "dueDate"):
            if key in payload:
                payload[key] = self._normalize_datetime(payload[key])

        if any(
            key in payload for key in ("startDate", "dueDate", "timeZone", "isAllDay")
        ):
            payload["timeZone"] = payload.get("timeZone") or settings.default_timezone
            payload["isAllDay"] = payload.get("isAllDay", False)

        payload = {k: v for k, v in payload.items() if v is not None}

        return task_id, payload

    async def get_projects(self) -> list[dict]:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.base_url}/project", headers=self._headers(), timeout=15
            )
            r.raise_for_status()
            return r.json()

    async def get_project_data(self, project_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.base_url}/project/{project_id}/data",
                headers=self._headers(),
                timeout=15,
            )
            r.raise_for_status()
            return r.json()

    async def get_project_tasks(self, project_id: str) -> list[dict]:
        data = await self.get_project_data(project_id)

        return [
            {**task, "projectId": task.get("projectId", project_id)}
            for task in data.get("tasks", [])
        ]

    async def get_inbox_tasks(self) -> list[dict]:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.base_url}/project/inbox/data",
                headers=self._headers(),
                timeout=15,
            )
            r.raise_for_status()

            return [
                {**task, "projectId": task.get("projectId", "inbox")}
                for task in r.json().get("tasks", [])
            ]

    async def get_all_tasks(self, project_ids: list[str] | None = None) -> list[dict]:
        if project_ids is None:
            project_ids = [p["id"] for p in await self.get_projects()]

        inbox_tasks = await self.get_inbox_tasks()
        project_tasks = [
            await self.get_project_tasks(project_id) for project_id in project_ids
        ]

        return inbox_tasks + [task for tasks in project_tasks for task in tasks]

    async def update_task(
        self, task: dict | str, project_id: str | None = None, **fields
    ) -> dict:
        task_id, payload = self._normalize_payload(task, project_id, **fields)

        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.base_url}/task/{task_id}",
                headers=self._headers(),
                json=payload,
                timeout=15,
            )
            r.raise_for_status()

            if not r.content or not r.content.strip():
                return {"id": task_id, **payload}

            try:
                return r.json()
            except ValueError:
                return {"id": task_id, **payload}

    async def create_task(self, task: dict) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.base_url}/task", headers=self._headers(), json=task, timeout=15
            )
            r.raise_for_status()

            if not r.content or not r.content.strip():
                return task

            try:
                return r.json()
            except ValueError:
                return task
