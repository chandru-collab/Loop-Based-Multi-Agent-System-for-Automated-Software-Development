from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Project

router = APIRouter()

@router.get("/{project_id}/agents")
def get_agents_status(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    stages = [
        "requirement", "planner", "coder", "tester", 
        "reviewer", "debugger", "evaluator", "documentation"
    ]
    
    agent_names = {
        "requirement": "Requirement Agent",
        "planner": "Planner Agent",
        "coder": "Code Generation Agent",
        "tester": "Testing Agent",
        "reviewer": "Reviewer Agent",
        "debugger": "Debugger Agent",
        "evaluator": "Evaluation Agent",
        "documentation": "Documentation Agent"
    }

    result = []
    current_idx = stages.index(project.current_stage) if project.current_stage in stages else -1
    
    for i, stage in enumerate(stages):
        status = "pending"
        
        if project.status == "FAILED" and i == current_idx:
            status = "failed"
        elif i < current_idx or (project.status == "PLANNING_COMPLETED" and stage in ["requirement", "planner"]):
            status = "completed"
        elif i == current_idx and project.status not in ["FAILED", "PLANNING_COMPLETED"]:
            status = "running"
        elif stage == "coder" and project.status == "PLANNING_COMPLETED":
            status = "locked"
            
        result.append({
            "name": agent_names[stage],
            "status": status
        })

    return result
