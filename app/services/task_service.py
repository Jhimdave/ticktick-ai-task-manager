from collections.abc import Mapping
from typing import Any

from app.integration.ticktick import TickTickClient


class TaskService:
	def __init__(self, client: TickTickClient) -> None:
		self.client = client

	async def get_projects(self) -> Any:
		return await self.client.get_projects()

	async def get_project(self, project_id: str) -> Any:
		return await self.client.get_project(project_id)

	async def get_project_data(self, project_id: str) -> Any:
		return await self.client.get_project_data(project_id)

	async def get_task(self, task_id: str) -> Any:
		return await self.client.get_task(task_id)

	async def create_task(self, task: Mapping[str, Any]) -> Any:
		return await self.client.create_task(task)

	async def update_task(
		self,
		task_id: str,
		task: Mapping[str, Any],
	) -> Any:
		return await self.client.update_task(task_id, task)

	async def update_task_due_date(
		self,
		task_id: str,
		due_date: str | None,
	) -> Any:
		return await self.client.update_task_due_date(task_id, due_date)

	async def delete_task(self, task_id: str) -> None:
		await self.client.delete_task(task_id)
