from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import UniqueConstraint
from pydantic import BaseModel, Field
from typing import Optional, List
from app.database.database import get_db, SessionLocal
from app.database.models import (
    Project, RequirementAnalysis, DevelopmentPlan, ProjectFile,
    TestResult, ReviewResult, DebugResult, IterationHistory,
    EvaluationResult, DocumentationResult, ProjectVersion,
    RevisionRequest, PackageMetadata, WorkflowEvent, AgentRun,
    MAX_USER_REVISIONS, MAX_DEVELOPMENT_ITERATIONS
)
from app.schemas.project import ProjectCreate, ProjectResponse
from app.workflow.graph import experiment_a_graph, experiment_b_graph
from app.workflow.state_machine import transition_project_status, InvalidTransitionError
from app.services.package_service import PackageService
from app.services.live_runner import live_runner
import uuid
import os
import subprocess
import shutil
import logging
import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# ---- Request/Response Schemas ----

class ReviseRequest(BaseModel):
    feedback: str = Field(..., min_length=1, description="User feedback for the revision")

class ApproveResponse(BaseModel):
    message: str
    project_id: str
    version: int
    status: str
    package_filename: Optional[str] = None
    package_size: Optional[int] = None
    checksum_sha256: Optional[str] = None

# ---- Helpers ----

def _set_project_status(db: Session, project: Project, status: str, stage: str = None):
    try:
        transition_project_status(db, project, status, stage)
        db.commit()
    except InvalidTransitionError as e:
        logger.error(f"State transition error: {e}")
        # Force a FAILED state if we attempt an invalid transition inside workflow sync
        project.status = "FAILED"
        db.commit()

def _log_event(db: Session, project_id: str, version: int, event_type: str, details: dict):
    event = WorkflowEvent(
        id=str(uuid.uuid4()),
        project_id=project_id,
        version=version,
        event_type=event_type,
        details=details
    )
    db.add(event)

def _build_initial_state(project: Project, version: int, revision_feedback: str = None) -> dict:
    requirement = project.description
    if revision_feedback:
        requirement = f"{project.description}\n\n[REVISION FEEDBACK - Version {version}]: {revision_feedback}"
    return {
        "project_id": project.id,
        "user_requirement": requirement,
        "revision_feedback": revision_feedback,
        "active_version": version,
        "revision_count": project.revision_count,
        "requirements": None,
        "plan": None,
        "file_manifest": [],
        "generated_files": [],
        "generation_version": version,
        "workspace_path": None,
        "generation_status": "pending",
        "generation_errors": [],
        "test_results": None,
        "review_results": None,
        "debug_results": None,
        "evaluation_results": None,
        "documentation_results": None,
        "iteration": 1,
        "max_iterations": project.max_iterations or MAX_DEVELOPMENT_ITERATIONS,
        "current_stage": "requirement",
        "status": "RUNNING",
        "approval_status": "PENDING",
        "waiting_for_approval": False,
        "package_path": None,
        "package_checksum": None,
        "package_size": None,
        "iteration_history": [],
        "errors": [],
        "history": []
    }

def _infer_file_language(path: str) -> str:
    lower = path.lower()
    if lower.endswith(".py"):
        return "python"
    if lower.endswith((".ts", ".tsx")):
        return "typescript"
    if lower.endswith((".js", ".jsx")):
        return "javascript"
    if lower.endswith(".md"):
        return "markdown"
    if lower.endswith(".json"):
        return "json"
    if lower.endswith(".yml") or lower.endswith(".yaml"):
        return "yaml"
    if lower.endswith(".html"):
        return "html"
    if lower.endswith(".css"):
        return "css"
    if lower.endswith(".env") or lower.endswith(".example"):
        return "env"
    return "text"


