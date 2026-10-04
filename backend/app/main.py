from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.router import api_router
from app.database.database import engine, Base
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Loop-Based Multi-Agent System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# Mount generated projects directory for live preview
generated_projects_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "generated_projects"
)
if not os.path.exists(generated_projects_path):
    os.makedirs(generated_projects_path)

app.mount("/projects", StaticFiles(directory=generated_projects_path), name="projects")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Loop-Based Multi-Agent System API"}
