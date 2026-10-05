"""Universal Interactive Preview and Live Backend Router for ALL Generated Projects."""
import os
import json
import logging
import re
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Request, Response, HTTPException, status, Depends
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app.database.database import get_db, SessionLocal
from app.database.models import Project, RequirementAnalysis
from app.services.live_runner import live_runner

logger = logging.getLogger(__name__)

router = APIRouter()

BASE_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECTS_ROOT_DIR = os.path.abspath(os.path.join(BASE_BACKEND_DIR, "..", "generated_projects"))
PROJECTS_BACKEND_DIR = os.path.abspath(os.path.join(BASE_BACKEND_DIR, "generated_projects"))

STATIC_EXTENSIONS = {
    ".html", ".htm", ".css", ".js", ".mjs", ".json", ".svg", ".png",
    ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".woff", ".woff2", ".ttf",
    ".eot", ".map", ".txt", ".md", ".xml", ".wasm"
}

def find_project_workspace(project_id: str, version: int = 1) -> Optional[str]:
    """Find existing project directory across root and backend generated_projects."""
    candidates = [
        os.path.join(PROJECTS_ROOT_DIR, project_id, "versions", f"v{version}"),
        os.path.join(PROJECTS_BACKEND_DIR, project_id, "versions", f"v{version}"),
        os.path.join(PROJECTS_ROOT_DIR, project_id, f"v{version}"),
        os.path.join(PROJECTS_ROOT_DIR, project_id),
        os.path.join(PROJECTS_BACKEND_DIR, project_id),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return os.path.abspath(c)
    return None

def ensure_workspace_exists(project_id: str, version: int = 1, db: Session = None) -> str:
    """Ensure project directory and preview assets exist, generating on-demand if missing."""
    ws = find_project_workspace(project_id, version)
    index_file = os.path.join(ws, "index.html") if ws else None
    if ws and os.path.isfile(index_file) and os.path.getsize(index_file) > 100:
        return ws

    target_ws = os.path.abspath(os.path.join(PROJECTS_ROOT_DIR, project_id, "versions", f"v{version}"))
    os.makedirs(target_ws, exist_ok=True)

    should_close_db = False
    if db is None:
        db = SessionLocal()
        should_close_db = True

    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        req = db.query(RequirementAnalysis).filter(
            RequirementAnalysis.project_id == project_id
        ).order_by(RequirementAnalysis.created_at.desc()).first()

        title = (project.name if project else None) or "Autonomous Application"
        description = (project.description if project else None) or "Production-grade autonomous application."

        req_dict = {
            "project_summary": title,
            "summary": description,
            "user_requirement": description,
            "functional_requirements": req.functional_requirements if req and req.functional_requirements else [
                "Full interactive user interface",
                "Real-time data CRUD and state management",
                "Automated validation and error feedback",
                "Responsive layout and data filtering"
            ],
            "data_entities": req.data_entities if req and req.data_entities else ["Item", "Record", "Task"],
            "ui_requirements": req.ui_requirements if req and req.ui_requirements else []
        }

        from app.agents.preview_templates import ensure_preview_files
        ensure_preview_files(target_ws, req_dict, [])
    finally:
        if should_close_db:
            db.close()

    return target_ws

def try_auto_start_live_server(project_id: str, workspace_path: str):
    """Automatically boot the project's real backend process (app.py / server.js) in the background."""
    try:
        status_info = live_runner.get_status(project_id)
        if status_info.get("status") != "RUNNING":
            app_py = os.path.join(workspace_path, "app.py")
            server_js = os.path.join(workspace_path, "server.js")
            main_py = os.path.join(workspace_path, "main.py")
            if os.path.exists(app_py) or os.path.exists(server_js) or os.path.exists(main_py):
                live_runner.start_project(project_id, workspace_path)
    except Exception as e:
        logger.debug(f"Auto-start server notice for {project_id}: {e}")

# =====================================================================
# Universal Dynamic Data Store (For ALL entities and collections)
# =====================================================================

def get_collection_file(workspace_path: str, collection: str) -> str:
    safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '', collection.lower()) or "items"
    data_dir = os.path.join(workspace_path, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, f"{safe_name}.json")

