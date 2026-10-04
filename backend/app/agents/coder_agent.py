"""Code Generation Agent for generating real project files from requirements and plan."""
import os
import json
import ast
import logging
from typing import Dict, Any, List, Optional

from app.agents.base import BaseAgent
from app.agents.schemas import FileManifest, GeneratedFile
from app.core.llm import generate_with_fallback
from app.core.security import safe_join
from app.agents.preview_templates import ensure_preview_files
from app.agents.fallback_templates import generate_production_fallback_file
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

logger = logging.getLogger(__name__)

REQUIRED_PRODUCTION_FILES = [
    ("index.html", "Production browser entry point for the application UI."),
    ("style.css", "Responsive production styles for the application UI."),
    ("script.js", "Browser-side application behavior and API integration."),
    ("server.js", "Production Node.js HTTP server and static asset entry point."),
    ("app.py", "Production Python application entry point and API server."),
    ("requirements.txt", "Pinned Python runtime dependencies."),
    ("package.json", "Node.js scripts and runtime dependencies."),
    ("Dockerfile", "Production multi-stage containerization configuration."),
    ("docker-compose.yml", "Production container orchestration and service specification."),
    (".env.example", "Environment configuration template with standard defaults."),
    (".gitignore", "Production source control ignore rules."),
    ("README.md", "Production setup, operation, and API documentation."),
    ("tests/test_app.py", "Automated pytest test suite for the generated application."),
]


