import os
import json
import logging
from typing import Dict, Any

from app.agents.base import BaseAgent
from app.agents.schemas import ReviewResult
from app.core.llm import generate_with_fallback
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

logger = logging.getLogger(__name__)

class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Reviewer Agent", "Reviews generated code against requirements and tests.")

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "requirements": "dict", 
            "plan": "dict", 
            "workspace_path": "str", 
            "test_results": "dict"
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {"review_results": "dict", "status": "str"}
        
    def _read_source_files(self, workspace_path: str) -> str:
        source_context = ""
        if not os.path.exists(workspace_path):
            return source_context
            
        for root, dirs, files in os.walk(workspace_path):
            # Skip virtual environments, caches, etc.
            dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "venv", ".pytest_cache"]]
            for file in files:
                if file.endswith((".py", ".json", ".md", ".txt")) and file != "requirements.txt":
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, workspace_path)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            source_context += f"--- {rel_path} ---\n{content}\n\n"
                    except Exception:
                        pass
        return source_context

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        requirements = state.get("requirements", {})
        plan = state.get("plan", {})
        workspace_path = state.get("workspace_path")
        test_results = state.get("test_results", {})
        
        if not workspace_path:
            raise ValueError("Workspace path is missing.")
            
        logger.info(f"Reviewing project in {workspace_path}")
        
        source_context = self._read_source_files(workspace_path)
        # Truncate context to avoid token limits, but try to keep as much as possible
        source_context = source_context[:15000]
        
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "reviewer.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
            
        parser = PydanticOutputParser(pydantic_object=ReviewResult)
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Requirements:\n{requirements}\n\nPlan:\n{plan}\n\nTest Results:\n{test_results}\n\nSource Code:\n{source_code}\n\n{format_instructions}")
        ])
        
        formatted_prompt = prompt.format_messages(
            requirements=json.dumps(requirements, indent=2),
            plan=json.dumps(plan, indent=2),
            test_results=json.dumps(test_results, indent=2),
            source_code=source_context,
            format_instructions=parser.get_format_instructions()
        )
        
        try:
            review_result: ReviewResult = generate_with_fallback(formatted_prompt, ReviewResult)
        except Exception as e:
            logger.warning(f"Reviewer LLM call encountered error: {e}. Running deterministic code audit.")
            critical_issues = []
            security_issues = []
            major_issues = []
            minor_issues = []
            
            # Static sanity check on source_context
            if "TODO" in source_context or "pass\n" in source_context or "..." in source_context:
                minor_issues.append("Detected stub patterns or placeholder comments in source files.")
            if "eval(" in source_context or "exec(" in source_context:
                security_issues.append("Unsafe dynamic code execution detected.")
            if tests_failed > 0:
                critical_issues.append(f"{tests_failed} unit test(s) failed in sandbox.")

            status = "NEEDS_FIX" if (critical_issues or security_issues or major_issues) else "PASS"
            review_result = ReviewResult(
                status=status,
                critical_issues=critical_issues,
                major_issues=major_issues,
                minor_issues=minor_issues,
                missing_requirements=[],
                security_issues=security_issues,
                recommendations=["Verify all inputs are validated", "Ensure environment secrets are properly configured"]
            )
        
        # Enforce quality gates logic safely
        tests_failed = test_results.get("tests_failed", 0)
        
        # If the LLM said PASS but tests failed, override to NEEDS_FIX
        if review_result.status == "PASS" and tests_failed > 0:
            review_result.status = "NEEDS_FIX"
            if "Tests are failing" not in review_result.critical_issues:
                review_result.critical_issues.append(f"{tests_failed} tests are failing.")
                
        # If there are critical or security issues, it must be NEEDS_FIX
        if (len(review_result.critical_issues) > 0 or 
            len(review_result.major_issues) > 0 or 
            len(review_result.security_issues) > 0):
            review_result.status = "NEEDS_FIX"

        # Calculate empirical confidence score based on tests and review issues
        from app.workflow.routing import calculate_confidence_score
        synthetic_state = {
            "test_results": test_results,
            "review_results": review_result.model_dump()
        }
        score = calculate_confidence_score(synthetic_state)
        review_result.confidence_score = score

        if score < 80.0:
            review_result.status = "NEEDS_FIX"

        logger.info(f"Review completed with status={review_result.status} and confidence_score={score}%")

        return {
            "review_results": review_result.model_dump(),
            "status": "COMPLETED"
        }
