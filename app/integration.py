
import httpx

class TickTickApi:
    
    BASE_URL = "https://api.ticktick.com/open/v1"
    
    def __init__(self, api_key: str, timeout: float = 20.0) -> None:
        
        if not api_key:
            raise ValueError("A TickTick API key is required")
        
        self._client = httpx.AsyncClient(
            base_url = self.BASE_URL,
            headers = {"Authorization": f"Bearer {api_key}"},
            timeout = timeout
        )
        
    @staticmethod
    def _get_tasks(data: dict, project_id: str) -> list[dict]:
        tasks = data.get("tasks", [])
        if not isinstance(tasks, list):
            raise ValueError("TickTick project data must contain a tasks list")

        return [
            {**task, "projectId": task.get("projectId", project_id)}
            for task in tasks
        ]

    async def get_projects(self):
        """Get all projects."""
        response = await self._client.get("/project")
        response.raise_for_status()
        return response.json()
        
        
    async def get_project_tasks(self, project_id: str):
        """Get tasks for a specific project."""
        response = await self._client.get(f"/project/{project_id}/data")
        response.raise_for_status()
        return self._get_tasks(response.json(), project_id)
    
    async def get_inbox_tasks(self):
        """Get tasks for the Inbox project."""
        response = await self._client.get("/project/inbox/data")
        response.raise_for_status()
        return self._get_tasks(response.json(), "inbox")
    
    async def get_all_tasks(self, projects_ids: list[str]):
        """Get all tasks."""
        inbox_tasks = await self.get_inbox_tasks()
        project_tasks = [await self.get_project_tasks(project_id) for project_id in projects_ids]
        
        return inbox_tasks + [task for tasks in project_tasks for task in tasks]