class CodeGenerationAgent(BaseAgent):
    """Generates complete project source files, directories, configurations, and browser UI."""

    def __init__(self):
        super().__init__("Code Generation Agent", "Generates real project files from requirements and plan.")
        self.MAX_RETRIES = 2

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "requirements": "dict",
            "plan": "dict",
            "project_id": "str",
            "generation_version": "int"
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "generated_files": "list",
            "file_manifest": "list",
            "workspace_path": "str",
            "status": "str"
        }

    def validate_python_syntax(self, code: str) -> Optional[str]:
        """Validate Python code string syntax and return error message if invalid."""
        try:
            ast.parse(code)
            return None
        except SyntaxError as e:
            return str(e)

    def ensure_production_manifest(self, manifest: FileManifest) -> FileManifest:
        """Guarantee a runnable full-stack baseline when the model omits core files."""
        existing_paths = {item.path.replace("\\", "/") for item in manifest.files}
        files = list(manifest.files)
        for path, purpose in REQUIRED_PRODUCTION_FILES:
            if path not in existing_paths:
                files.append({"path": path, "purpose": purpose, "language": path.rsplit(".", 1)[-1]})
        return FileManifest(files=files)

    def ensure_preview_entrypoint(
        self,
        workspace_path: str,
        requirements: Dict[str, Any],
        generated_files_metadata: List[Dict[str, str]],
    ) -> None:
        """Guarantee a fully functional, interactive, requirement-specific browser UI for live preview."""
        ensure_preview_files(workspace_path, requirements, generated_files_metadata)

    def _generate_production_fallback_file(
        self,
        file_path: str,
        purpose: str,
        requirements: Dict[str, Any],
        plan: Dict[str, Any]
    ) -> GeneratedFile:
        """Synthesize robust, complete, production-grade source code for any file."""
        return generate_production_fallback_file(file_path, purpose, requirements, plan)

    def _generate_manifest(self, requirements: Dict[str, Any], plan: Dict[str, Any]) -> FileManifest:
        """Prompt the LLM to generate the project file manifest and apply production baseline."""
        manifest_prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "coder_manifest.txt")
        with open(manifest_prompt_path, "r", encoding="utf-8") as f:
            manifest_system_prompt = f.read()

        manifest_parser = PydanticOutputParser(pydantic_object=FileManifest)
        manifest_prompt = ChatPromptTemplate.from_messages([
            ("system", manifest_system_prompt),
            ("human", "Requirements:\n{requirements}\n\nPlan:\n{plan}\n\n{format_instructions}")
        ])

        formatted_manifest_prompt = manifest_prompt.format_messages(
            requirements=json.dumps(requirements, indent=2),
            plan=json.dumps(plan, indent=2),
            format_instructions=manifest_parser.get_format_instructions()
        )

        logger.info("Generating File Manifest...")
        manifest: FileManifest = generate_with_fallback(formatted_manifest_prompt, FileManifest)
        return self.ensure_production_manifest(manifest)

    def _generate_file_with_retry(
        self,
        item,
        requirements: Dict[str, Any],
        plan: Dict[str, Any],
        workspace_path: str,
        file_system_prompt: str,
        file_parser: PydanticOutputParser
    ) -> Optional[Dict[str, str]]:
        """Generate a single file with LLM retries and syntax validation."""
        for attempt in range(self.MAX_RETRIES + 1):
            file_prompt = ChatPromptTemplate.from_messages([
                ("system", file_system_prompt),
                ("human", "Requirements:\n{requirements}\n\nPlan:\n{plan}\n\nGenerate file: {file_path} (Purpose: {purpose})\n\n{format_instructions}")
            ])

            formatted_file_prompt = file_prompt.format_messages(
                requirements=json.dumps(requirements, indent=2),
                plan=json.dumps(plan, indent=2),
                file_path=item.path,
                purpose=item.purpose,
                format_instructions=file_parser.get_format_instructions()
            )

            try:
                generated_file: GeneratedFile = generate_with_fallback(formatted_file_prompt, GeneratedFile)

                if item.path.endswith(".py"):
                    syntax_error = self.validate_python_syntax(generated_file.content)
                    if syntax_error:
                        raise ValueError(f"Syntax error in {item.path}: {syntax_error}")

                full_path = safe_join(workspace_path, item.path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(generated_file.content)

                logger.info(f"Successfully generated {item.path}")
                return {
                    "path": item.path,
                    "language": generated_file.language,
                    "purpose": generated_file.purpose
                }
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {item.path}: {e}")

        return None

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete project generation workflow."""
        requirements = state.get("requirements")
        plan = state.get("plan")
        project_id = state.get("project_id")
        version = state.get("generation_version", 1)

        if not requirements or not plan:
            raise ValueError("Requirements or Plan missing. Run previous agents first.")

        workspace_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "..",
                "generated_projects",
                project_id,
                "versions",
                f"v{version}",
            )
        )
        os.makedirs(workspace_path, exist_ok=True)

        # 1. Generate File Manifest
        manifest = self._generate_manifest(requirements, plan)

        # 2. Read File Generation Prompt
        file_prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "coder_file.txt")
        with open(file_prompt_path, "r", encoding="utf-8") as f:
            file_system_prompt = f.read()

        file_parser = PydanticOutputParser(pydantic_object=GeneratedFile)
        generated_files_metadata = []
        errors = []

        # 3. Generate each file from manifest
        for item in manifest.files:
            logger.info(f"Generating file: {item.path}...")
            file_meta = self._generate_file_with_retry(
                item,
                requirements,
                plan,
                workspace_path,
                file_system_prompt,
                file_parser
            )

            if file_meta:
                generated_files_metadata.append(file_meta)
            else:
                # Synthesize robust production fallback
                logger.info(f"Synthesizing production-grade implementation for {item.path}...")
                fallback_file = self._generate_production_fallback_file(
                    item.path, item.purpose, requirements, plan
                )
                try:
                    full_path = safe_join(workspace_path, item.path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(fallback_file.content)
                    generated_files_metadata.append({
                        "path": item.path,
                        "language": fallback_file.language,
                        "purpose": fallback_file.purpose
                    })
                    logger.info(f"Successfully synthesized production fallback for {item.path}")
                except Exception as write_err:
                    errors.append(f"Failed to write synthesized {item.path}: {write_err}")

        # 4. Guarantee interactive live preview entrypoint
        self.ensure_preview_entrypoint(workspace_path, requirements, generated_files_metadata)

        status = "CODE_GENERATION_COMPLETED"

        return {
            "file_manifest": [f.model_dump() for f in manifest.files],
            "generated_files": generated_files_metadata,
            "workspace_path": workspace_path,
            "generation_status": status,
            "generation_errors": errors,
            "status": status
        }
