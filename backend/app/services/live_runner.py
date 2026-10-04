import os
import sys
import time
import socket
import logging
import subprocess
import threading
from typing import Dict, Any, Optional, List
from collections import deque

logger = logging.getLogger(__name__)

class LiveRunnerService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LiveRunnerService, cls).__new__(cls)
                cls._instance._init()
            return cls._instance

    def _init(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.ports: Dict[str, int] = {}
        self.logs: Dict[str, deque] = {}
        self.start_times: Dict[str, float] = {}

    def _find_free_port(self, start_port: int = 8010, max_port: int = 8090) -> int:
        for port in range(start_port, max_port):
            if port in self.ports.values():
                continue
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                res = s.connect_ex(('127.0.0.1', port))
                if res != 0:
                    return port
        raise RuntimeError("No free port available in range for live project execution")

    def _stream_logs(self, project_id: str, process: subprocess.Popen):
        log_queue = self.logs.setdefault(project_id, deque(maxlen=200))
        try:
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                clean_line = line.strip()
                if clean_line:
                    log_queue.append(clean_line)
                    logger.debug(f"[{project_id}] {clean_line}")
        except Exception as e:
            log_queue.append(f"[LiveRunner Error reading stream: {e}]")

    def start_project(self, project_id: str, workspace_path: str) -> Dict[str, Any]:
        with self._lock:
            # If already running, return current status
            if project_id in self.processes:
                proc = self.processes[project_id]
                if proc.poll() is None:
                    port = self.ports.get(project_id, 8010)
                    return {
                        "status": "RUNNING",
                        "port": port,
                        "live_url": f"http://127.0.0.1:{port}",
                        "message": "Live application is already running",
                        "pid": proc.pid
                    }
                else:
                    self.stop_project(project_id)

            if not os.path.exists(workspace_path):
                raise ValueError(f"Workspace path does not exist: {workspace_path}")

            port = self._find_free_port()
            env = os.environ.copy()
            env["PORT"] = str(port)
            env["PYTHONUNBUFFERED"] = "1"
            env["HOST"] = "127.0.0.1"

            app_py = os.path.join(workspace_path, "app.py")
            main_py = os.path.join(workspace_path, "main.py")
            server_js = os.path.join(workspace_path, "server.js")
            index_html = os.path.join(workspace_path, "index.html")

            # Determine launch command
            python_executable = sys.executable
            cmd = None

            if os.path.exists(app_py):
                # Check if app.py uses uvicorn or standard python
                cmd = [python_executable, "-u", "app.py"]
            elif os.path.exists(main_py):
                cmd = [python_executable, "-u", "main.py"]
            elif os.path.exists(server_js):
                cmd = ["node", "server.js"]
            elif os.path.exists(index_html):
                # Fallback to python built-in http.server
                cmd = [python_executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"]
            else:
                raise ValueError("No runnable entrypoint (app.py, main.py, server.js, index.html) found in workspace")

            self.logs[project_id] = deque(maxlen=200)
            self.logs[project_id].append(f"[LiveRunner] Starting process: {' '.join(cmd)} on port {port}")

            try:
                proc = subprocess.Popen(
                    cmd,
                    cwd=workspace_path,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                self.processes[project_id] = proc
                self.ports[project_id] = port
                self.start_times[project_id] = time.time()

                # Start log listener thread
                thread = threading.Thread(
                    target=self._stream_logs,
                    args=(project_id, proc),
                    daemon=True
                )
                thread.start()

                # Brief wait to ensure process didn't crash instantly
                time.sleep(0.6)
                if proc.poll() is not None:
                    exit_code = proc.poll()
                    err_logs = list(self.logs.get(project_id, []))
                    raise RuntimeError(f"Live server failed on startup with exit code {exit_code}. Logs: {' | '.join(err_logs[-5:])}")

                return {
                    "status": "RUNNING",
                    "port": port,
                    "live_url": f"http://127.0.0.1:{port}",
                    "message": "Live real-time server started successfully",
                    "pid": proc.pid
                }

            except Exception as e:
                self.stop_project(project_id)
                raise RuntimeError(f"Failed to start live application: {e}")

    def stop_project(self, project_id: str) -> Dict[str, Any]:
        with self._lock:
            proc = self.processes.pop(project_id, None)
            port = self.ports.pop(project_id, None)
            self.start_times.pop(project_id, None)

            if proc:
                try:
                    proc.terminate()
                    proc.wait(timeout=2)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
                if project_id in self.logs:
                    self.logs[project_id].append("[LiveRunner] Process stopped.")
                return {"status": "STOPPED", "message": f"Server on port {port} stopped"}

            return {"status": "STOPPED", "message": "Server was not running"}

    def get_status(self, project_id: str) -> Dict[str, Any]:
        with self._lock:
            proc = self.processes.get(project_id)
            if proc and proc.poll() is None:
                port = self.ports.get(project_id)
                uptime = time.time() - self.start_times.get(project_id, time.time())
                return {
                    "status": "RUNNING",
                    "port": port,
                    "live_url": f"http://127.0.0.1:{port}",
                    "uptime_seconds": int(uptime),
                    "pid": proc.pid,
                    "logs": list(self.logs.get(project_id, []))[-30:]
                }
            elif proc and proc.poll() is not None:
                exit_code = proc.poll()
                self.processes.pop(project_id, None)
                self.ports.pop(project_id, None)
                return {
                    "status": "CRASHED",
                    "exit_code": exit_code,
                    "live_url": None,
                    "logs": list(self.logs.get(project_id, []))[-30:]
                }
            else:
                return {
                    "status": "STOPPED",
                    "live_url": None,
                    "port": None,
                    "logs": list(self.logs.get(project_id, []))[-30:]
                }

    def get_logs(self, project_id: str) -> List[str]:
        return list(self.logs.get(project_id, []))

live_runner = LiveRunnerService()
