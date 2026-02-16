from typing import List, Optional, Union, Literal, Dict, Any
from pydantic import BaseModel, Field, field_validator

class StepBase(BaseModel):
    timeout_seconds: int = 30

class MCPToolStep(StepBase):
    type: Literal["mcp_tool"]
    tool_name: str
    input: Dict[str, Any]

class HTTPStep(StepBase):
    type: Literal["http"]
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    url: str
    headers: Dict[str, str] = {}
    json_body: Optional[Dict[str, Any]] = Field(default=None, alias="json")

class PersistSnapshotStep(StepBase):
    type: Literal["persist_snapshot"]
    include_keys: Optional[List[str]] = None

Step = Union[MCPToolStep, HTTPStep, PersistSnapshotStep]

class WorkflowDefinition(BaseModel):
    version: str
    steps: List[Step]

    @field_validator('steps')
    @classmethod
    def check_steps_not_empty(cls, v: List[Step]) -> List[Step]:
        if not v:
            raise ValueError('Workflow must have at least one step')
        return v