def _persist_result(project: Project, result: dict, version: int, db: Session):
    """Persist all workflow output to DB."""
    if not result or not isinstance(result, dict):
        logger.warning(f"No valid dict result returned from workflow graph for project {project.id}")
        _set_project_status(db, project, "FAILED")
        db.commit()
        return

    if result.get("requirements") and isinstance(result["requirements"], dict):
        db.query(RequirementAnalysis).filter(
            RequirementAnalysis.project_id == project.id,
            RequirementAnalysis.version == version
        ).delete()
        db.add(RequirementAnalysis(
            id=str(uuid.uuid4()),
            project_id=project.id,
            version=version,
            **result["requirements"]
        ))

    if result.get("plan") and isinstance(result["plan"], dict):
        db.query(DevelopmentPlan).filter(
            DevelopmentPlan.project_id == project.id,
            DevelopmentPlan.version == version
        ).delete()
        db.add(DevelopmentPlan(
            id=str(uuid.uuid4()),
            project_id=project.id,
            version=version,
            **result["plan"]
        ))

    documentation_result = result.get("documentation_results")
    if isinstance(documentation_result, dict):
        db.query(DocumentationResult).filter(
            DocumentationResult.project_id == project.id,
            DocumentationResult.version == version
        ).delete()
        db.add(DocumentationResult(
            id=str(uuid.uuid4()),
            project_id=project.id,
            version=version,
            status=documentation_result.get("status", "COMPLETED"),
            files_created=documentation_result.get("files_created", []),
            files_updated=documentation_result.get("files_updated", []),
            documentation_summary=documentation_result.get("documentation_summary"),
        ))

    tracked_files = []
    if result.get("generated_files") and isinstance(result["generated_files"], list):
        for item in result["generated_files"]:
            if isinstance(item, str):
                tracked_files.append({
                    "path": item,
                    "language": _infer_file_language(item),
                    "purpose": "documentation" if "docs/" in item or item == "README.md" else "source"
                })
            elif isinstance(item, dict):
                tracked_files.append(item)

    if isinstance(documentation_result, dict):
        created = documentation_result.get("files_created", []) or []
        updated = documentation_result.get("files_updated", []) or []
        for path in created + updated:
            if isinstance(path, str):
                tracked_files.append({
                    "path": path,
                    "language": _infer_file_language(path),
                    "purpose": "documentation"
                })
            elif isinstance(path, dict):
                tracked_files.append(path)

    # Also scan disk workspace if available to guarantee no missing files
    ws_path = result.get("workspace_path") or _find_workspace_path(project.id, version)
    if ws_path and os.path.exists(ws_path):
        for root, dirs, files_in_dir in os.walk(ws_path):
            dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "venv", ".venv", ".pytest_cache", "node_modules", "dist"]]
            for file_name in files_in_dir:
                full_path = os.path.join(root, file_name)
                rel_path = os.path.relpath(full_path, ws_path).replace("\\", "/")
                if not any(f.get("path") == rel_path for f in tracked_files if isinstance(f, dict)):
                    tracked_files.append({
                        "path": rel_path,
                        "language": _infer_file_language(rel_path),
                        "purpose": "documentation" if rel_path.startswith("docs/") or rel_path == "README.md" else "source"
                    })

    if tracked_files:
        db.query(ProjectFile).filter(
            ProjectFile.project_id == project.id,
            ProjectFile.version == version
        ).delete()
        for f in tracked_files:
            if not isinstance(f, dict):
                continue
            path = f.get("path")
            if not path:
                continue
            normalized_path = str(path).replace("\\", "/").lstrip("./")
            db.add(ProjectFile(
                id=str(uuid.uuid4()),
                project_id=project.id,
                version=version,
                path=normalized_path,
                language=f.get("language") or _infer_file_language(normalized_path),
                purpose=f.get("purpose") or ("documentation" if "docs/" in normalized_path or normalized_path == "README.md" else "source"),
                file_type="source"
            ))

    # Determine final status
    final_status = result.get("status", "FAILED")
    if result.get("waiting_for_approval") or result.get("current_stage") == "WAITING_FOR_APPROVAL":
        final_status = "WAITING_FOR_APPROVAL"

    _set_project_status(db, project, final_status, result.get("current_stage"))
    db.commit()

def run_workflow_background(project_id: str, version: int, initial_state: dict, config: dict, experiment_type: str, revision_id: str = None):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return

        graph = experiment_a_graph if experiment_type == "A" else experiment_b_graph
        result = graph.invoke(initial_state, config)
        
        _persist_result(project, result, version, db)

        pv = db.query(ProjectVersion).filter(
            ProjectVersion.project_id == project_id,
            ProjectVersion.version == version
        ).first()
        if pv:
            pv.workspace_path = result.get("workspace_path")
            pv.evaluation_status = result.get("evaluation_results", {}).get("status") if result.get("evaluation_results") else None
            if project.status == "WAITING_FOR_APPROVAL":
                pv.status = "ACTIVE"
            db.commit()

        if revision_id:
            revision = db.query(RevisionRequest).filter(RevisionRequest.id == revision_id).first()
            if revision:
                revision.status = "COMPLETED"
                db.commit()

    except Exception as e:
        logger.exception("Graph execution failed in background")
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.status = "FAILED"
            db.commit()
    finally:
        db.close()

# ---- CRUD ----

