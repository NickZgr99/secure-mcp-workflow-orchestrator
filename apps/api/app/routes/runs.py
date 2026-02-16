from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from apps.api.app.db.session import get_db
from apps.api.app.db.models import Run
from apps.api.app.schemas import RunResponse
from apps.api.app.cache.redis_client import get_redis
import uuid
import json

router = APIRouter()

@router.get("/{run_id}", response_model=RunResponse)
async def get_run(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    redis = await get_redis()
    state_json = await redis.get(f"run:{run_id}:state")
    
    if state_json:
        state = json.loads(state_json)
        return RunResponse(
            id=state["run_id"],
            workflow_id=state["workflow_id"],
            status=state["status"],
            current_step_index=state["current_step_index"],
            created_at=state.get("created_at", None) or None # Adjust as needed
            # Note: The Redis state might not have all fields, ideally we fetch from DB and overlay Redis state
        )

    run = await db.get(Run, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    return RunResponse(
        id=run.id,
        workflow_id=run.workflow_id,
        status=run.status,
        current_step_index=run.current_step_index,
        started_at=run.started_at,
        finished_at=run.finished_at,
        error_message=run.error_message,
        created_at=run.created_at
    )
