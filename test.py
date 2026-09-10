import asyncio
import json
import os
from datetime import date
from typing import Any

from dotenv import load_dotenv

from app.integration.ticktick import TickTickClient



def print_json(title: str, value: Any) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(value, indent=2, ensure_ascii=True))


def is_due_today(task: dict[str, Any], today: date) -> bool:
    due_date = task.get("dueDate")
    return isinstance(due_date, str) and due_date[:10] == today.isoformat()


async def main() -> None:
    load_dotenv()
    token = os.getenv("TICKTICK_ACCESS_TOKEN")
    if not token:
        raise SystemExit(
            "Missing TICKTICK_ACCESS_TOKEN. Add it to .env before running this script."
        )

    today = date.today()

    async with TickTickClient(token) as client:
        projects = await client.get_projects()
        print_json("Projects", projects)

        # today_tasks: list[dict[str, Any]] = []
        # for project in projects:
        #     project_id = project.get("id")
        #     if not project_id:
        #         continue

        #     project_data = await client.get_project_data(project_id)
        #     for task in project_data.get("tasks", []):
        #         if is_due_today(task, today):
        #             today_tasks.append(
        #                 {
        #                     "projectId": project_id,
        #                     "projectName": project.get("name"),
        #                     "task": task,
        #                 }
        #             )

        # print_json(f"Tasks due today ({today.isoformat()})", today_tasks)


if __name__ == "__main__":
    asyncio.run(main()) 
