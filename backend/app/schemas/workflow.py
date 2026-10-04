from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WorkflowRunResponse(BaseModel):
    id: str
    project_id: str
    iteration: int
    stage: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AgentRunResponse(BaseModel):
    id: str
    project_id: str
    agent_name: str
    status: str
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
