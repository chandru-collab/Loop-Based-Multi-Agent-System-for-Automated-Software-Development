import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, DATABASE

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_database():
    """Reset the in-memory database before each test."""
    DATABASE.clear()
    yield
    DATABASE.clear()

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_create_todo_success():
    payload = {
        "title": "Write Unit Tests",
        "description": "Write comprehensive Pytest suite for Todo REST API",
        "status": "pending"
    }
    response = client.post("/todos", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["status"] == payload["status"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_todo_invalid_payload():
    # Missing required 'title' field
    payload = {
        "description": "Missing title test",
        "status": "pending"
    }
    response = client.post("/todos", json=payload)
    assert response.status_code == 422

def test_create_todo_invalid_status():
    payload = {
        "title": "Invalid Status Test",
        "status": "unknown_status"
    }
    response = client.post("/todos", json=payload)
    assert response.status_code == 422

def test_get_todos_pagination_and_list():
    # Seed 15 todos
    for i in range(15):
        DATABASE.append({
            "id": f"todo-{i}",
            "title": f"Todo {i}",
            "description": f"Description {i}",
            "status": "pending" if i % 2 == 0 else "completed",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        })

    # Default page 1, limit 10
    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 10
    assert data["total"] == 15
    assert data["page"] == 1
    assert data["limit"] == 10

    # Test custom page and limit
    response = client.get("/todos?page=2&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 5
    assert data["page"] == 2
    assert data["limit"] == 5

def test_get_todos_status_filtering():
    DATABASE.append({
        "id": "t1",
        "title": "Task 1",
        "description": "Desc 1",
        "status": "completed",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    })
    DATABASE.append({
        "id": "t2",
        "title": "Task 2",
        "description": "Desc 2",
        "status": "pending",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    })

    response = client.get("/todos?status=completed")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["status"] == "completed"

    response = client.get("/todos?status=pending")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["status"] == "pending"

def test_get_single_todo_success():
    DATABASE.append({
        "id": "t-abc",
        "title": "Specific Todo",
        "description": "Find me",
        "status": "pending",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    })

    response = client.get("/todos/t-abc")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "t-abc"
    assert data["title"] == "Specific Todo"

def test_get_single_todo_not_found():
    response = client.get("/todos/nonexistent")
    assert response.status_code == 404

def test_update_todo_success():
    DATABASE.append({
        "id": "t-upd",
        "title": "Old Title",
        "description": "Old Desc",
        "status": "pending",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    })

    payload = {
        "title": "New Title",
        "description": "New Desc",
        "status": "completed"
    }
    response = client.put("/todos/t-upd", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["description"] == "New Desc"
    assert data["status"] == "completed"
    assert data["updated_at"] != data["created_at"]

def test_update_todo_not_found():
    payload = {
        "title": "New Title",
        "status": "completed"
    }
    response = client.put("/todos/nonexistent", json=payload)
    assert response.status_code == 404

def test_delete_todo_success():
    DATABASE.append({
        "id": "t-del",
        "title": "Delete Me",
        "description": "Gone soon",
        "status": "pending",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    })

    response = client.delete("/todos/t-del")
    assert response.status_code == 200
    data = response.json()
    assert "successfully deleted" in data["message"]
    assert not any(t["id"] == "t-del" for t in DATABASE)

def test_delete_todo_not_found():
    response = client.delete("/todos/nonexistent")
    assert response.status_code == 404
