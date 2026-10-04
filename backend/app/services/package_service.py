import os
import io
import re
import zipfile
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Files/patterns to exclude from ZIP
EXCLUDE_PATTERNS = [
    ".env",
    ".env.local",
    ".env.production",
    "*.pyc",
    "__pycache__",
    "venv",
    ".venv",
    "node_modules",
    ".git",
    ".pytest_cache",
    "*.log",
    "*.db",
    "*.sqlite",
    "*.sqlite3",
    "dist",
    "build",
    ".DS_Store",
    "Thumbs.db",
]

from app.core.security import scan_for_secrets

class PackageService:
    def __init__(self):
        self.base_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "generated_projects"
        ))

    def _should_exclude(self, path: str) -> bool:
        """Check if a file should be excluded from the ZIP."""
        basename = os.path.basename(path)
        parts = path.replace("\\", "/").split("/")

        for pattern in EXCLUDE_PATTERNS:
            if pattern.startswith("*"):
                ext = pattern[1:]
                if basename.endswith(ext):
                    return True
            elif pattern in parts or pattern == basename:
                return True
        return False



    def _scan_for_secrets(self, workspace_path: str) -> List[str]:
        """Scan all files for secrets before packaging."""
        issues = []
        for root, dirs, files in os.walk(workspace_path):
            dirs[:] = [d for d in dirs if not self._should_exclude(d)]
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, workspace_path)
                if self._should_exclude(rel_path):
                    continue
                if file.endswith((".py", ".js", ".ts", ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini")):
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        secrets = scan_for_secrets(content)
                        if secrets:
                            issues.extend([f"{rel_path}: {s}" for s in secrets])
                    except Exception:
                        pass
        return issues

    def create_package(self, project_id: str, version: int) -> Dict[str, Any]:
        """Create the final ZIP package for an approved version."""
        workspace_path = os.path.join(
            self.base_dir, project_id, "versions", f"v{version}"
        )
        if not os.path.exists(workspace_path):
            # Preserve compatibility with workspaces created relative to the backend cwd.
            workspace_path = os.path.abspath(os.path.join(
                "generated_projects", project_id, "versions", f"v{version}"
            ))
        packages_dir = os.path.join(self.base_dir, project_id, "packages")
        os.makedirs(packages_dir, exist_ok=True)

        package_filename = f"{project_id}_v{version}_final.zip"
        package_path = os.path.join(packages_dir, package_filename)

        if not os.path.exists(workspace_path):
            raise FileNotFoundError(f"Workspace not found: {workspace_path}")

        # Scan for secrets
        secret_issues = self._scan_for_secrets(workspace_path)
        if secret_issues:
            raise ValueError(f"Packaging aborted - potential secrets detected:\n" + "\n".join(secret_issues[:10]))

        # Create ZIP directly on disk
        with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(workspace_path):
                dirs[:] = [d for d in dirs if not self._should_exclude(d)]
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, workspace_path)
                    if self._should_exclude(rel_path):
                        continue
                        
                    normalized_rel_path = rel_path.replace("\\", "/")
                    is_document = (
                        normalized_rel_path.lower() == "readme.md" or 
                        normalized_rel_path.startswith("docs/")
                    )
                    
                    if is_document:
                        arcname = os.path.join(f"v{version}", "document", rel_path)
                    else:
                        arcname = os.path.join(f"v{version}", "code", rel_path)
                        
                    try:
                        zf.write(full_path, arcname)
                    except Exception as e:
                        logger.warning(f"Skipping file {rel_path}: {e}")

        # Calculate checksum and size directly from the written file
        sha256_hash = hashlib.sha256()
        size = 0
        with open(package_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
                size += len(byte_block)
        
        sha256 = sha256_hash.hexdigest()

        logger.info(f"Package created: {package_filename} ({size} bytes, sha256={sha256[:16]}...)")

        return {
            "package_path": package_path,
            "package_filename": package_filename,
            "package_size": size,
            "checksum_sha256": sha256,
            "created_at": datetime.utcnow().isoformat()
        }
