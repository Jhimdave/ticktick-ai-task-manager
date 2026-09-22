
import os
import json
from dotenv import load_dotenv
import asyncio
from integration import TickTickApi


async def main():
    load_dotenv()
    api_key = os.getenv("TICKTICK_API_KEY")
    
    if not api_key:
        raise SystemExit(
            "Missing TICKTICK_API_KEY. Add it to .env before running this script."
        )
        
    ticktick_api = TickTickApi(api_key)
    
    projects = await ticktick_api.get_projects()
    projects_json = json.dumps(projects, ensure_ascii=True, indent=2)

    print("Projects:", projects_json)

    tasks = await ticktick_api.get_all_tasks([project["id"] for project in projects])
    tasks_json = json.dumps(tasks, ensure_ascii=True, indent=2)    
    
    print("All Tasks:", tasks_json)

if __name__ == "__main__":
    asyncio.run(main())
