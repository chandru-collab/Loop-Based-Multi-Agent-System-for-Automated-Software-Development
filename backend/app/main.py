from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.router import api_router
from app.database.database import engine, Base
import os

# Create database tables and ensure schema integrity
Base.metadata.create_all(bind=engine)
try:
    with engine.connect() as conn:
        from sqlalchemy import text
        conn.execute(text("ALTER TABLE review_results ADD COLUMN confidence_score FLOAT"))
        conn.commit()
except Exception:
    pass # Column already exists or table freshly created

app = FastAPI(title="Loop-Based Multi-Agent System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.routes import project_preview

app.include_router(api_router, prefix="/api")
app.include_router(project_preview.router, prefix="/projects", tags=["project_preview"])

# Mount generated projects directory as fallback static files
generated_projects_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "generated_projects"
)
if not os.path.exists(generated_projects_path):
    os.makedirs(generated_projects_path)

class NoCacheStaticFiles(StaticFiles):
    """StaticFiles handler that disables HTTP caching so live preview always serves fresh files."""
    def is_not_modified(self, response_headers, request_headers) -> bool:
        return False

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

app.mount("/projects-static", NoCacheStaticFiles(directory=generated_projects_path), name="projects_static")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Loop-Based Multi-Agent System API"}