@router.post("/", response_model=ProjectResponse)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(
        id=str(uuid.uuid4()),
        name=project_in.name,
        description=project_in.description,
        max_iterations=project_in.max_iterations,
        status="CREATED"
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/{project_id}/status")
def get_project_status(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    pkg = db.query(PackageMetadata).filter(PackageMetadata.project_id == project_id, PackageMetadata.version == project.current_version).first()
    return {
        "project_id": project_id,
        "name": project.name,
        "status": project.status,
        "current_stage": project.current_stage,
        "current_version": project.current_version,
        "revision_count": project.revision_count,
        "max_revisions": project.max_revisions,
        "approval_status": project.approval_status,
        "has_package": pkg is not None,
        "package_filename": pkg.package_filename if pkg else None
    }

# ---- Workflow ----

@router.post("/{project_id}/start")
def start_project(project_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    version = 1
    project.current_version = version
    try:
        transition_project_status(db, project, "RUNNING")
    except InvalidTransitionError as e:
        raise HTTPException(status_code=409, detail=str(e))
    db.commit()

    # Create a ProjectVersion record
    pv = db.query(ProjectVersion).filter(
        ProjectVersion.project_id == project_id,
        ProjectVersion.version == version
    ).first()
    if not pv:
        pv = ProjectVersion(
            id=str(uuid.uuid4()),
            project_id=project_id,
            version=version,
            parent_version=None,
            status="ACTIVE"
        )
        db.add(pv)
        _log_event(db, project_id, version, "VERSION_CREATED", {"version": version})
        db.commit()

    initial_state = _build_initial_state(project, version)
    config = {"configurable": {"thread_id": f"{project_id}_v{version}"}}

    background_tasks.add_task(
        run_workflow_background,
        project_id,
        version,
        initial_state,
        config,
        project.experiment_type
    )

    return {"message": "Workflow started in background", "project_id": project_id, "status": project.status}

@router.post("/{project_id}/retry")
def retry_project(project_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    version = project.current_version or 1
    project.status = "RUNNING"
    project.current_stage = "requirement"
    db.commit()

    initial_state = _build_initial_state(project, version)
    # A retry must not resume the failed checkpoint for this version.
    config = {"configurable": {"thread_id": f"{project_id}_v{version}_retry_{uuid.uuid4()}"}}

    background_tasks.add_task(
        run_workflow_background,
        project_id,
        version,
        initial_state,
        config,
        project.experiment_type
    )

    return {"message": "Project retried in background", "project_id": project_id, "status": project.status}

# ---- Approval & Revision ----

@router.post("/{project_id}/approve")
def approve_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    version = project.current_version

    # Idempotency - if already completed, return existing package
    if project.status == "COMPLETED":
        pkg = db.query(PackageMetadata).filter(
            PackageMetadata.project_id == project_id,
            PackageMetadata.version == version
        ).first()
        return ApproveResponse(
            message="Project already approved and packaged",
            project_id=project_id,
            version=version,
            status="COMPLETED",
            package_filename=pkg.package_filename if pkg else None,
            package_size=pkg.package_size if pkg else None,
            checksum_sha256=pkg.checksum_sha256 if pkg else None
        )

    # State validation
    if project.status != "WAITING_FOR_APPROVAL":
        raise HTTPException(
            status_code=409,
            detail=f"Cannot approve project in status '{project.status}'. Must be WAITING_FOR_APPROVAL."
        )
    if project.approval_status == "APPROVED":
        raise HTTPException(status_code=409, detail="Project has already been approved.")

    # Set PACKAGING
    try:
        with db.begin_nested(): # Ensure this part is atomic within the request
            transition_project_status(db, project, "PACKAGING")
            project.approval_status = "APPROVED"
            _log_event(db, project_id, version, "APPROVAL_REQUEST", {"version": version})
    except InvalidTransitionError as e:
        raise HTTPException(status_code=409, detail=str(e))
    db.commit()

    # Update ProjectVersion
    pv = db.query(ProjectVersion).filter(
        ProjectVersion.project_id == project_id,
        ProjectVersion.version == version
    ).first()
    if pv:
        pv.approval_status = "APPROVED"
        pv.status = "COMPLETED"
        db.commit()

    # Create package
    try:
        svc = PackageService()
        pkg_data = svc.create_package(project_id, version)

        pkg = PackageMetadata(
            id=str(uuid.uuid4()),
            project_id=project_id,
            version=version,
            package_path=pkg_data["package_path"],
            package_filename=pkg_data["package_filename"],
            package_size=pkg_data["package_size"],
            checksum_sha256=pkg_data["checksum_sha256"]
        )
        db.add(pkg)
        _log_event(db, project_id, version, "PACKAGING_COMPLETED", {
            "filename": pkg_data["package_filename"],
            "size": pkg_data["package_size"]
        })

        try:
            transition_project_status(db, project, "COMPLETED")
        except InvalidTransitionError:
            pass # Ignore if it somehow failed, though it shouldn't from PACKAGING
        _log_event(db, project_id, version, "PROJECT_COMPLETED", {"version": version})
        db.commit()

    except ValueError as e:
        project.status = "FAILED"
        _log_event(db, project_id, version, "WORKFLOW_FAILED", {"reason": str(e)})
        db.commit()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        project.status = "FAILED"
        _log_event(db, project_id, version, "WORKFLOW_FAILED", {"reason": str(e)})
        db.commit()
        raise HTTPException(status_code=500, detail=f"Packaging failed: {e}")

    return ApproveResponse(
        message="Project approved and packaged successfully",
        project_id=project_id,
        version=version,
        status="COMPLETED",
        package_filename=pkg_data["package_filename"],
        package_size=pkg_data["package_size"],
        checksum_sha256=pkg_data["checksum_sha256"]
    )

@router.post("/{project_id}/revise")
def revise_project(project_in: ReviseRequest, project_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.status != "WAITING_FOR_APPROVAL":
        raise HTTPException(
            status_code=409,
            detail=f"Cannot request revision in status '{project.status}'. Must be WAITING_FOR_APPROVAL."
        )

    if project.revision_count >= MAX_USER_REVISIONS:
        raise HTTPException(
            status_code=409,
            detail=f"Revision limit reached ({MAX_USER_REVISIONS}). No further revisions are allowed."
        )

    if not project_in.feedback or not project_in.feedback.strip():
        raise HTTPException(status_code=400, detail="Revision feedback cannot be empty.")

    source_version = project.current_version
    target_version = source_version + 1

    # Idempotency: check if this revision already exists
    existing_rev = db.query(RevisionRequest).filter(
        RevisionRequest.project_id == project_id,
        RevisionRequest.source_version == source_version
    ).first()
    if existing_rev:
        raise HTTPException(
            status_code=409,
            detail=f"A revision from v{source_version} already exists (target: v{target_version})."
        )

    # Mark current version as superseded
    pv = db.query(ProjectVersion).filter(
        ProjectVersion.project_id == project_id,
        ProjectVersion.version == source_version
    ).first()
    if pv:
        pv.status = "SUPERSEDED"
        pv.approval_status = "REVISION_REQUESTED"

    # Create revision request record
    revision = RevisionRequest(
        id=str(uuid.uuid4()),
        project_id=project_id,
        source_version=source_version,
        target_version=target_version,
        feedback=project_in.feedback,
        status="SUBMITTED"
    )
    db.add(revision)

    # Update project
    project.revision_count += 1
    project.current_version = target_version
    project.approval_status = "PENDING"
    try:
        transition_project_status(db, project, "RUNNING")
    except InvalidTransitionError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(e))

    _log_event(db, project_id, source_version, "REVISION_REQUEST", {
        "source_version": source_version,
        "target_version": target_version,
        "feedback_length": len(project_in.feedback)
    })
    db.commit()

    # Create new ProjectVersion record
    new_pv = ProjectVersion(
        id=str(uuid.uuid4()),
        project_id=project_id,
        version=target_version,
        parent_version=source_version,
        status="ACTIVE",
        revision_feedback=project_in.feedback
    )
    db.add(new_pv)
    _log_event(db, project_id, target_version, "VERSION_CREATED", {"version": target_version, "parent": source_version})
    db.commit()

    # Run new workflow for the new version
    initial_state = _build_initial_state(project, target_version, project_in.feedback)
    config = {"configurable": {"thread_id": f"{project_id}_v{target_version}"}}

    background_tasks.add_task(
        run_workflow_background,
        project_id,
        target_version,
        initial_state,
        config,
        project.experiment_type,
        revision.id
    )

    return {
        "message": f"Revision submitted. New version v{target_version} is running in background.",
        "project_id": project_id,
        "source_version": source_version,
        "target_version": target_version,
        "status": project.status
    }

# ---- Data Retrieval ----

@router.get("/{project_id}/requirements")
def get_requirements(project_id: str, db: Session = Depends(get_db)):
    req = db.query(RequirementAnalysis).filter(
        RequirementAnalysis.project_id == project_id
    ).order_by(RequirementAnalysis.created_at.desc()).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirements not found")
    return req

@router.get("/{project_id}/plan")
def get_plan(project_id: str, db: Session = Depends(get_db)):
    plan = db.query(DevelopmentPlan).filter(
        DevelopmentPlan.project_id == project_id
    ).order_by(DevelopmentPlan.created_at.desc()).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

def _find_workspace_path(project_id: str, version: int) -> Optional[str]:
    candidates = [
        # Root generated_projects / {project_id} / versions / v{version}
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "generated_projects", project_id, "versions", f"v{version}")),
        # Backend generated_projects / {project_id} / versions / v{version}
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "generated_projects", project_id, "versions", f"v{version}")),
        # Root generated_projects / {project_id} / v{version}
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "generated_projects", project_id, f"v{version}")),
        # Root generated_projects / {project_id}
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "generated_projects", project_id)),
        # Backend generated_projects / {project_id}
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "generated_projects", project_id)),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    return None

