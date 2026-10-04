import os
import json
import logging
from typing import Dict, Any

from app.agents.base import BaseAgent
from app.agents.schemas import EvaluationOutput
from app.core.llm import generate_with_fallback
from app.database.database import SessionLocal
from app.database.models import (
    TestResult, ReviewResult, DebugResult, IterationHistory,
    ProjectFile, RequirementAnalysis
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

logger = logging.getLogger(__name__)

class EvaluationMetricsAgent(BaseAgent):
    def __init__(self):
        super().__init__("Evaluation Agent", "Evaluates the final project against requirements and quality gates.")

    def get_input_schema(self) -> Dict[str, Any]:
        return {}

    def get_output_schema(self) -> Dict[str, Any]:
        return {"evaluation_results": "dict"}

    def _collect_metrics(self, project_id: str, version: int) -> Dict[str, Any]:
        """Collect hard metrics from the database - no fabrication."""
        with SessionLocal() as db:
            # Get all test results for this version
            test_results = db.query(TestResult).filter(
                TestResult.project_id == project_id,
                TestResult.version == version
            ).order_by(TestResult.iteration.desc()).all()

            # Get all review results
            review_results = db.query(ReviewResult).filter(
                ReviewResult.project_id == project_id,
                ReviewResult.version == version
            ).order_by(ReviewResult.iteration.desc()).all()

            # Get all debug results
            debug_results = db.query(DebugResult).filter(
                DebugResult.project_id == project_id,
                DebugResult.version == version
            ).order_by(DebugResult.iteration.desc()).all()

            # Get iteration history
            iterations = db.query(IterationHistory).filter(
                IterationHistory.project_id == project_id,
                IterationHistory.version == version
            ).all()

            # Get file count
            files = db.query(ProjectFile).filter(
                ProjectFile.project_id == project_id,
                ProjectFile.version == version
            ).all()

            # Get requirements
            req = db.query(RequirementAnalysis).filter(
                RequirementAnalysis.project_id == project_id,
                RequirementAnalysis.version == version
            ).order_by(RequirementAnalysis.created_at.desc()).first()

            # Use the LAST test result (final iteration)
            last_test = test_results[0] if test_results else None
            last_review = review_results[0] if review_results else None

            # Aggregate files_modified across debug runs
            total_files_modified = sum(
                len(dr.files_modified or []) for dr in debug_results
            )

            # Requirements totals
            req_total = 0
            acceptance_criteria_total = 0
            if req:
                req_total = len(req.functional_requirements or []) + len(req.non_functional_requirements or [])
                acceptance_criteria_total = len(req.acceptance_criteria or [])

            return {
                "last_test": last_test,
                "last_review": last_review,
                "total_iterations": len(set(ih.iteration for ih in iterations)),
                "files_generated": len(files),
                "total_files_modified": total_files_modified,
                "req_total": req_total,
                "acceptance_criteria_total": acceptance_criteria_total,
                "requirements": req,
                "all_reviews": review_results,
            }

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        project_id = state.get("project_id")
        version = state.get("generation_version", 1)

        logger.info(f"Evaluating project {project_id} version {version}")

        metrics = self._collect_metrics(project_id, version)
        last_test = metrics["last_test"]
        last_review = metrics["last_review"]

        # Hard numeric metrics from DB
        tests_total = last_test.tests_total if last_test else 0
        tests_passed = last_test.tests_passed if last_test else 0
        tests_failed = last_test.tests_failed if last_test else 0
        tests_skipped = last_test.tests_skipped if last_test else 0
        test_pass_rate = last_test.pass_rate if last_test else 0.0
        code_coverage = last_test.coverage if last_test else None

        review_critical = len(last_review.critical_issues or []) if last_review else 0
        review_major = len(last_review.major_issues or []) if last_review else 0
        review_minor = len(last_review.minor_issues or []) if last_review else 0
        security_count = len(last_review.security_issues or []) if last_review else 0

        # Quality gate
        gate_passed = (
            tests_failed == 0 and
            review_critical == 0 and
            review_major == 0 and
            security_count == 0
        )
        final_quality_status = "PASS" if gate_passed else "FAIL"

        # LLM supplement for qualitative metrics
        req = metrics["requirements"]
        req_summary = json.dumps({
            "functional_requirements": req.functional_requirements if req else [],
            "acceptance_criteria": req.acceptance_criteria if req else []
        }, indent=2) if req else "{}"

        test_summary = json.dumps({
            "tests_total": tests_total,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "pass_rate": test_pass_rate
        }, indent=2)

        review_summary = json.dumps({
            "critical_issues": last_review.critical_issues if last_review else [],
            "major_issues": last_review.major_issues if last_review else [],
            "minor_issues": last_review.minor_issues if last_review else [],
            "security_issues": last_review.security_issues if last_review else []
        }, indent=2)

        parser = PydanticOutputParser(pydantic_object=EvaluationOutput)
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert software quality evaluator.
You are given factual metrics from a completed development workflow.
Your job is to:
1. Write a quality summary based on the facts provided.
2. Identify real risks based on the review findings.
3. List remaining issues (if any).
4. Provide actionable recommendations.
5. Count how many acceptance criteria were satisfied based on the test results. 
   Only count an acceptance criterion as satisfied if the test data suggests it was verified.
   Be conservative - if uncertain, do NOT count it as satisfied.
Do NOT fabricate test results or review findings. Only use what is provided."""),
            ("human", """Requirements and Acceptance Criteria:
{req_summary}

Test Results:
{test_summary}

Review Results:
{review_summary}

Iterations used: {iterations}
Files generated: {files_generated}
Files modified by debugger: {files_modified}
Quality gate: {gate}

{format_instructions}""")
        ])

        formatted = prompt.format_messages(
            req_summary=req_summary,
            test_summary=test_summary,
            review_summary=review_summary,
            iterations=metrics["total_iterations"],
            files_generated=metrics["files_generated"],
            files_modified=metrics["total_files_modified"],
            gate=final_quality_status,
            format_instructions=parser.get_format_instructions()
        )

        try:
            llm_eval: EvaluationOutput = generate_with_fallback(formatted, EvaluationOutput)
        except Exception as e:
            logger.error(f"LLM evaluation failed: {e}")
            llm_eval = EvaluationOutput(
                quality_summary=f"Quality gate: {final_quality_status}. LLM evaluation unavailable.",
                risks=["LLM evaluation could not be completed"],
                remaining_issues=[],
                recommendations=[],
                acceptance_criteria_satisfied=0
            )

        req_total = metrics["req_total"]
        acc_total = metrics["acceptance_criteria_total"]
        acc_satisfied = min(llm_eval.acceptance_criteria_satisfied, acc_total)
        acc_coverage = (acc_satisfied / acc_total * 100) if acc_total > 0 else 0.0

        # Requirements coverage based on test pass rate
        req_satisfied = int((test_pass_rate / 100.0) * req_total) if req_total > 0 else 0
        req_coverage = (req_satisfied / req_total * 100) if req_total > 0 else 0.0

        evaluation_result = {
            "status": final_quality_status,
            "requirements_total": req_total,
            "requirements_satisfied": req_satisfied,
            "requirements_coverage": round(req_coverage, 1),
            "acceptance_criteria_total": acc_total,
            "acceptance_criteria_satisfied": acc_satisfied,
            "acceptance_criteria_coverage": round(acc_coverage, 1),
            "tests_total": tests_total,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "tests_skipped": tests_skipped,
            "test_pass_rate": round(test_pass_rate, 1),
            "code_coverage": code_coverage,
            "review_critical_issues": review_critical,
            "review_major_issues": review_major,
            "review_minor_issues": review_minor,
            "security_issue_count": security_count,
            "iterations_used": metrics["total_iterations"],
            "files_generated": metrics["files_generated"],
            "files_modified": metrics["total_files_modified"],
            "final_quality_status": final_quality_status,
            "quality_summary": llm_eval.quality_summary,
            "risks": llm_eval.risks,
            "remaining_issues": llm_eval.remaining_issues,
            "recommendations": llm_eval.recommendations
        }

        logger.info(f"Evaluation complete for {project_id}: {final_quality_status}")
        return {"evaluation_results": evaluation_result, "status": "COMPLETED"}
