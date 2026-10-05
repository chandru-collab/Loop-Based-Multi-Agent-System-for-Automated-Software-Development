from typing import Dict, Any
from app.workflow.state import DevelopmentState
from app.agents.requirement_agent import RequirementAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.coder_agent import CodeGenerationAgent
from app.agents.tester_agent import TestingAgent
from app.agents.reviewer_agent import ReviewerAgent
from app.agents.debugger_agent import DebuggerAgent
from app.agents.evaluation_agent import EvaluationMetricsAgent
from app.agents.documentation_agent import DocumentationAgent
from app.database.database import SessionLocal
from app.database.models import (
    Project, AgentRun, TestResult, ReviewResult, DebugResult,
    IterationHistory, EvaluationResult, DocumentationResult, WorkflowEvent
)
import uuid
import datetime
import logging

logger = logging.getLogger(__name__)

def _update_db_stage(project_id: str, stage: str):
    if not project_id:
        return
    with SessionLocal() as db:
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.current_stage = stage
            db.commit()

def _log_event(db, project_id: str, version: int, event_type: str, details: dict):
    event = WorkflowEvent(
        id=str(uuid.uuid4()),
        project_id=project_id,
        version=version,
        event_type=event_type,
        details=details
    )
    db.add(event)

def requirement_node(state: DevelopmentState) -> Dict[str, Any]:
    agent = RequirementAgent()
    project_id = state.get("project_id")
    version = state.get("generation_version") or 1
    started_at = datetime.datetime.utcnow()
    try:
        result = agent.execute(state)
        history = list(state.get("history") or [])
        history.append({"agent": agent.name, "status": "completed"})
        _update_db_stage(project_id, "planner")
        
        with SessionLocal() as db:
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                agent_name=agent.name,
                status="completed",
                started_at=started_at,
                completed_at=datetime.datetime.utcnow(),
                output_summary="Generated project requirements and acceptance criteria"
            ))
            db.commit()

        return {
            "requirements": result["requirements"],
            "current_stage": "planner",
            "status": "REQUIREMENT_ANALYSIS_COMPLETED",
            "history": history
        }
    except Exception as e:
        logger.error(f"RequirementAgent failed: {e}")
        errors = list(state.get("errors") or []) + [str(e)]
        with SessionLocal() as db:
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                agent_name=agent.name,
                status="failed",
                started_at=started_at,
                completed_at=datetime.datetime.utcnow(),
                error_message=str(e)
            ))
            db.commit()
        return {"status": "FAILED", "current_stage": "REQUIREMENT_ANALYSIS", "errors": errors}

def planner_node(state: DevelopmentState) -> Dict[str, Any]:
    agent = PlannerAgent()
    project_id = state.get("project_id")
    version = state.get("generation_version") or 1
    started_at = datetime.datetime.utcnow()
    try:
        result = agent.execute(state)
        history = list(state.get("history") or [])
        history.append({"agent": agent.name, "status": "completed"})
        _update_db_stage(project_id, "coder")
        
        with SessionLocal() as db:
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                agent_name=agent.name,
                status="completed",
                started_at=started_at,
                completed_at=datetime.datetime.utcnow(),
                output_summary="Created architecture and development plan"
            ))
            db.commit()

        return {
            "plan": result["plan"],
            "current_stage": "coder",
            "status": "PLANNING_COMPLETED",
            "history": history
        }
    except Exception as e:
        logger.error(f"PlannerAgent failed: {e}")
        errors = list(state.get("errors") or []) + [str(e)]
        with SessionLocal() as db:
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                agent_name=agent.name,
                status="failed",
                started_at=started_at,
                completed_at=datetime.datetime.utcnow(),
                error_message=str(e)
            ))
            db.commit()
        return {"status": "FAILED", "current_stage": "PLANNING", "errors": errors}

