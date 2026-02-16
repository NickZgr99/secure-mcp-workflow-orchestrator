from fastapi import FastAPI
from contextlib import asynccontextmanager
from apps.api.app.routes import workflows, webhooks, runs
from apps.api.app.db.session import engine
from apps.api.app.db.models import Base
from apps.api.app.cache.redis_client import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB and Redis
    async with engine.begin() as conn:
        # Create tables for dev (in prod use Alembic)
        await conn.run_sync(Base.metadata.create_all)
    await redis_client.connect()
    yield
    # Shutdown
    await redis_client.close()

app = FastAPI(title="Secure MCP Workflow Orchestrator", lifespan=lifespan)

app.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(runs.router, prefix="/runs", tags=["Runs"])

@app.get("/health")
async def health():
    return {"status": "ok"}
