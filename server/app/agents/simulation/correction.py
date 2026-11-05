import logging
import re
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class CorrectionAgent:
    """
    Responsibilities:
    - Analyze test failures and execution tracebacks
    - Propose controlled code adjustments
    - Enforce maximum iteration limit
    - NEVER tamper with independent reference tests to force passing
    """
    def __init__(self, max_iterations: Optional[int] = None):
        self.max_iterations = max_iterations or settings.MAX_SIMULATION_ITERATIONS

    def analyze_failure_and_correct(
        self,
        code_str: str,
        test_failure_report: Dict[str, Any],
        iteration: int
    ) -> Dict[str, Any]:
        if iteration > self.max_iterations:
            return {
                "can_retry": False,
                "reason": f"Maximum iteration limit ({self.max_iterations}) exceeded.",
                "adjusted_code": code_str
            }

        stderr = test_failure_report.get("stderr", "")
        benchmark_eval = test_failure_report.get("benchmark_eval", {})

        adjusted_code = code_str

        # Safe error remediation:
        # 1. Missing imports or NameErrors
        if "NameError: name 'np' is not defined" in stderr:
            adjusted_code = "import numpy as np\n" + adjusted_code
        elif "NameError: name 'odeint' is not defined" in stderr:
            adjusted_code = "from scipy.integrate import odeint\n" + adjusted_code

        # 2. Numerical divergence or negative concentrations
        if not benchmark_eval.get("passed") and benchmark_eval.get("max_deviation") and benchmark_eval["max_deviation"] > 0.05:
            # Adjust time stepping density to improve ODE convergence
            if "linspace(0, 100, 20)" in adjusted_code:
                adjusted_code = adjusted_code.replace("linspace(0, 100, 20)", "linspace(0, 100, 50)")

        # Verify that independent reference benchmarks were NOT tampered with
        if "benchmark" in adjusted_code.lower() and "tolerance = 1.0" in adjusted_code:
            raise RuntimeError("Integrity violation: Correction Agent attempted to alter reference benchmark criteria.")

        return {
            "can_retry": True,
            "iteration": iteration,
            "corrections_applied": ["Enhanced numerical integration resolution"],
            "adjusted_code": adjusted_code
        }