def coder_node(state: DevelopmentState) -> Dict[str, Any]:
    agent = CodeGenerationAgent()
    project_id = state.get("project_id")
    version = state.get("generation_version") or 1
    started_at = datetime.datetime.utcnow()
    try:
        result = agent.execute(state)
        history = list(state.get("history") or [])
        history.append({"agent": agent.name, "status": "completed"})
        _update_db_stage(project_id, "tester")
        
        with SessionLocal() as db:
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                agent_name=agent.name,
                status="completed",
                started_at=started_at,
                completed_at=datetime.datetime.utcnow(),
                output_summary=f"Generated {len(result.get('generated_files', []))} files"
            ))
            db.commit()

        # Automatically launch live project server in background if runnable entrypoint exists
        try:
            from app.services.live_runner import live_runner
            live_runner.start_project(project_id, result["workspace_path"])
            logger.info(f"Auto-started live project runner for {project_id}")
        except Exception as lr_err:
            logger.debug(f"Live runner auto-start note for {project_id}: {lr_err}")

        return {
            "file_manifest": result["file_manifest"],
            "generated_files": result["generated_files"],
            "workspace_path": result["workspace_path"],
            "generation_status": result["generation_status"],
            "generation_errors": result["generation_errors"],
            "current_stage": "tester",
            "status": result["status"],
            "history": history
        }
    except Exception as e:
        logger.error(f"CodeGenerationAgent failed: {e}")
        errors = list(state.get("errors") or []) + [str(e)]
        with SessionLocal() as db:
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                agent_name=agent.name,
                status="failed",
                started_at=started_at,
                completed_at=datetime.datetime.utcnow(),
                error_message=str(e)
            ))
            db.commit()
        return {"status": "FAILED", "generation_status": "FAILED", "current_stage": "CODE_GENERATING", "errors": errors}

def tester_node(state: DevelopmentState) -> Dict[str, Any]:
    agent = TestingAgent()
    project_id = state.get("project_id")
    version = state.get("generation_version") or 1
    started_at = datetime.datetime.utcnow()
    try:
        result = agent.execute(state)
        history = list(state.get("history") or [])
        history.append({"agent": agent.name, "status": "completed"})

        iteration = state.get("iteration") or 1

        with SessionLocal() as db:
            db.add(TestResult(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                iteration=iteration,
                **result["test_results"]
            ))
            
            test_res = result.get("test_results", {})
            passed = test_res.get("tests_passed", 0)
            total = test_res.get("tests_total", 0)
            
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                agent_name=agent.name,
                status="completed",
                started_at=started_at,
                completed_at=datetime.datetime.utcnow(),
                output_summary=f"Executed {total} tests, {passed} passed."
            ))
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.current_stage = "reviewer"
            db.commit()

        return {
            "test_results": result["test_results"],
            "current_stage": "reviewer",
            "history": history
        }
    except Exception as e:
        logger.error(f"TestingAgent failed: {e}")
        errors = list(state.get("errors") or []) + [str(e)]
        with SessionLocal() as db:
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                agent_name=agent.name,
                status="failed",
                started_at=started_at,
                completed_at=datetime.datetime.utcnow(),
                error_message=str(e)
            ))
            db.commit()
        return {"status": "FAILED", "current_stage": "TESTING", "errors": errors}

