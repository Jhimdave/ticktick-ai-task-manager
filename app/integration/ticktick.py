
from collections.abc import Mapping
from typing import Any

import httpx


class TickTickClient:
    """Async client for the TickTick Open API."""

    def __init__( self, token: str, base_url: str = "https://api.ticktick.com/open/v1", timeout: float = 20.0 ) -> None:
        
        if not token:
            raise ValueError("A TickTick access token is required")

        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {token}"},
            timeout=timeout,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "TickTickClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def _request( self, method: str, path: str, json: Mapping[str, Any] | None = None ) -> Any:
        response = await self._client.request(method, path, json=json)
        response.raise_for_status()
        if not response.content:
            return None
        return response.json()

    async def get_projects(self) -> Any:
        return await self._request("GET", "/project")

    async def get_project(self, project_id: str) -> Any:
        return await self._request("GET", f"/project/{project_id}")

    async def get_project_data(self, project_id: str) -> Any:
        """Return a project together with its tasks and checklist data."""
        return await self._request("GET", f"/project/{project_id}/data")

    async def get_task(self, task_id: str) -> Any:
        return await self._request("GET", f"/task/{task_id}")

    async def create_task(self, task: Mapping[str, Any]) -> Any:
        return await self._request("POST", "/task", json=task)

    async def update_task(
        self,
        task_id: str,
        task: Mapping[str, Any],
    ) -> Any:
        return await self._request("POST", f"/task/{task_id}", json=task)

    async def update_task_due_date(
        self,
        task_id: str,
        due_date: str | None,
    ) -> Any:
        return await self.update_task(task_id, {"dueDate": due_date})

    async def delete_task(self, task_id: str) -> None:
        await self._request("DELETE", f"/task/{task_id}")
    