@router.get("/{project_id}/files")
def get_files(project_id: str, version: int = None, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    active_version = version or project.current_version
    query = db.query(ProjectFile).filter(ProjectFile.project_id == project_id)
    if version:
        query = query.filter(ProjectFile.version == version)
    else:
        query = query.filter(ProjectFile.version == project.current_version)
    files = query.all()
    files_by_path = {f.path: {"path": f.path, "language": f.language, "purpose": f.purpose} for f in files}

    workspace_path = _find_workspace_path(project_id, active_version)
    if not workspace_path or not os.path.exists(workspace_path) or len(os.listdir(workspace_path)) == 0:
        workspace_path = _preview_workspace(project_id, active_version, db)

    if workspace_path and os.path.exists(workspace_path):
        for root, dirs, files_in_dir in os.walk(workspace_path):
            dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "venv", ".venv", ".pytest_cache", "node_modules", "dist"]]
            for file_name in files_in_dir:
                full_path = os.path.join(root, file_name)
                rel_path = os.path.relpath(full_path, workspace_path).replace("\\", "/")
                if rel_path not in files_by_path:
                    files_by_path[rel_path] = {
                        "path": rel_path,
                        "language": _infer_file_language(rel_path),
                        "purpose": "documentation" if rel_path.startswith("docs/") or rel_path == "README.md" else "source",
                    }

    return {
        "project_id": project_id,
        "version": active_version,
        "files": list(files_by_path.values())
    }

