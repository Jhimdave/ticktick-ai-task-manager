import asyncio

from app.clients.ticktick_client import TickTickClient
from app.services.scheduler_service import SchedulerService


async def main():
    client = TickTickClient()

    print("\n\n================ PROJECTS ================\n\n")

    projects = await client.get_projects()

    for project in projects:
        print(f'{project["id"]} | {project["name"]}')

    print("\n\n================ SCHEDULING TODAY ================\n\n")

    scheduler = SchedulerService(client)
    result = await scheduler.schedule_today()

    print(f"Scheduled: {len(result.scheduled)}")
    print(f"Unscheduled: {len(result.unscheduled)}")
    print(f"Fixed appointments: {result.fixed_appointments}")


if __name__ == "__main__":
    asyncio.run(main())