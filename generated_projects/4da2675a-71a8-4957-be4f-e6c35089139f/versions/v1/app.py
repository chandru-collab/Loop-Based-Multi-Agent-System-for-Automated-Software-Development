import os
import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
    title="Todo REST API",
    description="A clean Todo REST API with full CRUD operations, status filtering, pagination, request validation, and error handlers.",
    version="1.0.0",
)

# Enable CORS for local development and testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database store for Todos with initial seed records
DATABASE: list[dict[str, Any]] = [
    {
        "id": "task-101",
        "title": "Architect High-Throughput REST Endpoints",
        "description": "Standardize JSON schema, pagination, status filtering, and defensive validation.",
        "status": "completed",
        "priority": "urgent",
        "category": "Engineering",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "task-102",
        "title": "Implement Role-Based Access Control (RBAC)",
        "description": "Enforce bearer token authentication and scope-based permission gates.",
        "status": "pending",
        "priority": "high",
        "category": "Security",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "task-103",
        "title": "Automate Database Migration & Backup Pipeline",
        "description": "Configure persistent SQLite volume mounts and automated WAL replication.",
        "status": "completed",
        "priority": "medium",
        "category": "Operations",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "task-104",
        "title": "Design Responsive Dark-Mode User Dashboard",
        "description": "Deliver a fluid, glassmorphic UI with live event telemetry and statistics.",
        "status": "pending",
        "priority": "medium",
        "category": "Design",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
]


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Title of the todo item")
    description: Optional[str] = Field(None, max_length=500, description="Detailed description of the todo item")
    status: str = Field(default="pending", description="Status of the todo: 'pending' or 'completed'")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        v_lower = v.lower()
        if v_lower not in ["pending", "completed"]:
            raise ValueError("Status must be either 'pending' or 'completed'")
        return v_lower


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="Title of the todo item")
    description: Optional[str] = Field(None, max_length=500, description="Detailed description")
    status: Optional[str] = Field(None, description="Status of the todo: 'pending' or 'completed'")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_lower = v.lower()
            if v_lower not in ["pending", "completed"]:
                raise ValueError("Status must be either 'pending' or 'completed'")
            return v_lower
        return v


class TodoResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    status: str
    created_at: str
    updated_at: str


class TodoPaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[TodoResponse]


@app.get("/api/health", status_code=status.HTTP_200_OK)
def health_check() -> dict[str, str]:
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    new_todo = {
        "id": str(uuid.uuid4()),
        "title": payload.title.strip(),
        "description": payload.description.strip() if payload.description else "",
        "status": payload.status,
        "created_at": now,
        "updated_at": now,
    }
    DATABASE.append(new_todo)
    return new_todo


@app.get("/todos", response_model=TodoPaginatedResponse, status_code=status.HTTP_200_OK)
def list_todos(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status ('pending' or 'completed')"),
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
) -> dict[str, Any]:
    filtered = DATABASE
    if status_filter:
        sf_lower = status_filter.lower()
        if sf_lower not in ["pending", "completed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status filter. Must be 'pending' or 'completed'.",
            )
        filtered = [t for t in DATABASE if t["status"] == sf_lower]

    total = len(filtered)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_data = filtered[start_idx:end_idx]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": paginated_data,
    }


@app.get("/todos/{todo_id}", response_model=TodoResponse, status_code=status.HTTP_200_OK)
def get_todo(todo_id: str) -> dict[str, Any]:
    for todo in DATABASE:
        if todo["id"] == todo_id:
            return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id '{todo_id}' not found.")


@app.put("/todos/{todo_id}", response_model=TodoResponse, status_code=status.HTTP_200_OK)
@app.patch("/todos/{todo_id}", response_model=TodoResponse, status_code=status.HTTP_200_OK)
def update_todo(todo_id: str, payload: TodoUpdate) -> dict[str, Any]:
    target_todo = None
    for todo in DATABASE:
        if todo["id"] == todo_id:
            target_todo = todo
            break

    if not target_todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id '{todo_id}' not found.")

    if payload.title is not None:
        target_todo["title"] = payload.title.strip()
    if payload.description is not None:
        target_todo["description"] = payload.description.strip()
    if payload.status is not None:
        target_todo["status"] = payload.status

    target_todo["updated_at"] = datetime.now(timezone.utc).isoformat()
    return target_todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_200_OK)
def delete_todo(todo_id: str, response: Response) -> dict[str, Any]:
    initial_length = len(DATABASE)
    DATABASE[:] = [t for t in DATABASE if t["id"] != todo_id]

    if len(DATABASE) == initial_length:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id '{todo_id}' not found.")

    return {"message": f"Todo with id '{todo_id}' successfully deleted."}


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check_root() -> dict[str, str]:
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Serve static frontend files (index.html, script.js, style.css, assets)
@app.get("/", include_in_schema=False)
def serve_index():
    index_file = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Todo REST API Live", "docs": "/docs"}

@app.get("/{file_path:path}", include_in_schema=False)
def serve_static(file_path: str):
    safe_path = os.path.normpath(os.path.join(BASE_DIR, file_path))
    if safe_path.startswith(BASE_DIR) and os.path.isfile(safe_path):
        return FileResponse(safe_path)
    index_file = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    import socket

    def find_available_port(default_port: int = 5000, max_attempts: int = 10) -> int:
        for p in range(default_port, default_port + max_attempts):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("127.0.0.1", p)) != 0:
                    return p
        return default_port

    requested_port = int(os.environ.get("PORT", 5000))
    port = find_available_port(requested_port)
    print(f"Starting Todo REST API on http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)

