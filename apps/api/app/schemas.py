from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from shared.shared.schemas.workflow import WorkflowDefinition

class WorkflowCreate(BaseModel):
    name: str
    definition: WorkflowDefinition

class WorkflowResponse(BaseModel):
    id: UUID
    name: str
    is_active: bool
    definition: WorkflowDefinition
    created_at: datetime
    updated_at: datetime

class WebhookEndpointCreate(BaseModel):
    path: str
    secret: str

class WebhookEndpointResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    path: str
    is_active: bool
    created_at: datetime

class RunResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    status: str
    current_step_index: int
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
