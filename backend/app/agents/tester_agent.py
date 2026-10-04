import os
import json
import logging
from typing import Dict, Any

from app.agents.base import BaseAgent
from app.agents.schemas import GeneratedFile
from app.core.llm import generate_with_fallback
from app.execution.sandbox import SandboxExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

logger = logging.getLogger(__name__)

class TestingAgent(BaseAgent):
    def __init__(self):
        super().__init__("Testing Agent", "Executes tests via SandboxExecutor and generates tests if missing.")

    def get_input_schema(self) -> Dict[str, Any]:
        return {"workspace_path": "str", "requirements": "dict", "plan": "dict", "generated_files": "list"}

    def get_output_schema(self) -> Dict[str, Any]:
        return {"test_results": "dict", "status": "str"}
        
    def _check_tests_exist(self, workspace_path: str) -> bool:
        if not os.path.exists(workspace_path):
            return False
            
        # Check tests/ directory
        tests_dir = os.path.join(workspace_path, "tests")
        if os.path.exists(tests_dir):
            for root, _, files in os.walk(tests_dir):
                if any(f.startswith("test_") or f.endswith("_test.py") for f in files):
                    return True
                    
        # Check root directory
        for f in os.listdir(workspace_path):
            if f.startswith("test_") or f.endswith("_test.py"):
                return True
                
        return False
        
    def _generate_tests(self, workspace_path: str, requirements: dict, plan: dict, generated_files: list):
        logger.info("No tests found. Generating test files...")
        
        # Read some source code to give context to the LLM (e.g. main.py or models.py)
        source_context = ""
        for f in generated_files:
            path = f.get("path", "")
            if path.endswith(".py") and not path.startswith("tests/"):
                full_path = os.path.join(workspace_path, path)
                if os.path.exists(full_path):
                    with open(full_path, "r", encoding="utf-8") as file:
                        content = file.read()
                        source_context += f"--- {path} ---\n{content}\n\n"
                        
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "tester_generate.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
            
        parser = PydanticOutputParser(pydantic_object=GeneratedFile)
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Requirements:\n{requirements}\n\nPlan:\n{plan}\n\nSource Context:\n{source_context}\n\nGenerate the test suite.\n{format_instructions}")
        ])
        
        formatted_prompt = prompt.format_messages(
            requirements=json.dumps(requirements, indent=2),
            plan=json.dumps(plan, indent=2),
            source_context=source_context[:10000], # Limit context size
            format_instructions=parser.get_format_instructions()
        )
        
        try:
            generated_test: GeneratedFile = generate_with_fallback(formatted_prompt, GeneratedFile)
            
            safe_path = generated_test.path.lstrip("/\\")
            if not safe_path.startswith("tests/"):
                safe_path = "tests/" + safe_path
                
            if ".." in safe_path:
                raise ValueError("Invalid path traversal")
                
            full_path = os.path.join(workspace_path, safe_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(generated_test.content)
                
            logger.info(f"Successfully generated tests at {safe_path}")
        except Exception as e:
            logger.error(f"Failed to generate tests: {e}")

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        workspace_path = state.get("workspace_path")
        requirements = state.get("requirements", {})
        plan = state.get("plan", {})
        generated_files = state.get("generated_files", [])
        
        if not workspace_path:
            raise ValueError("Workspace path is missing.")
            
        if not self._check_tests_exist(workspace_path):
            self._generate_tests(workspace_path, requirements, plan, generated_files)
            
        logger.info(f"Executing tests in sandbox for workspace: {workspace_path}")
        executor = SandboxExecutor()
        test_results = executor.execute_tests(workspace_path)
        
        return {
            "test_results": test_results,
            "status": "COMPLETED"
        }
