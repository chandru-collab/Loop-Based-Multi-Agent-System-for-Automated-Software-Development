"""Automated Pytest test suite for generated Todo REST API."""
import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json().get("status") == "healthy"

def test_get_todos():
    res = client.get("/todos")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_todo_crud_lifecycle():
    # 1. Create
    payload = {
        "title": "Automated Pytest Task",
        "description": "Integration test for CRUD lifecycle",
        "priority": "HIGH",
        "category": "Testing",
        "completed": False
    }
    create_res = client.post("/todos", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()
    todo_id = created["id"]
    assert created["title"] == payload["title"]
    assert created["completed"] is False

    # 2. Read single
    get_res = client.get(f"/todos/{todo_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == todo_id

    # 3. Update
    update_res = client.put(f"/todos/{todo_id}", json={"completed": True, "title": "Updated Pytest Task"})
    assert update_res.status_code == 200
    assert update_res.json()["completed"] is True
    assert update_res.json()["title"] == "Updated Pytest Task"

    # 4. Filter
    pending_res = client.get("/todos?status=pending")
    assert pending_res.status_code == 200
    assert all(t["completed"] is False for t in pending_res.json())

    # 5. Delete
    del_res = client.delete(f"/todos/{todo_id}")
    assert del_res.status_code == 200

    # 6. Verify deleted
    not_found = client.get(f"/todos/{todo_id}")
    assert not_found.status_code == 404
