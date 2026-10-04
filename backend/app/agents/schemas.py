from pydantic import BaseModel, Field
from typing import List, Optional

class RequirementAnalysisOutput(BaseModel):
    project_summary: str = Field(description="A brief summary of the project and its goals.")
    functional_requirements: List[str] = Field(description="List of explicit functional requirements.")
    non_functional_requirements: List[str] = Field(description="List of non-functional requirements (e.g., performance, scale).")
    technology_requirements: List[str] = Field(description="List of technology constraints and requirements.")
    user_roles: List[str] = Field(description="List of user roles interacting with the system.")
    data_entities: List[str] = Field(description="List of core data entities.")
    api_requirements: List[str] = Field(description="List of API endpoint requirements.")
    ui_requirements: List[str] = Field(description="List of UI/UX requirements.")
    security_requirements: List[str] = Field(description="List of security requirements.")
    constraints: List[str] = Field(description="List of constraints.")
    assumptions: List[str] = Field(description="List of assumptions made that are not explicitly stated by the user.")
    acceptance_criteria: List[str] = Field(description="List of testable acceptance criteria.")
    ambiguities: List[str] = Field(description="List of ambiguities or unclear requirements.")

class DevelopmentPlanOutput(BaseModel):
    architecture: str = Field(description="High-level architecture description.")
    technology_stack: List[str] = Field(description="List of chosen technologies.")
    modules: List[str] = Field(description="List of system modules.")
    components: List[str] = Field(description="List of frontend and backend components.")
    database_design: List[str] = Field(description="Description of the database schema and relationships.")
    api_design: List[str] = Field(description="List of API routes and their purpose.")
    frontend_structure: List[str] = Field(description="Directory and file structure for the frontend.")
    backend_structure: List[str] = Field(description="Directory and file structure for the backend.")
    file_structure: List[str] = Field(description="Overall projected file structure.")
    implementation_steps: List[str] = Field(description="Ordered list of steps to implement the project.")
    testing_strategy: str = Field(description="Strategy for testing the application.")
    security_strategy: str = Field(description="Strategy for securing the application.")
    dependencies: List[str] = Field(description="List of external dependencies required.")
    configuration: List[str] = Field(description="List of environment variables and configuration needed.")
    deployment_notes: str = Field(description="Notes on how to deploy the application.")

class FileManifestItem(BaseModel):
    path: str = Field(description="Relative path of the file (e.g. src/main.py)")
    purpose: str = Field(description="Purpose of the file")
    language: str = Field(description="Programming language or format (e.g. python, json, markdown)")

class FileManifest(BaseModel):
    files: List[FileManifestItem] = Field(description="List of all files to be generated")

class GeneratedFile(BaseModel):
    path: str = Field(description="Relative path of the file")
    purpose: str = Field(description="Purpose of the file")
    language: str = Field(description="Programming language (e.g. python, markdown, json)")
    content: str = Field(description="The complete source code of the file. Do NOT wrap in markdown code blocks.")

class ReviewResult(BaseModel):
    status: str = Field(description="Status of the review: PASS or NEEDS_FIX")
    critical_issues: List[str] = Field(description="Issues that block basic functionality")
    major_issues: List[str] = Field(description="Significant defects or missing requirements")
    minor_issues: List[str] = Field(description="Non-blocking issues like style or optimization")
    missing_requirements: List[str] = Field(description="Requirements from the list that were not implemented")
    security_issues: List[str] = Field(description="Security vulnerabilities detected")
    recommendations: List[str] = Field(description="General improvements")

class ModifiedFile(BaseModel):
    path: str = Field(description="Relative path of the modified file")
    content: str = Field(description="The complete new source code of the file. Do NOT wrap in markdown code blocks.")

class DebugResult(BaseModel):
    status: str = Field(description="Status of the debug process: FIXED or FAILED")
    modified_files: List[ModifiedFile] = Field(description="The files that were modified with their new content")
    files_modified: List[str] = Field(description="List of file paths that were modified")
    issues_addressed: List[str] = Field(description="List of issues that were targeted")
    changes_summary: List[str] = Field(description="Summary of what was changed")
    remaining_issues: List[str] = Field(description="Issues that could not be fixed")

class EvaluationOutput(BaseModel):
    """LLM-generated evaluation supplement for risks and recommendations."""
    quality_summary: str = Field(description="Brief overall quality summary of the project")
    risks: List[str] = Field(description="Known risks or concerns about the generated project")
    remaining_issues: List[str] = Field(description="Issues not resolved during development")
    recommendations: List[str] = Field(description="Recommendations for improvement")
    acceptance_criteria_satisfied: int = Field(description="Number of acceptance criteria that were satisfied based on the test results and review. Be conservative - only count as satisfied if tests confirm it.")

class DocumentationOutput(BaseModel):
    """LLM-generated documentation content."""
    readme: str = Field(description="Complete README.md content for the generated project")
    architecture: str = Field(description="Architecture documentation describing the system design")
    setup_guide: str = Field(description="Step-by-step setup and installation instructions")
    api_docs: str = Field(description="API endpoints documentation")
    testing_guide: str = Field(description="How to run tests and interpret results")
    development_history: str = Field(description="Summary of the development process and iterations")
    known_issues: str = Field(description="Known limitations and issues")