@router.get("/{project_id}/files/{file_path:path}")
def get_file_content(project_id: str, file_path: str, version: int = None, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    v = version or project.current_version
    base_dir = _find_workspace_path(project_id, v)
    if not base_dir or not os.path.exists(base_dir):
        base_dir = _preview_workspace(project_id, v, db)
    
    from app.core.security import safe_join
    try:
        full_path = safe_join(base_dir, file_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File does not exist on disk")

    return FileResponse(full_path)

def _preview_workspace(project_id: str, version: int, db: Session) -> str:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    workspace = _find_workspace_path(project_id, version)
    if not workspace:
        # Fallback to creating a live preview directly from RequirementAnalysis in DB
        workspace = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "..", "generated_projects",
            project_id, "versions", f"v{version}"
        ))
        os.makedirs(workspace, exist_ok=True)
        req = db.query(RequirementAnalysis).filter(
            RequirementAnalysis.project_id == project_id
        ).order_by(RequirementAnalysis.created_at.desc()).first()
        req_dict = {
            "project_summary": project.name or project.description,
            "summary": project.description,
            "functional_requirements": req.functional_requirements if req and req.functional_requirements else [project.description],
            "data_entities": req.data_entities if req and req.data_entities else [],
            "ui_requirements": req.ui_requirements if req and req.ui_requirements else []
        }
        from app.agents.coder_agent import CodeGenerationAgent
        coder = CodeGenerationAgent()
        coder.ensure_preview_entrypoint(workspace, req_dict, [])
    return workspace

def _build_preview(workspace: str) -> str:
    dist_dir = os.path.join(workspace, "dist")
    dist_index = os.path.join(dist_dir, "index.html")
    root_index = os.path.join(workspace, "index.html")
    package_path = os.path.join(workspace, "package.json")
    
    if os.path.exists(dist_index):
        return dist_dir
    if not os.path.exists(package_path):
        return workspace

    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm:
        return workspace

    try:
        subprocess.run(
            [npm, "install", "--no-audit", "--no-fund"],
            cwd=workspace, check=True, capture_output=True, text=True, timeout=30
        )
        try:
            subprocess.run(
                [npm, "run", "build"],
                cwd=workspace, check=True, capture_output=True, text=True, timeout=30
            )
        except subprocess.CalledProcessError:
            npx = shutil.which("npx.cmd") or shutil.which("npx")
            if npx:
                subprocess.run(
                    [npx, "vite", "build"],
                    cwd=workspace, check=True, capture_output=True, text=True, timeout=30
                )
    except Exception as exc:
        logger.warning(f"Preview build failed or timed out: {exc}")
        return workspace

    if os.path.exists(dist_index):
        return dist_dir
    return workspace

