import os
import json
import logging
from typing import Dict, Any

from app.agents.base import BaseAgent
from app.agents.schemas import DebugResult
from app.core.llm import generate_with_fallback
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

logger = logging.getLogger(__name__)

class DebuggerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Debugger Agent", "Modifies generated code to fix tests and review issues.")

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "workspace_path": "str", 
            "test_results": "dict",
            "review_results": "dict"
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {"debug_results": "dict", "status": "str"}
        
    def _read_source_files(self, workspace_path: str) -> str:
        source_context = ""
        if not os.path.exists(workspace_path):
            return source_context
            
        for root, dirs, files in os.walk(workspace_path):
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
        workspace_path = state.get("workspace_path")
        test_results = state.get("test_results", {})
        review_results = state.get("review_results", {})
        
        if not workspace_path:
            raise ValueError("Workspace path is missing.")
            
        logger.info(f"Debugging project in {workspace_path}")
        
        source_context = self._read_source_files(workspace_path)
        source_context = source_context[:20000] # Provide up to 20K chars of context
        
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "debugger.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
            
        parser = PydanticOutputParser(pydantic_object=DebugResult)
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Test Results:\n{test_results}\n\nReview Results:\n{review_results}\n\nSource Code:\n{source_code}\n\n{format_instructions}")
        ])
        
        formatted_prompt = prompt.format_messages(
            test_results=json.dumps(test_results, indent=2),
            review_results=json.dumps(review_results, indent=2),
            source_code=source_context,
            format_instructions=parser.get_format_instructions()
        )
        
        debug_result: DebugResult = generate_with_fallback(formatted_prompt, DebugResult)
        
        # Write modified files to disk
        modified_paths = []
        from app.core.security import safe_join
        for mod_file in debug_result.modified_files:
            try:
                full_path = safe_join(workspace_path, mod_file.path)
            except ValueError as ve:
                logger.warning(f"Skipping invalid path in debugger: {ve}")
                continue
                
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(mod_file.content)
                
            modified_paths.append(mod_file.path)
            logger.info(f"Debugger modified: {mod_file.path}")
            
        # Update the list of files modified (to match what was actually written)
        debug_result.files_modified = modified_paths

        return {
            "debug_results": debug_result.model_dump(),
            "status": "COMPLETED"
        }
