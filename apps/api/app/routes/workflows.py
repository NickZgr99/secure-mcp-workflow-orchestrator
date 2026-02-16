from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from apps.api.app.db.session import get_db
from apps.api.app.db.models import Workflow, WebhookEndpoint
from apps.api.app.schemas import WorkflowCreate, WorkflowResponse, WebhookEndpointCreate, WebhookEndpointResponse
from shared.shared.schemas.workflow import WorkflowDefinition
import uuid

router = APIRouter()

@router.post("/", response_model=WorkflowResponse)
async def create_workflow(workflow: WorkflowCreate, db: AsyncSession = Depends(get_db)):
    db_workflow = Workflow(
        name=workflow.name,
        definition_json=workflow.definition.model_dump()
    )
    db.add(db_workflow)
    await db.commit()
    await db.refresh(db_workflow)
    return WorkflowResponse(
        id=db_workflow.id,
        name=db_workflow.name,
        is_active=db_workflow.is_active,
        definition=WorkflowDefinition(**db_workflow.definition_json),
        created_at=db_workflow.created_at,
        updated_at=db_workflow.updated_at
    )

@router.post("/{workflow_id}/webhook-endpoints", response_model=WebhookEndpointResponse)
async def create_webhook_endpoint(workflow_id: uuid.UUID, endpoint: WebhookEndpointCreate, db: AsyncSession = Depends(get_db)):
    db_workflow = await db.get(Workflow, workflow_id)
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db_endpoint = WebhookEndpoint(
        workflow_id=workflow_id,
        path=endpoint.path,
        secret=endpoint.secret
    )
    db.add(db_endpoint)
    await db.commit()
    await db.refresh(db_endpoint)
    return WebhookEndpointResponse(
        id=db_endpoint.id,
        workflow_id=db_endpoint.workflow_id,
        path=db_endpoint.path,
        is_active=db_endpoint.is_active,
        created_at=db_endpoint.created_at
    )
