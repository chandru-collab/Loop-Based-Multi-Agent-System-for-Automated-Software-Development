from typing import TypedDict, List, Dict, Any, Optional

class DevelopmentState(TypedDict):
    project_id: str
    user_requirement: str
    revision_feedback: Optional[str]
    active_version: int
    revision_count: int
    requirements: Optional[Dict[str, Any]]
    plan: Optional[Dict[str, Any]]
    file_manifest: List[Dict[str, str]]
    generated_files: List[Dict[str, str]]
    generation_version: int
    workspace_path: Optional[str]
    generation_status: str
    generation_errors: List[str]
    test_results: Optional[Dict[str, Any]]
    review_results: Optional[Dict[str, Any]]
    debug_results: Optional[Dict[str, Any]]
    evaluation_results: Optional[Dict[str, Any]]
    documentation_results: Optional[Dict[str, Any]]
    confidence_score: Optional[float]
    routing_metadata: Optional[Dict[str, Any]]
    iteration: int
    max_iterations: int
    current_stage: str
    status: str
    approval_status: str
    waiting_for_approval: bool
    package_path: Optional[str]
    package_checksum: Optional[str]
    package_size: Optional[int]
    iteration_history: List[Dict[str, Any]]
    errors: List[str]
    history: List[Dict[str, Any]]
