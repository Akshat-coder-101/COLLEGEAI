import logging
import numpy as np
from typing import Dict, Any, List, Optional
from app.simulation.execution_service import SimulationExecutionService
from app.simulation.benchmark_service import IndependentBenchmarkService

logger = logging.getLogger(__name__)


class SimulationTestingAgent:
    """
    Responsibilities:
    - Execute the simulation code in the sandbox
    - Run independent reference benchmark comparisons
    - Record errors and numerical deviations
    """
    def __init__(self, execution_service: Optional[SimulationExecutionService] = None):
        self.exec_service = execution_service or SimulationExecutionService()
        self.benchmarks = IndependentBenchmarkService()

    def test_simulation(self, code_str: str) -> Dict[str, Any]:
        exec_result = self.exec_service.run_simulation(code_str)
        metrics = exec_result.get("metrics", {})
        simulated_values = metrics.get("simulated_values", [])

        benchmark_eval = {
            "passed": False,
            "max_deviation": None,
            "mean_squared_error": None
        }

        if exec_result["success"] and simulated_values:
            # Independent reference benchmark: analytical decay at matching time points
            t_points = np.array(metrics.get("time_points", np.linspace(0, 100, len(simulated_values))))
            k_eff = float(metrics.get("k_eff", 0.0036))
            reference_values = self.benchmarks.get_reference_thermal_decay(
                initial_val=simulated_values[0],
                decay_rate=k_eff,
                time_points=t_points
            ).tolist()

            benchmark_eval = self.benchmarks.evaluate_numerical_accuracy(
                simulated_values=simulated_values,
                reference_values=reference_values,
                tolerance=0.05
            )

        return {
            "execution_success": exec_result["success"],
            "exit_code": exec_result["exit_code"],
            "logs": exec_result["logs"],
            "metrics": metrics,
            "stderr": exec_result["stderr"],
            "benchmark_eval": benchmark_eval
        }