@router.get("/{project_id}/preview")
def get_project_preview(project_id: str, version: int = None, db: Session = Depends(get_db)):
    import re
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    v = version or project.current_version
    workspace = _preview_workspace(project_id, v, db)
    preview_root = _build_preview(workspace)
    index_path = os.path.join(preview_root, "index.html")
    
    if not os.path.exists(index_path):
        root_index = os.path.join(workspace, "index.html")
        if os.path.exists(root_index):
            index_path = root_index
        else:
            req = db.query(RequirementAnalysis).filter(
                RequirementAnalysis.project_id == project_id
            ).order_by(RequirementAnalysis.created_at.desc()).first()
            req_dict = {
                "project_summary": project.name or project.description,
                "summary": project.description,
                "functional_requirements": req.functional_requirements if req and req.functional_requirements else [project.description],
                "data_entities": req.data_entities if req and req.data_entities else [],
                "ui_requirements": req.ui_requirements if req and req.ui_requirements else []
            }
            from app.agents.coder_agent import CodeGenerationAgent
            coder = CodeGenerationAgent()
            coder.ensure_preview_entrypoint(workspace, req_dict, [])
            index_path = os.path.join(workspace, "index.html")
        
    with open(index_path, "r", encoding="utf-8") as file:
        html = file.read()

    # If preview is serving from unbuilt workspace and has .tsx/.jsx script tag, fallback gracefully to pure JS
    if not os.path.exists(os.path.join(workspace, "dist", "index.html")):
        if "main.tsx" in html or "App.tsx" in html or "main.jsx" in html or "src/" in html:
            standalone_js = os.path.join(workspace, "script.js")
            if not os.path.exists(standalone_js) or os.path.getsize(standalone_js) < 30:
                req = db.query(RequirementAnalysis).filter(
                    RequirementAnalysis.project_id == project_id
                ).order_by(RequirementAnalysis.created_at.desc()).first()
                req_dict = {
                    "project_summary": project.name or project.description,
                    "summary": project.description,
                    "functional_requirements": req.functional_requirements if req and req.functional_requirements else [project.description],
                    "data_entities": req.data_entities if req and req.data_entities else [],
                    "ui_requirements": req.ui_requirements if req and req.ui_requirements else []
                }
                from app.agents.coder_agent import CodeGenerationAgent
                coder = CodeGenerationAgent()
                coder.ensure_preview_entrypoint(workspace, req_dict, [])
                with open(index_path, "r", encoding="utf-8") as file:
                    html = file.read()
            
            # Rewrite unbundled module tags to pure runnable JS
            html = re.sub(r'<script[^>]*src=["\'][^"\']*\.(tsx|jsx|ts)["\'][^>]*></script>', '<script src="./script.js"></script>', html, flags=re.IGNORECASE)
            if '<link rel="stylesheet" href="./style.css">' not in html and '<link rel="stylesheet" href="style.css">' not in html:
                html = re.sub(r'(<head[^>]*>)', r'\1<link rel="stylesheet" href="./style.css">', html, count=1, flags=re.IGNORECASE)
        
    asset_base = f"/api/projects/{project_id}/preview/"
    
    # robust base tag injection
    html = re.sub(r'(<head[^>]*>)', r'\1<base href="' + asset_base + '">', html, count=1, flags=re.IGNORECASE)
    if '<base ' not in html:
        html = f'<base href="{asset_base}">{html}'
        
    return HTMLResponse(html)

