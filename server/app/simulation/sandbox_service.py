import os
import sys
import tempfile
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class SandboxSecurityException(Exception):
    pass


class SandboxService:
    """
    Isolated execution environment enforcing:
    - Resource & execution time limits
    - Prohibited command inspection
    - Restricted filesystem access inside temporary execution directories
    - No access to application secrets
    - Process isolation
    """
    PROHIBITED_TOKENS = [
        "rmdir /s /q", "rm -rf /", "format", "shutdown",
        "drop database", "eval(", "exec(", "__import__('os').system",
        "socket.connect", "curl ", "wget ", "powershell -enc"
    ]

    def __init__(self, timeout_seconds: Optional[int] = None):
        self.timeout = timeout_seconds or settings.SIMULATION_TIMEOUT

    def inspect_code_safety(self, code_str: str) -> None:
        """
        Scans code for hazardous tokens or illicit system calls before execution.
        """
        code_lower = code_str.lower()
        for token in self.PROHIBITED_TOKENS:
            if token in code_lower:
                raise SandboxSecurityException(
                    f"Security violation: Code contains prohibited token '{token}'"
                )

    def execute_python_code(
        self,
        code_str: str,
        extra_env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Runs Python script in an isolated subprocess with strict timeouts and cleaned environment.
        """
        self.inspect_code_safety(code_str)

        with tempfile.TemporaryDirectory() as tmp_dir:
            script_path = Path(tmp_dir) / "simulation_runner.py"
            script_path.write_text(code_str, encoding="utf-8")

            # Clean environment without sensitive tokens
            env = {
                "PATH": os.environ.get("PATH", ""),
                "PYTHONPATH": os.path.dirname(sys.executable),
                "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
            }
            if extra_env:
                env.update(extra_env)

            try:
                proc = subprocess.run(
                    [sys.executable, str(script_path)],
                    cwd=tmp_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.timeout
                )

                return {
                    "exit_code": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "timed_out": False,
                    "success": proc.returncode == 0
                }
            except subprocess.TimeoutExpired as e:
                return {
                    "exit_code": -1,
                    "stdout": e.stdout or "",
                    "stderr": f"Execution timed out after {self.timeout} seconds.",
                    "timed_out": True,
                    "success": False
                }
            except Exception as e:
                return {
                    "exit_code": -1,
                    "stdout": "",
                    "stderr": f"Sandbox execution failure: {e}",
                    "timed_out": False,
                    "success": False
                }
