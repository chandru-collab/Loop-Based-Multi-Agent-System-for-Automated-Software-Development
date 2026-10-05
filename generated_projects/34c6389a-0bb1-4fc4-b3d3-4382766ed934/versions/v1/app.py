"""Production FastAPI Todo Application with SQLite & Full CRUD Endpoints."""
import os
import sys
import sqlite3
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("todo_app")

DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "todos.db"))

INITIAL_SEED_TODOS = [
    ("Setup FastAPI backend routing & SQLite models", "Configure SQLAlchemy SQLite database and Pydantic schemas", "HIGH", "Backend", 1, "2026-10-05 10:00"),
    ("Implement CRUD endpoints and status filtering", "Build GET, POST, PUT, DELETE with query parameter filters", "HIGH", "Dev", 1, "2026-10-05 11:15"),
    ("Add pagination and validation query params", "Allow users to filter by pending/completed with custom page sizes", "MEDIUM", "Testing", 0, "2026-10-05 12:30"),
    ("Automate Pytest test suites with TestClient", "Verify 100% test coverage for create, read, update, delete operations", "MEDIUM", "Security", 0, "2026-10-05 13:45"),
]

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                priority TEXT DEFAULT 'MEDIUM',
                category TEXT DEFAULT 'General',
                completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("SELECT COUNT(*) FROM todos")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO todos (title, description, priority, category, completed, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, INITIAL_SEED_TODOS)
        conn.commit()

init_db()

app = FastAPI(
    title="Todo REST API",
    description="Production-grade Todo Management API with CRUD, status filtering, and pagination.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field("", max_length=1000)
    priority: Optional[str] = Field("MEDIUM", max_length=20)
    category: Optional[str] = Field("General", max_length=50)
    completed: Optional[bool] = False

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    completed: Optional[bool] = None

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    category: str
    completed: bool
    created_at: str

@app.get("/health", tags=["System"])
def health():
    return {
        "status": "healthy",
        "service": "Todo REST API",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/todos", tags=["Todos"])
@app.get("/api/todos", tags=["Todos"])
def get_todos(
    status: Optional[str] = Query("all", description="all, pending, completed"),
    search: Optional[str] = Query(None, description="Search keyword"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        query = "SELECT * FROM todos WHERE 1=1"
        params = []
        
        if status == "pending":
            query += " AND completed = 0"
        elif status == "completed":
            query += " AND completed = 1"
            
        if search:
            query += " AND (title LIKE ? OR description LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
            
        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        offset = (page - 1) * limit
        params.extend([limit, offset])
        
        cur.execute(query, params)
        rows = cur.fetchall()
        
        result = []
        for r in rows:
            d = dict(r)
            d["completed"] = bool(d["completed"])
            result.append(d)
        return result

@app.post("/todos", status_code=status.HTTP_201_CREATED, tags=["Todos"])
@app.post("/api/todos", status_code=status.HTTP_201_CREATED, tags=["Todos"])
def create_todo(payload: TodoCreate):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO todos (title, description, priority, category, completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            payload.title,
            payload.description or "",
            payload.priority or "MEDIUM",
            payload.category or "General",
            1 if payload.completed else 0,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))
        conn.commit()
        todo_id = cur.lastrowid
        cur.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        row = dict(cur.fetchone())
        row["completed"] = bool(row["completed"])
        return row

@app.get("/todos/{todo_id}", tags=["Todos"])
@app.get("/api/todos/{todo_id}", tags=["Todos"])
def get_todo(todo_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Todo not found")
        res = dict(row)
        res["completed"] = bool(res["completed"])
        return res

@app.put("/todos/{todo_id}", tags=["Todos"])
@app.put("/api/todos/{todo_id}", tags=["Todos"])
@app.patch("/todos/{todo_id}", tags=["Todos"])
@app.patch("/api/todos/{todo_id}", tags=["Todos"])
def update_todo(todo_id: int, payload: TodoUpdate):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        existing = cur.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        current = dict(existing)
        new_title = payload.title if payload.title is not None else current["title"]
        new_desc = payload.description if payload.description is not None else current["description"]
        new_prio = payload.priority if payload.priority is not None else current["priority"]
        new_cat = payload.category if payload.category is not None else current["category"]
        new_comp = 1 if (payload.completed if payload.completed is not None else current["completed"]) else 0
        
        cur.execute("""
            UPDATE todos SET title = ?, description = ?, priority = ?, category = ?, completed = ?
            WHERE id = ?
        """, (new_title, new_desc, new_prio, new_cat, new_comp, todo_id))
        conn.commit()
        
        cur.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        res = dict(cur.fetchone())
        res["completed"] = bool(res["completed"])
        return res

@app.delete("/todos/{todo_id}", tags=["Todos"])
@app.delete("/api/todos/{todo_id}", tags=["Todos"])
def delete_todo(todo_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Todo not found")
        return {"message": "Todo deleted successfully", "id": todo_id}

@app.post("/todos/reset", tags=["Todos"])
@app.post("/api/todos/reset", tags=["Todos"])
def reset_todos():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM todos")
        cur.executemany("""
            INSERT INTO todos (title, description, priority, category, completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, INITIAL_SEED_TODOS)
        conn.commit()
        return {"message": "Todos reset to initial seed data", "count": len(INITIAL_SEED_TODOS)}

# Frontend static serving
@app.get("/", include_in_schema=False)
def serve_root():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

if os.path.exists(os.path.join(BASE_DIR, "style.css")):
    @app.get("/style.css", include_in_schema=False)
    def serve_css():
        return FileResponse(os.path.join(BASE_DIR, "style.css"), media_type="text/css")

if os.path.exists(os.path.join(BASE_DIR, "script.js")):
    @app.get("/script.js", include_in_schema=False)
    def serve_js():
        return FileResponse(os.path.join(BASE_DIR, "script.js"), media_type="application/javascript")

if __name__ == "__main__":
    import uvicorn
    import socket
    port = int(os.environ.get("PORT", 5000))
    # Check if port is in use and fallback
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("127.0.0.1", port)) == 0:
            port = 5050
    print(f"Starting Todo REST API server at http://127.0.0.1:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