def reviewer_node(state: DevelopmentState) -> Dict[str, Any]:
    agent = ReviewerAgent()
    project_id = state.get("project_id")
    version = state.get("generation_version") or 1
    started_at = datetime.datetime.utcnow()
    try:
        result = agent.execute(state)
        history = list(state.get("history") or [])
        history.append({"agent": agent.name, "status": "completed"})

        iteration = state.get("iteration") or 1

        with SessionLocal() as db:
            db.add(ReviewResult(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                iteration=iteration,
                **result["review_results"]
            ))
            
            review_res = result.get("review_results", {})
            critical = len(review_res.get("critical_issues") or [])
            major = len(review_res.get("major_issues") or [])
            confidence = review_res.get("confidence_score")
            conf_str = f" Confidence score: {confidence}%." if confidence is not None else ""
            
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                agent_name=agent.name,
                status="completed",
                started_at=started_at,
                completed_at=datetime.datetime.utcnow(),
                output_summary=f"Review found {critical} critical, {major} major issues.{conf_str}"
            ))
            db.add(IterationHistory(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                iteration=iteration,
                stage="review",
                status=result["review_results"]["status"],
                summary=result["review_results"]
            ))
            _log_event(db, project_id, version, "REVIEW_COMPLETED", {
                "status": result["review_results"]["status"],
                "confidence_score": confidence,
                "critical_issues": critical,
                "major_issues": major
            })
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.current_stage = "routing"
            db.commit()

        return {
            "review_results": result["review_results"],
            "confidence_score": confidence,
            "current_stage": "routing",
            "history": history
        }
    except Exception as e:
        logger.error(f"ReviewerAgent failed: {e}")
        errors = list(state.get("errors") or []) + [str(e)]
        with SessionLocal() as db:
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                agent_name=agent.name,
                status="failed",
                started_at=started_at,
                completed_at=datetime.datetime.utcnow(),
                error_message=str(e)
            ))
            db.commit()
        return {"status": "FAILED", "current_stage": "REVIEWING", "errors": errors}

def debugger_node(state: DevelopmentState) -> Dict[str, Any]:
    agent = DebuggerAgent()
    project_id = state.get("project_id")
    version = state.get("generation_version") or 1
    started_at = datetime.datetime.utcnow()
    try:
        result = agent.execute(state)
        history = list(state.get("history") or [])
        history.append({"agent": agent.name, "status": "completed"})

        iteration = state.get("iteration") or 1

        db_debug_result = dict(result["debug_results"])
        db_debug_result.pop("modified_files", None)

        with SessionLocal() as db:
            db.add(DebugResult(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                iteration=iteration,
                **db_debug_result
            ))
            
            db_res = result.get("debug_results", {})
            files_modified = len(db_res.get("files_modified") or [])
            
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                agent_name=agent.name,
                status="completed",
                started_at=started_at,
                completed_at=datetime.datetime.utcnow(),
                output_summary=f"Debug applied changes to {files_modified} files."
            ))
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.current_stage = "tester"
            db.commit()

        return {
            "debug_results": result["debug_results"],
            "current_stage": "tester",
            "iteration": iteration + 1,
            "history": history
        }
    except Exception as e:
        logger.error(f"DebuggerAgent failed: {e}")
        errors = list(state.get("errors") or []) + [str(e)]
        with SessionLocal() as db:
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                agent_name=agent.name,
                status="failed",
                started_at=started_at,
                completed_at=datetime.datetime.utcnow(),
                error_message=str(e)
            ))
            db.commit()
        return {"status": "FAILED", "current_stage": "DEBUGGING", "errors": errors}

