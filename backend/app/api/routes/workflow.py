from fastapi import APIRouter

router = APIRouter()

@router.get("/{project_id}/workflow")
def get_workflow_status(project_id: str):
    # Mock data for Phase 1
    return {
        "status": "running",
        "current_stage": "Code Generation",
        "iteration": 1
    }

@router.get("/{project_id}/evaluation")
def get_evaluation(project_id: str):
    # Mock data for Phase 1
    return {
        "score": 85,
        "test_pass_rate": 90.5
    }
