from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON, UniqueConstraint, Text
from sqlalchemy.sql import func
from app.database.database import Base

MAX_USER_REVISIONS = 3
MAX_DEVELOPMENT_ITERATIONS = 5

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, default="CREATED")
    current_stage = Column(String, default="requirement")
    current_version = Column(Integer, default=1)
    revision_count = Column(Integer, default=0)
    max_iterations = Column(Integer, default=MAX_DEVELOPMENT_ITERATIONS)
    max_revisions = Column(Integer, default=MAX_USER_REVISIONS)
    experiment_type = Column(String, default="B")
    approval_status = Column(String, default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ProjectVersion(Base):
    __tablename__ = "project_versions"
    __table_args__ = (UniqueConstraint("project_id", "version", name="uq_project_version"),)

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    version = Column(Integer, nullable=False)
    parent_version = Column(Integer, nullable=True)
    status = Column(String, default="ACTIVE")  # ACTIVE, SUPERSEDED, COMPLETED
    approval_status = Column(String, default="PENDING")  # PENDING, APPROVED, REVISION_REQUESTED
    workspace_path = Column(String)
    evaluation_status = Column(String, nullable=True)
    package_path = Column(String, nullable=True)
    revision_feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RevisionRequest(Base):
    __tablename__ = "revision_requests"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    source_version = Column(Integer)
    target_version = Column(Integer)
    feedback = Column(Text, nullable=False)
    status = Column(String, default="SUBMITTED")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PackageMetadata(Base):
    __tablename__ = "package_metadata"
    __table_args__ = (UniqueConstraint("project_id", "version", name="uq_package_version"),)

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    version = Column(Integer)
    package_path = Column(String)
    package_filename = Column(String)
    package_size = Column(Integer)
    checksum_sha256 = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WorkflowEvent(Base):
    __tablename__ = "workflow_events"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    version = Column(Integer)
    event_type = Column(String)  # APPROVAL_REQUEST, REVISION_REQUEST, PACKAGING_STARTED, etc.
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    version = Column(Integer, default=1)
    agent_name = Column(String)
    status = Column(String, default="pending")
    input_summary = Column(String)
    output_summary = Column(String)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(String)

class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    version = Column(Integer, default=1)
    iteration = Column(Integer)
    stage = Column(String)
    status = Column(String, default="running")
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    version = Column(Integer)
    status = Column(String)  # PASS or FAIL
    requirements_total = Column(Integer)
    requirements_satisfied = Column(Integer)
    requirements_coverage = Column(Float)
    acceptance_criteria_total = Column(Integer)
    acceptance_criteria_satisfied = Column(Integer)
    acceptance_criteria_coverage = Column(Float)
    tests_total = Column(Integer)
    tests_passed = Column(Integer)
    tests_failed = Column(Integer)
    tests_skipped = Column(Integer)
    test_pass_rate = Column(Float)
    code_coverage = Column(Float, nullable=True)
    review_critical_issues = Column(Integer)
    review_major_issues = Column(Integer)
    review_minor_issues = Column(Integer)
    security_issue_count = Column(Integer)
    iterations_used = Column(Integer)
    files_generated = Column(Integer)
    files_modified = Column(Integer)
    final_quality_status = Column(String)
    quality_summary = Column(Text)
    risks = Column(JSON)
    remaining_issues = Column(JSON)
    recommendations = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DocumentationResult(Base):
    __tablename__ = "documentation_results"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    version = Column(Integer)
    status = Column(String)  # COMPLETED or FAILED
    files_created = Column(JSON)
    files_updated = Column(JSON)
    documentation_summary = Column(Text)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

class ProjectFile(Base):
    __tablename__ = "project_files"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    version = Column(Integer, default=1)
    path = Column(String, index=True)
    file_type = Column(String)
    language = Column(String)
    purpose = Column(String)
    content_hash = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RequirementAnalysis(Base):
    __tablename__ = "requirement_analyses"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    version = Column(Integer, default=1)
    project_summary = Column(String)
    functional_requirements = Column(JSON)
    non_functional_requirements = Column(JSON)
    technology_requirements = Column(JSON)
    user_roles = Column(JSON)
    data_entities = Column(JSON)
    api_requirements = Column(JSON)
    ui_requirements = Column(JSON)
    security_requirements = Column(JSON)
    constraints = Column(JSON)
    assumptions = Column(JSON)
    acceptance_criteria = Column(JSON)
    ambiguities = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DevelopmentPlan(Base):
    __tablename__ = "development_plans"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    version = Column(Integer, default=1)
    architecture = Column(String)
    technology_stack = Column(JSON)
    modules = Column(JSON)
    components = Column(JSON)
    database_design = Column(JSON)
    api_design = Column(JSON)
    frontend_structure = Column(JSON)
    backend_structure = Column(JSON)
    file_structure = Column(JSON)
    implementation_steps = Column(JSON)
    testing_strategy = Column(String)
    security_strategy = Column(String)
    dependencies = Column(JSON)
    configuration = Column(JSON)
    deployment_notes = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    version = Column(Integer)
    iteration = Column(Integer)
    tests_total = Column(Integer)
    tests_passed = Column(Integer)
    tests_failed = Column(Integer)
    tests_skipped = Column(Integer)
    pass_rate = Column(Float)
    coverage = Column(Float)
    execution_time = Column(Float)
    failed_tests = Column(JSON)
    errors = Column(JSON)
    status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ReviewResult(Base):
    __tablename__ = "review_results"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    version = Column(Integer)
    iteration = Column(Integer)
    status = Column(String)
    critical_issues = Column(JSON)
    major_issues = Column(JSON)
    minor_issues = Column(JSON)
    missing_requirements = Column(JSON)
    security_issues = Column(JSON)
    recommendations = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DebugResult(Base):
    __tablename__ = "debug_results"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    version = Column(Integer)
    iteration = Column(Integer)
    status = Column(String)
    files_modified = Column(JSON)
    issues_addressed = Column(JSON)
    changes_summary = Column(JSON)
    remaining_issues = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class IterationHistory(Base):
    __tablename__ = "iteration_history"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, index=True)
    version = Column(Integer)
    iteration = Column(Integer)
    stage = Column(String)
    status = Column(String)
    summary = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
