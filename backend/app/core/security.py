import os
import re
from typing import List

# Patterns that may indicate secrets
SECRET_PATTERNS = [
    r"(?i)(api_key|secret_key|password|token|private_key)\s*=\s*['\"][^'\"]{8,}['\"]",
    r"(?i)(aws_access_key_id|aws_secret_access_key)\s*=\s*['\"][^'\"]{5,}['\"]",
    r"sk-[a-zA-Z0-9]{20,}",  # OpenAI-style keys
    r"nvapi-[a-zA-Z0-9\-_]{20,}",  # NVIDIA API keys
]

def safe_join(base_directory: str, relative_path: str) -> str:
    """
    Safely join a base directory with a relative path.
    Prevents path traversal, absolute path injection, and symlink escapes.
    Raises ValueError if the path attempts to escape the base directory.
    """
    # Normalize paths
    base_directory = os.path.abspath(base_directory)
    
    # Strip any leading slashes or drive letters from relative_path to prevent absolute path evaluation
    relative_path = relative_path.lstrip("/\\")
    if ":" in relative_path:
        relative_path = relative_path.split(":", 1)[1].lstrip("/\\")
    
    # Attempt to join
    final_path = os.path.abspath(os.path.join(base_directory, relative_path))
    
    # Verify the final path is strictly under the base directory
    if not final_path.startswith(base_directory + os.sep) and final_path != base_directory:
        raise ValueError(f"Path traversal detected. Cannot access '{relative_path}' outside of '{base_directory}'")
        
    return final_path

def scan_for_secrets(content: str) -> List[str]:
    """Check content for potential secret leakage."""
    found = []
    if not content:
        return found
        
    for pattern in SECRET_PATTERNS:
        for m in re.finditer(pattern, content):
            found.append(f"Secret detected: {m.group(0)} (pattern: '{pattern}')")
    return found