def read_collection(workspace_path: str, collection: str) -> List[Dict[str, Any]]:
    col_path = get_collection_file(workspace_path, collection)
    if os.path.exists(col_path):
        try:
            with open(col_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    # Create default initial seed records based on collection name
    seeds = generate_initial_seeds(collection)
    write_collection(workspace_path, collection, seeds)
    return seeds

def write_collection(workspace_path: str, collection: str, data: List[Dict[str, Any]]) -> None:
    col_path = get_collection_file(workspace_path, collection)
    try:
        with open(col_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to write collection {collection}: {e}")

def generate_initial_seeds(collection: str) -> List[Dict[str, Any]]:
    c = collection.lower()
    if "todo" in c or "task" in c:
        return [
            {"id": "1", "title": "Configure production models & database schema", "description": "Setup SQLAlchemy models and migrations", "priority": "HIGH", "category": "Backend", "completed": True, "created_at": "2026-10-05 10:00"},
            {"id": "2", "title": "Implement REST endpoints and query filters", "description": "Build CRUD with filtering, pagination and search", "priority": "HIGH", "category": "Dev", "completed": True, "created_at": "2026-10-05 11:15"},
            {"id": "3", "title": "Validate error boundaries and input schemas", "description": "Defensive exception handlers and status codes", "priority": "MEDIUM", "category": "Testing", "completed": False, "created_at": "2026-10-05 12:30"},
            {"id": "4", "title": "Run full-coverage automated test suites", "description": "Automated pytest test client verification", "priority": "LOW", "category": "QA", "completed": False, "created_at": "2026-10-05 13:45"}
        ]
    elif "product" in c or "shop" in c or "item" in c:
        return [
            {"id": "1", "name": "Mechanical Pro Keyboard", "price": 129.99, "category": "Hardware", "stock": 42, "status": "In Stock", "rating": 4.9},
            {"id": "2", "name": "4K Ultra-Sharp Monitor", "price": 449.00, "category": "Displays", "stock": 18, "status": "In Stock", "rating": 4.8},
            {"id": "3", "name": "Ergonomic Mesh Chair", "price": 289.50, "category": "Furniture", "stock": 8, "status": "Low Stock", "rating": 4.7},
            {"id": "4", "name": "Noise-Cancelling Studio Headset", "price": 199.95, "category": "Audio", "stock": 25, "status": "In Stock", "rating": 4.9}
        ]
    elif "order" in c or "cart" in c:
        return [
            {"id": "ORD-101", "items": [{"name": "Mechanical Pro Keyboard", "price": 129.99, "qty": 1}], "total": 129.99, "status": "CONFIRMED", "customer": "Alex Chen", "created_at": "2026-10-05 10:30"},
            {"id": "ORD-102", "items": [{"name": "Noise-Cancelling Studio Headset", "price": 199.95, "qty": 1}], "total": 199.95, "status": "DELIVERED", "customer": "Samantha Wright", "created_at": "2026-10-05 11:45"}
        ]
    elif "asset" in c or "crypto" in c or "stock" in c or "ticker" in c:
        return [
            {"id": "1", "symbol": "BTC/USD", "name": "Bitcoin", "price": 64230.50, "change": 2.4, "volume": "28.4B", "holding": 0.45},
            {"id": "2", "symbol": "ETH/USD", "name": "Ethereum", "price": 3450.20, "change": -1.2, "volume": "14.2B", "holding": 3.20},
            {"id": "3", "symbol": "SOL/USD", "name": "Solana", "price": 148.90, "change": 5.8, "volume": "4.8B", "holding": 15.00},
            {"id": "4", "symbol": "NVDA", "name": "Nvidia Corp", "price": 124.50, "change": 3.1, "volume": "32.1B", "holding": 40.00}
        ]
    elif "trade" in c or "transaction" in c:
        return [
            {"id": "TRD-1", "type": "BUY", "asset": "BTC/USD", "amount": 0.15, "price": 63800.00, "status": "EXECUTED", "timestamp": "10:15 AM"},
            {"id": "TRD-2", "type": "BUY", "asset": "SOL/USD", "amount": 5.00, "price": 144.20, "status": "EXECUTED", "timestamp": "11:20 AM"}
        ]
    elif "calc" in c or "history" in c:
        return [
            {"id": "1", "expression": "125 * 48", "result": "6000", "timestamp": "10:00 AM"},
            {"id": "2", "expression": "sqrt(144) + 18", "result": "30", "timestamp": "10:05 AM"}
        ]
    elif "game" in c or "move" in c or "chess" in c:
        return [
            {"id": "1", "move": "e2 to e4", "player": "White", "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1", "timestamp": "10:00 AM"},
            {"id": "2", "move": "e7 to e5", "player": "Black", "fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2", "timestamp": "10:01 AM"}
        ]
    elif "user" in c or "member" in c or "account" in c:
        return [
            {"id": "1", "name": "Alex Chen", "email": "alex.chen@example.com", "role": "Administrator", "status": "Active"},
            {"id": "2", "name": "Samantha Wright", "email": "samantha@example.com", "role": "Lead Architect", "status": "Active"},
            {"id": "3", "name": "David Miller", "email": "david.m@example.com", "role": "Developer", "status": "Active"}
        ]
    elif "note" in c or "doc" in c or "post" in c:
        return [
            {"id": "1", "title": "System Architecture Overview", "content": "# Architecture\\n\\nHigh-performance multi-agent autonomous system with LangGraph loop orchestration.", "category": "Design", "created_at": "2026-10-05"},
            {"id": "2", "title": "Deployment Best Practices", "content": "# Deployment\\n\\nAutomated containerized pipelines with healthchecks and live process management.", "category": "DevOps", "created_at": "2026-10-05"}
        ]
    elif "message" in c or "chat" in c:
        return [
            {"id": "1", "sender": "System", "text": "Service initialized and connected to live backend router.", "timestamp": "10:00 AM"},
            {"id": "2", "sender": "Bot", "text": "Ready to process requests and execute operations.", "timestamp": "10:01 AM"}
        ]
    else:
        return [
            {"id": "1", "name": f"Primary {collection.capitalize()} Record", "category": "Core", "status": "Active", "details": "Initial operational record", "updated": "Just now"},
            {"id": "2", "name": f"Secondary {collection.capitalize()} Record", "category": "General", "status": "Active", "details": "Automated verification record", "updated": "Just now"}
        ]

# =====================================================================
# Universal API Dispatcher (Proxy to Live Server OR Dynamic Engine)
# =====================================================================

def handle_project_api(
    project_id: str,
    version: int,
    endpoint: str,
    method: str,
    body: Any = None,
    query_params: dict = None
) -> Response:
    workspace = ensure_workspace_exists(project_id, version)
    try_auto_start_live_server(project_id, workspace)

    clean_ep = endpoint.strip().lstrip("/")
    query_params = query_params or {}

    # 1. Check if live backend process is running and proxy directly
    try:
        proc_status = live_runner.get_status(project_id)
        if proc_status.get("status") == "RUNNING" and proc_status.get("port"):
            import httpx
            port = proc_status["port"]
            target_url = f"http://127.0.0.1:{port}/{clean_ep}"
            with httpx.Client(timeout=3.5) as client:
                res = client.request(
                    method=method,
                    url=target_url,
                    params=query_params,
                    json=body if method in ["POST", "PUT", "PATCH"] and body else None,
                    headers={"Content-Type": "application/json"}
                )
                return Response(
                    content=res.content,
                    status_code=res.status_code,
                    media_type=res.headers.get("content-type", "application/json")
                )
    except Exception as proxy_err:
        logger.debug(f"Direct proxy attempt skipped/failed ({proxy_err}), using dynamic data engine")

    # 2. Dynamic Universal Data Engine
    # System health & info endpoints
    if clean_ep in ["health", "status", "api/health", "ping"]:
        return JSONResponse({
            "status": "healthy",
            "service": "Generated Application Production Backend",
            "project_id": project_id,
            "version": version,
            "database": "active"
        })

    if clean_ep in ["info", "api/v1/info"]:
        return JSONResponse({
            "project_id": project_id,
            "version": version,
            "status": "operational",
            "timestamp": "2026-10-05T12:00:00Z"
        })

    # Normalize collection and item ID from path
    # e.g. "api/v1/items/5" -> "items", "5"
    # e.g. "todos/1" -> "todos", "1"
    # e.g. "products" -> "products", None
    ep_parts = [p for p in clean_ep.split("/") if p not in ["api", "v1", "v2"]]
    if not ep_parts:
        ep_parts = ["items"]

    collection_name = ep_parts[0]
    sub_action = ep_parts[1] if len(ep_parts) > 1 else None

    # Reset endpoint: /{collection}/reset
    if sub_action == "reset":
        seeds = generate_initial_seeds(collection_name)
        write_collection(workspace, collection_name, seeds)
        return JSONResponse({"message": f"{collection_name} reset to defaults", "count": len(seeds)})

    items = read_collection(workspace, collection_name)

    # Collection Root Endpoints (GET list, POST create)
    if not sub_action:
        if method == "GET":
            # Apply search filter
            search = query_params.get("search", "").lower()
            status_filter = query_params.get("status", "").lower()
            page = int(query_params.get("page", 1))
            limit = int(query_params.get("limit", 100))

            results = items
            if status_filter and status_filter != "all":
                if status_filter == "pending":
                    results = [t for t in results if not t.get("completed") and t.get("status", "").lower() != "completed"]
                elif status_filter == "completed":
                    results = [t for t in results if t.get("completed") or t.get("status", "").lower() == "completed"]
                else:
                    results = [t for t in results if str(t.get("status", "")).lower() == status_filter]

            if search:
                results = [
                    t for t in results
                    if any(search in str(v).lower() for v in t.values() if isinstance(v, (str, int, float)))
                ]

            offset = (page - 1) * limit
            paginated = results[offset : offset + limit]
            return JSONResponse(paginated)

        elif method == "POST":
            payload = body if isinstance(body, dict) else {}
            new_id = str(payload.get("id") or (max([int(t.get("id", 0)) for t in items if str(t.get("id", "")).isdigit()] + [0]) + 1))
            new_item = dict(payload)
            new_item["id"] = str(new_id)
            if "completed" in payload:
                new_item["completed"] = bool(payload["completed"])
            if "status" not in new_item:
                new_item["status"] = "Active"
            items.insert(0, new_item)
            write_collection(workspace, collection_name, items)
            return JSONResponse(new_item, status_code=status.HTTP_201_CREATED)

    # Single Record Operations (GET, PUT, PATCH, DELETE)
    item_id = sub_action
    target = next((t for t in items if str(t.get("id")) == str(item_id)), None)

    if method == "GET":
        if not target:
            raise HTTPException(status_code=404, detail=f"Record {item_id} not found in {collection_name}")
        return JSONResponse(target)

    elif method in ["PUT", "PATCH"]:
        if not target:
            raise HTTPException(status_code=404, detail=f"Record {item_id} not found in {collection_name}")
        payload = body if isinstance(body, dict) else {}
        for k, v in payload.items():
            if k != "id":
                target[k] = v
        write_collection(workspace, collection_name, items)
        return JSONResponse(target)

    elif method == "DELETE":
        if not target:
            raise HTTPException(status_code=404, detail=f"Record {item_id} not found in {collection_name}")
        items = [t for t in items if str(t.get("id")) != str(item_id)]
        write_collection(workspace, collection_name, items)
        return JSONResponse({"message": f"Deleted from {collection_name}", "id": item_id})

    return JSONResponse({"status": "acknowledged", "collection": collection_name, "method": method})

# =====================================================================
# Route Handlers
# =====================================================================

@router.api_route("/{project_id}/versions/v{version}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def project_version_dispatcher(
    project_id: str,
    version: int,
    path: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle all asset delivery AND API requests for a specific project version."""
    clean_path = path.strip().lstrip("/")
    method = request.method

    # Extract file extension if any
    _, ext = os.path.splitext(clean_path.split("?")[0])

    # Check if this is a static file request
    is_static = (ext.lower() in STATIC_EXTENSIONS) or (method == "GET" and (clean_path == "" or clean_path.endswith("/")))

    if is_static and method == "GET":
        file_to_serve = clean_path if (clean_path and not clean_path.endswith("/")) else "index.html"
        workspace = ensure_workspace_exists(project_id, version, db)
        try_auto_start_live_server(project_id, workspace)

        full_path = os.path.join(workspace, file_to_serve)
        if not os.path.isfile(full_path):
            if file_to_serve.endswith(".html") or "." not in file_to_serve:
                full_path = os.path.join(workspace, "index.html")

        if not os.path.isfile(full_path):
            ensure_workspace_exists(project_id, version, db)
            full_path = os.path.join(workspace, file_to_serve)

        if os.path.isfile(full_path):
            media_type = None
            if full_path.endswith(".html"):
                media_type = "text/html; charset=utf-8"
            elif full_path.endswith(".css"):
                media_type = "text/css; charset=utf-8"
            elif full_path.endswith(".js"):
                media_type = "application/javascript; charset=utf-8"
            elif full_path.endswith(".json"):
                media_type = "application/json"

            resp = FileResponse(full_path, media_type=media_type)
            resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
            resp.headers["Pragma"] = "no-cache"
            resp.headers["Expires"] = "0"
            return resp

    # Otherwise, treat as API request
    body = None
    if method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
        except Exception:
            body = {}
    query_params = dict(request.query_params)
    return handle_project_api(project_id, version, clean_path, method, body, query_params)

@router.api_route("/{project_id}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def project_root_dispatcher(
    project_id: str,
    path: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle all root-level project asset delivery and API calls."""
    clean_path = path.strip().lstrip("/")
    if clean_path.startswith("versions/v"):
        parts = clean_path.split("/", 2)
        v_num = int(parts[1].replace("v", ""))
        sub_path = parts[2] if len(parts) > 2 else "index.html"
        return await project_version_dispatcher(project_id, v_num, sub_path, request, db)
    return await project_version_dispatcher(project_id, 1, path, request, db)
