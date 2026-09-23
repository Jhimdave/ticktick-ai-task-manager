from fastapi import FastAPI

from app.routers.scheduler import router as scheduler_router
from app.routers.tasks import router as tasks_router

app = FastAPI(title="TickTick Task Manager")
app.include_router(scheduler_router)
app.include_router(tasks_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
