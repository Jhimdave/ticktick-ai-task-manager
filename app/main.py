import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.routes import router
from app.integration.ticktick import TickTickClient
from app.services.task_service import TaskService

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    client = TickTickClient(os.getenv("TICKTICK_ACCESS_TOKEN", ""))
    app.state.task_service = TaskService(client)
    yield
    await client.close()


app = FastAPI(title="TickTick Task Manager", lifespan=lifespan)
app.include_router(router)