@router.get("/{project_id}/preview/{asset_path:path}")
def get_project_preview_asset(project_id: str, asset_path: str, version: int = None, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    v = version or (project.current_version if project else 1)
    workspace = _preview_workspace(project_id, v, db)
    preview_root = _build_preview(workspace)
    from app.core.security import safe_join
    try:
        full_path = safe_join(preview_root, asset_path)
        if not os.path.isfile(full_path):
            full_path = safe_join(workspace, asset_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="Preview asset does not exist")

    media_type = None
    if asset_path.endswith(".css"):
        media_type = "text/css"
    elif asset_path.endswith(".js"):
        media_type = "application/javascript"
    elif asset_path.endswith(".html"):
        media_type = "text/html"
    return FileResponse(full_path, media_type=media_type)

@router.get("/{project_id}/iterations")
def get_iterations(project_id: str, db: Session = Depends(get_db)):
    return db.query(IterationHistory).filter(
        IterationHistory.project_id == project_id
    ).order_by(IterationHistory.version.desc(), IterationHistory.iteration.desc()).all()

@router.get("/{project_id}/tests")
def get_test_results(project_id: str, version: int = None, db: Session = Depends(get_db)):
    query = db.query(TestResult).filter(TestResult.project_id == project_id)
    if version:
        query = query.filter(TestResult.version == version)
    return query.order_by(TestResult.version.desc(), TestResult.iteration.desc()).all()

@router.get("/{project_id}/review")
def get_review_results(project_id: str, version: int = None, db: Session = Depends(get_db)):
    query = db.query(ReviewResult).filter(ReviewResult.project_id == project_id)
    if version:
        query = query.filter(ReviewResult.version == version)
    return query.order_by(ReviewResult.version.desc(), ReviewResult.iteration.desc()).all()

@router.get("/{project_id}/debug")
def get_debug_results(project_id: str, version: int = None, db: Session = Depends(get_db)):
    query = db.query(DebugResult).filter(DebugResult.project_id == project_id)
    if version:
        query = query.filter(DebugResult.version == version)
    return query.order_by(DebugResult.version.desc(), DebugResult.iteration.desc()).all()

@router.get("/{project_id}/evaluation")
def get_evaluation(project_id: str, version: int = None, db: Session = Depends(get_db)):
    query = db.query(EvaluationResult).filter(EvaluationResult.project_id == project_id)
    if version:
        query = query.filter(EvaluationResult.version == version)
    result = query.order_by(EvaluationResult.created_at.desc()).first()
    if not result:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return result

@router.get("/{project_id}/documentation")
def get_documentation(project_id: str, version: int = None, db: Session = Depends(get_db)):
    query = db.query(DocumentationResult).filter(DocumentationResult.project_id == project_id)
    if version:
        query = query.filter(DocumentationResult.version == version)
    result = query.order_by(DocumentationResult.generated_at.desc()).first()
    if not result:
        raise HTTPException(status_code=404, detail="Documentation not found")
    return result

@router.get("/{project_id}/versions")
def get_versions(project_id: str, db: Session = Depends(get_db)):
    versions = db.query(ProjectVersion).filter(
        ProjectVersion.project_id == project_id
    ).order_by(ProjectVersion.version.asc()).all()

    result = []
    for v in versions:
        revision = db.query(RevisionRequest).filter(
            RevisionRequest.project_id == project_id,
            RevisionRequest.source_version == v.version
        ).first()

        iterations = db.query(IterationHistory).filter(
            IterationHistory.project_id == project_id,
            IterationHistory.version == v.version
        ).count()

        result.append({
            "version": v.version,
            "status": v.status,
            "approval_status": v.approval_status,
            "evaluation_status": v.evaluation_status,
            "created_at": v.created_at.isoformat() if v.created_at else None,
            "parent_version": v.parent_version,
            "revision_feedback": v.revision_feedback,
            "iterations_used": iterations,
            "revision_feedback_for_next": revision.feedback if revision else None,
        })

    return result

@router.get("/{project_id}/versions/{version}")
def get_version_detail(project_id: str, version: int, db: Session = Depends(get_db)):
    pv = db.query(ProjectVersion).filter(
        ProjectVersion.project_id == project_id,
        ProjectVersion.version == version
    ).first()
    if not pv:
        raise HTTPException(status_code=404, detail=f"Version {version} not found")

    req = db.query(RequirementAnalysis).filter(
        RequirementAnalysis.project_id == project_id,
        RequirementAnalysis.version == version
    ).first()

    plan = db.query(DevelopmentPlan).filter(
        DevelopmentPlan.project_id == project_id,
        DevelopmentPlan.version == version
    ).first()

    files = db.query(ProjectFile).filter(
        ProjectFile.project_id == project_id,
        ProjectFile.version == version
    ).all()

    test = db.query(TestResult).filter(
        TestResult.project_id == project_id,
        TestResult.version == version
    ).order_by(TestResult.iteration.desc()).first()

    review = db.query(ReviewResult).filter(
        ReviewResult.project_id == project_id,
        ReviewResult.version == version
    ).order_by(ReviewResult.iteration.desc()).first()

    evaluation = db.query(EvaluationResult).filter(
        EvaluationResult.project_id == project_id,
        EvaluationResult.version == version
    ).first()

    return {
        "version": pv.version,
        "status": pv.status,
        "approval_status": pv.approval_status,
        "evaluation_status": pv.evaluation_status,
        "parent_version": pv.parent_version,
        "revision_feedback": pv.revision_feedback,
        "created_at": pv.created_at.isoformat() if pv.created_at else None,
        "requirements": {
            "summary": req.project_summary if req else None,
            "functional": req.functional_requirements if req else [],
            "acceptance_criteria": req.acceptance_criteria if req else []
        },
        "plan": {"architecture": plan.architecture if plan else None},
        "files": [{"path": f.path, "language": f.language} for f in files],
        "test_summary": {
            "total": test.tests_total if test else 0,
            "passed": test.tests_passed if test else 0,
            "failed": test.tests_failed if test else 0,
            "pass_rate": test.pass_rate if test else 0
        } if test else None,
        "review_summary": {
            "status": review.status if review else None,
            "critical": len(review.critical_issues or []) if review else 0,
            "major": len(review.major_issues or []) if review else 0
        } if review else None,
        "evaluation": {
            "status": evaluation.status if evaluation else None,
            "quality_summary": evaluation.quality_summary if evaluation else None,
            "test_pass_rate": evaluation.test_pass_rate if evaluation else None
        } if evaluation else None
    }

@router.get("/{project_id}/agents")
def get_agents(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    agents = db.query(AgentRun).filter(
        AgentRun.project_id == project_id
    ).order_by(AgentRun.started_at.asc()).all()
    
    return agents

@router.get("/{project_id}/report")
def get_report(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    versions = db.query(ProjectVersion).filter(ProjectVersion.project_id == project_id).all()
    evaluations = db.query(EvaluationResult).filter(EvaluationResult.project_id == project_id).all()
    test_results = db.query(TestResult).filter(TestResult.project_id == project_id).all()
    review_results = db.query(ReviewResult).filter(ReviewResult.project_id == project_id).all()
    debug_results = db.query(DebugResult).filter(DebugResult.project_id == project_id).all()
    requirements = db.query(RequirementAnalysis).filter(RequirementAnalysis.project_id == project_id).all()
    plans = db.query(DevelopmentPlan).filter(DevelopmentPlan.project_id == project_id).all()
    documentation = db.query(DocumentationResult).filter(DocumentationResult.project_id == project_id).all()
    packages = db.query(PackageMetadata).filter(PackageMetadata.project_id == project_id).all()
    iterations = db.query(IterationHistory).filter(IterationHistory.project_id == project_id).all()
    agent_runs = db.query(AgentRun).filter(AgentRun.project_id == project_id).all()
    
    report_data = {
        "project_metadata": {
            "id": project.id,
            "name": project.name,
            "status": project.status,
            "current_version": project.current_version,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
            "revision_count": project.revision_count
        },
        "versions": [{"version": v.version, "status": v.status, "approval_status": v.approval_status} for v in versions],
        "requirement_metrics": [{"version": req.version, "total_functional": len(req.functional_requirements or [])} for req in requirements],
        "planning_metrics": [{"version": plan.version, "total_modules": len(plan.modules or [])} for plan in plans],
        "testing_metrics": [{"version": tr.version, "iteration": tr.iteration, "tests_total": tr.tests_total, "tests_passed": tr.tests_passed, "pass_rate": tr.pass_rate} for tr in test_results],
        "review_metrics": [{"version": rr.version, "iteration": rr.iteration, "critical_issues": len(rr.critical_issues or []), "major_issues": len(rr.major_issues or [])} for rr in review_results],
        "debugging_metrics": [{"version": dr.version, "iteration": dr.iteration, "files_modified": len(dr.files_modified or [])} for dr in debug_results],
        "iteration_metrics": [{"version": iter.version, "iteration": iter.iteration, "stage": iter.stage, "status": iter.status} for iter in iterations],
        "evaluation_metrics": [],
        "documentation_metrics": [{"version": doc.version, "files_created": len(doc.files_created or [])} for doc in documentation],
        "agent_runs": [{"agent_name": ar.agent_name, "version": ar.version, "status": ar.status, "duration_seconds": (ar.completed_at - ar.started_at).total_seconds() if ar.completed_at and ar.started_at else None} for ar in agent_runs],
        "packaging_metadata": [{"version": pkg.version, "size": pkg.package_size, "sha256": pkg.checksum_sha256} for pkg in packages]
    }
    
    for ev in evaluations:
        report_data["evaluation_metrics"].append({
            "version": ev.version,
            "status": ev.status,
            "test_pass_rate": ev.test_pass_rate,
            "code_coverage": ev.code_coverage,
            "requirements_coverage": ev.requirements_coverage,
            "iterations_used": ev.iterations_used,
            "final_quality": ev.final_quality_status
        })
        
    return report_data

@router.get("/{project_id}/report/export")
def export_report(project_id: str, db: Session = Depends(get_db)):
    import json
    report_data = get_report(project_id, db)
    report_json = json.dumps(report_data, indent=2)
    return Response(
        content=report_json,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=project_{project_id}_report.json"}
    )

@router.get("/{project_id}/package")
def get_package(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    pkg = db.query(PackageMetadata).filter(
        PackageMetadata.project_id == project_id,
        PackageMetadata.version == project.current_version
    ).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Package not found. Project may not be approved yet.")

    return {
        "project_id": project_id,
        "version": pkg.version,
        "package_filename": pkg.package_filename,
        "package_size": pkg.package_size,
        "checksum_sha256": pkg.checksum_sha256,
        "created_at": pkg.created_at.isoformat() if pkg.created_at else None,
        "download_url": f"/api/projects/{project_id}/download"
    }

@router.get("/{project_id}/download")
def download_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    pkg = db.query(PackageMetadata).filter(
        PackageMetadata.project_id == project_id,
        PackageMetadata.version == project.current_version
    ).first()

    if not pkg or not pkg.package_path or not os.path.exists(pkg.package_path):
        raise HTTPException(status_code=404, detail="Package file not found. Please approve first.")

    return FileResponse(
        path=pkg.package_path,
        filename=pkg.package_filename,
        media_type="application/zip"
    )

@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted", "project_id": project_id}
