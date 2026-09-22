
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
        
    async def get_projects(self):
        """Get all projects."""
        response = await self._client.get("/project")
        return response.json()
        
        
    async def get_project_tasks(self, project_id: str):
        """Get tasks for a specific project."""
        response = await self._client.get(f"/project/{project_id}/data")
        return response.json()
    
    async def get_inbox_tasks(self):
        """Get tasks for the Inbox project."""
        response = await self._client.get("/project/inbox/data")
        return response.json()
    
    async def get_all_tasks(self, projects_ids: list[str]):
        """Get all tasks."""
        inbox_tasks = await self.get_inbox_tasks()
        project_tasks = [await self.get_project_tasks(project_id) for project_id in projects_ids]
        
        return inbox_tasks + [task for tasks in project_tasks for task in tasks]
