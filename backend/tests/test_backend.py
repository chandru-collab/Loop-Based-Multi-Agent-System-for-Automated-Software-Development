import os
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import Base, engine, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.workflow.graph import development_graph
from app.agents.base import BaseAgent
from app.agents.coder_agent import CodeGenerationAgent
from app.agents.schemas import FileManifest, FileManifestItem, GeneratedFile
from app.api.routes.projects import _persist_result
from app.database.models import Project, ProjectFile
from typing import Dict, Any

# Test Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine_test = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

Base.metadata.create_all(bind=engine_test)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

class MockAgent(BaseAgent):
    def get_input_schema(self) -> Dict[str, Any]:
        return {}
    def get_output_schema(self) -> Dict[str, Any]:
        return {}
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success"}

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_project_creation_and_persistence():
    response = client.post("/api/projects/", json={"name": "Test Proj", "description": "Test Desc", "max_iterations": 3})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Proj"
    assert "id" in data
    proj_id = data["id"]
    
    # Check persistence
    response2 = client.get(f"/api/projects/{proj_id}")
    assert response2.status_code == 200
    assert response2.json()["name"] == "Test Proj"

def test_base_agent():
    agent = MockAgent("mock", "A mock agent")
    assert agent.name == "mock"
    assert agent.execute({}) == {"status": "success"}

def test_langgraph_construction():
    assert development_graph is not None

def test_langgraph_routing_max_iterations():
    from app.workflow.routing import route_after_review
    state = {"review_results": {"critical_issues": ["issue"]}, "iteration": 5, "max_iterations": 5}
    # Max iterations reached, should go to evaluator despite critical issues
    assert route_after_review(state) == "evaluator"

def test_langgraph_routing_issues():
    from app.workflow.routing import route_after_review
    state = {"review_results": {"major_issues": ["issue"]}, "iteration": 1, "max_iterations": 5}
    assert route_after_review(state) == "debugger"

def test_langgraph_routing_no_issues():
    from app.workflow.routing import route_after_review
    state = {"review_results": {"critical_issues": [], "major_issues": []}, "iteration": 1, "max_iterations": 5}
    assert route_after_review(state) == "evaluator"


def test_code_generation_agent_executes_successfully(monkeypatch):
    agent = CodeGenerationAgent()
    state = {
        "requirements": {"summary": "Build a to-do app"},
        "plan": {"architecture": "Simple single-page app"},
        "project_id": "regression-test-project",
        "generation_version": 1,
    }

    manifest = FileManifest(files=[
        FileManifestItem(path="index.html", purpose="Landing page", language="html"),
        FileManifestItem(path="app.py", purpose="Backend app", language="python"),
    ])

    def fake_generate(prompt, output_model):
        if output_model is FileManifest:
            return manifest

        text = str(prompt)
        if "app.py" in text:
            return GeneratedFile(
                path="app.py",
                purpose="Backend app",
                language="python",
                content="print('hello')\n",
            )

        return GeneratedFile(
            path="index.html",
            purpose="Landing page",
            language="html",
            content="<html><body>Hello</body></html>",
        )

    monkeypatch.setattr("app.agents.coder_agent.generate_with_fallback", fake_generate)

    result = agent.execute(state)

    assert result["generation_status"] == "CODE_GENERATION_COMPLETED"
    assert result["status"] == "CODE_GENERATION_COMPLETED"
    assert os.path.exists(os.path.join(result["workspace_path"], "index.html"))
    html = open(os.path.join(result["workspace_path"], "index.html"), encoding="utf-8").read()
    assert "<!doctype html>" in html.lower()
    assert "script.js" in html


def test_fallback_preview_contains_real_app_ui():
    agent = CodeGenerationAgent()
    workspace_path = os.path.join("generated_projects", "fallback-preview-check", "versions", "v1")
    os.makedirs(workspace_path, exist_ok=True)

    agent.ensure_preview_entrypoint(
        workspace_path,
        {"summary": "Build a to-do app with task tracking"},
        [],
    )

    html = open(os.path.join(workspace_path, "index.html"), encoding="utf-8").read()
    assert "<!doctype html>" in html.lower()
    assert "script.js" in html
    assert os.path.exists(os.path.join(workspace_path, "script.js"))


def test_persist_result_tracks_documentation_files():
    with TestingSessionLocal() as db:
        project_id = str(uuid.uuid4())
        project = Project(
            id=project_id,
            name="Doc Project",
            description="Doc project description",
            max_iterations=3,
            status="RUNNING",
        )
        db.add(project)
        db.commit()

        _persist_result(
            project,
            {
                "status": "WAITING_FOR_APPROVAL",
                "current_stage": "WAITING_FOR_APPROVAL",
                "documentation_results": {
                    "status": "COMPLETED",
                    "files_created": ["README.md", "docs/setup.md", "docs/api.md"],
                    "files_updated": [],
                    "documentation_summary": "Generated docs",
                },
            },
            1,
            db,
        )

        files = db.query(ProjectFile).filter(ProjectFile.project_id == project.id).all()
        paths = {f.path for f in files}
        assert "README.md" in paths
        assert "docs/setup.md" in paths
        assert "docs/api.md" in paths
