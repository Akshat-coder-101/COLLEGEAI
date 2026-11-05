import json
import logging
from typing import Dict, Any, List, Optional
from app.simulation.sandbox_service import SandboxService
from app.simulation.benchmark_service import IndependentBenchmarkService

logger = logging.getLogger(__name__)


class SimulationExecutionService:
    def __init__(self, sandbox: Optional[SandboxService] = None):
        self.sandbox = sandbox or SandboxService()
        self.benchmarks = IndependentBenchmarkService()

    def run_simulation(self, code_str: str) -> Dict[str, Any]:
        """
        Executes code in isolated sandbox and extracts JSON metrics if printed.
        """
        exec_res = self.sandbox.execute_python_code(code_str)

        logs = []
        if exec_res["stdout"]:
            logs.extend([line for line in exec_res["stdout"].splitlines() if line.strip()])
        if exec_res["stderr"]:
            logs.append(f"STDERR: {exec_res['stderr']}")

        # Parse metrics if emitted in stdout as JSON
        metrics = {}
        for line in reversed(logs):
            line_str = line.strip()
            if line_str.startswith("{") and line_str.endswith("}"):
                try:
                    metrics = json.loads(line_str)
                    break
                except Exception:
                    pass

        return {
            "success": exec_res["success"],
            "exit_code": exec_res["exit_code"],
            "logs": logs,
            "metrics": metrics,
            "stderr": exec_res["stderr"]
        }