def evaluator_node(state: DevelopmentState) -> Dict[str, Any]:
    agent = EvaluationMetricsAgent()
    project_id = state.get("project_id")
    version = state.get("generation_version") or 1
    started_at = datetime.datetime.utcnow()
    try:
        result = agent.execute(state)
        history = list(state.get("history") or [])
        history.append({"agent": agent.name, "status": "completed"})

        eval_data = result["evaluation_results"]

        with SessionLocal() as db:
            eval_record = EvaluationResult(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                status=eval_data["status"],
                requirements_total=eval_data.get("requirements_total", 0),
                requirements_satisfied=eval_data.get("requirements_satisfied", 0),
                requirements_coverage=eval_data.get("requirements_coverage", 0.0),
                acceptance_criteria_total=eval_data.get("acceptance_criteria_total", 0),
                acceptance_criteria_satisfied=eval_data.get("acceptance_criteria_satisfied", 0),
                acceptance_criteria_coverage=eval_data.get("acceptance_criteria_coverage", 0.0),
                tests_total=eval_data.get("tests_total", 0),
                tests_passed=eval_data.get("tests_passed", 0),
                tests_failed=eval_data.get("tests_failed", 0),
                tests_skipped=eval_data.get("tests_skipped", 0),
                test_pass_rate=eval_data.get("test_pass_rate", 0.0),
                code_coverage=eval_data.get("code_coverage"),
                review_critical_issues=eval_data.get("review_critical_issues", 0),
                review_major_issues=eval_data.get("review_major_issues", 0),
                review_minor_issues=eval_data.get("review_minor_issues", 0),
                security_issue_count=eval_data.get("security_issue_count", 0),
                iterations_used=eval_data.get("iterations_used", 0),
                files_generated=eval_data.get("files_generated", 0),
                files_modified=eval_data.get("files_modified", 0),
                final_quality_status=eval_data.get("final_quality_status", "FAIL"),
                quality_summary=eval_data.get("quality_summary", ""),
                risks=eval_data.get("risks", []),
                remaining_issues=eval_data.get("remaining_issues", []),
                recommendations=eval_data.get("recommendations", [])
            )
            db.add(eval_record)
            
            score = eval_data.get("test_pass_rate", 0)
            
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                agent_name=agent.name,
                status="completed",
                started_at=started_at,
                completed_at=datetime.datetime.utcnow(),
                output_summary=f"Evaluation complete. Pass rate: {score}%."
            ))
            _log_event(db, project_id, version, "EVALUATION_COMPLETED", {
                "status": eval_data["status"],
                "test_pass_rate": eval_data.get("test_pass_rate")
            })
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.current_stage = "documentor"
            db.commit()

        return {
            "evaluation_results": eval_data,
            "current_stage": "documentor",
            "history": history
        }
    except Exception as e:
        logger.error(f"EvaluationAgent failed: {e}")
        errors = list(state.get("errors") or []) + [str(e)]
        with SessionLocal() as db:
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                agent_name=agent.name,
                status="failed",
                started_at=started_at,
                completed_at=datetime.datetime.utcnow(),
                error_message=str(e)
            ))
            db.commit()
        return {"status": "FAILED", "current_stage": "EVALUATING", "errors": errors}

def documentor_node(state: DevelopmentState) -> Dict[str, Any]:
    agent = DocumentationAgent()
    project_id = state.get("project_id")
    version = state.get("generation_version") or 1
    started_at = datetime.datetime.utcnow()
    try:
        result = agent.execute(state)
        history = list(state.get("history") or [])
        history.append({"agent": agent.name, "status": "completed"})

        doc_data = result["documentation_results"]

        with SessionLocal() as db:
            doc_record = DocumentationResult(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                status=doc_data["status"],
                files_created=doc_data.get("files_created", []),
                files_updated=doc_data.get("files_updated", []),
                documentation_summary=doc_data.get("documentation_summary", ""),
            )
            db.add(doc_record)
            
            created = len(doc_data.get("files_created", []))
            updated = len(doc_data.get("files_updated", []))
            
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                agent_name=agent.name,
                status="completed",
                started_at=started_at,
                completed_at=datetime.datetime.utcnow(),
                output_summary=f"Created {created} files, updated {updated} documentation files."
            ))
            _log_event(db, project_id, version, "DOCUMENTATION_COMPLETED", {
                "files_created": len(doc_data.get("files_created", []))
            })
            db.commit()

        return {
            "documentation_results": doc_data,
            "current_stage": "WAITING_FOR_APPROVAL",
            "status": "WAITING_FOR_APPROVAL",
            "waiting_for_approval": True,
            "history": history
        }
    except Exception as e:
        logger.error(f"DocumentationAgent failed: {e}")
        errors = list(state.get("errors") or []) + [str(e)]
        with SessionLocal() as db:
            db.add(AgentRun(
                id=str(uuid.uuid4()),
                project_id=project_id,
                version=version,
                agent_name=agent.name,
                status="failed",
                started_at=started_at,
                completed_at=datetime.datetime.utcnow(),
                error_message=str(e)
            ))
            db.commit()
        return {"status": "FAILED", "current_stage": "DOCUMENTING", "errors": errors}
