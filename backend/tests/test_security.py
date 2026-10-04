import os
import pytest
from app.core.security import safe_join, scan_for_secrets

def test_safe_join_valid():
    base = "/opt/project/workspace"
    rel = "src/main.py"
    joined = safe_join(base, rel)
    assert joined.replace("\\", "/").endswith("/opt/project/workspace/src/main.py")

def test_safe_join_traversal():
    base = "/opt/project/workspace"
    rel = "../../etc/passwd"
    with pytest.raises(ValueError, match="Path traversal detected"):
        safe_join(base, rel)

def test_safe_join_absolute_injection():
    base = "/opt/project/workspace"
    rel = "/etc/passwd"
    joined = safe_join(base, rel)
    # The lstrip should turn /etc/passwd into etc/passwd and join it to base
    assert joined.replace("\\", "/").endswith("/opt/project/workspace/etc/passwd")

def test_scan_for_secrets():
    safe_code = "API_KEY = os.getenv('API_KEY')"
    assert len(scan_for_secrets(safe_code)) == 0
    
    leaked_code = "api_key = 'sk-12345678901234567890'"
    issues = scan_for_secrets(leaked_code)
    assert len(issues) > 0
    assert "sk-" in issues[0]
    
    aws_leak = 'AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"'
    issues = scan_for_secrets(aws_leak)
    assert len(issues) > 0
