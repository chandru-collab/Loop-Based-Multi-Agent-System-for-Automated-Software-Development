import logging
from sqlalchemy.orm import Session
from app.database.models import Project

logger = logging.getLogger(__name__)

# Valid state transitions for the project workflow
ALLOWED_TRANSITIONS = {
    "CREATED": ["RUNNING", "FAILED"],
    "FAILED": ["RUNNING"],
    "RUNNING": ["WAITING_FOR_APPROVAL", "FAILED"],
    "WAITING_FOR_APPROVAL": ["PACKAGING", "RUNNING", "FAILED", "APPROVED"], # APPROVED is used before PACKAGING in some flows
    "APPROVED": ["PACKAGING", "FAILED", "COMPLETED"],
    "PACKAGING": ["COMPLETED", "FAILED"],
    "COMPLETED": [] # Terminal state
}

class InvalidTransitionError(Exception):
    pass

def can_transition(current_status: str, next_status: str) -> bool:
    """Check if a state transition is allowed."""
    if current_status not in ALLOWED_TRANSITIONS:
        return False
    return next_status in ALLOWED_TRANSITIONS[current_status]

def transition_project_status(db: Session, project: Project, next_status: str, stage: str = None):
    """
    Safely transition a project's status, ensuring validity.
    """
    if not can_transition(project.status, next_status):
        raise InvalidTransitionError(f"Cannot transition project from {project.status} to {next_status}")
    
    logger.info(f"Transitioning project {project.id} from {project.status} to {next_status}")
    project.status = next_status
    if stage:
        project.current_stage = stage
