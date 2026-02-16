from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from apps.api.app.db.session import get_db
from apps.api.app.db.models import WebhookEndpoint, Run
from apps.api.app.events.bus import event_bus
from apps.api.app.cache.redis_client import get_redis
import json
import uuid

router = APIRouter()

@router.post("/{path}")
async def trigger_webhook(
    path: str, 
    x_webhook_secret: str = Header(None), 
    db: AsyncSession = Depends(get_db)
):
    stmt = select(WebhookEndpoint).where(WebhookEndpoint.path == path)
    result = await db.execute(stmt)
    endpoint = result.scalar_one_or_none()
    
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    
    if not endpoint.is_active:
        raise HTTPException(status_code=400, detail="Endpoint is inactive")
        
    if endpoint.secret != x_webhook_secret:
        raise HTTPException(status_code=401, detail="Invalid secret")

    run_id = uuid.uuid4()
    
    new_run = Run(
        id=run_id,
        workflow_id=endpoint.workflow_id,
        status="QUEUED",
        triggered_by="WEBHOOK"
    )
    db.add(new_run)
    await db.commit()
    
    # Store initial state in Redis
    redis = await get_redis()
    initial_state = {
        "run_id": str(run_id),
        "workflow_id": str(endpoint.workflow_id),
        "status": "QUEUED",
        "current_step_index": 0,
        "context": {},
        "steps": []
    }
    await redis.set(f"run:{run_id}:state", json.dumps(initial_state), ex=86400) # 24h TTL
    
    # Publish event
    await event_bus.publish("RunStarted", {"run_id": str(run_id)})
    
    return {"run_id": str(run_id), "status": "QUEUED"}
