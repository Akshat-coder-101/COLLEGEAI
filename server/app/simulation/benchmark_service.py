import numpy as np
from typing import Dict, Any, List


class IndependentBenchmarkService:
    """
    Maintains immutable scientific benchmark reference tests.
    CRITICAL: These reference tests must never be modified by the correction agent.
    """
    @staticmethod
    def get_reference_thermal_decay(initial_val: float, decay_rate: float, time_points: np.ndarray) -> np.ndarray:
        """
        Analytical solution for exponential decay: y(t) = y0 * exp(-k * t)
        """
        return initial_val * np.exp(-decay_rate * time_points)

    @staticmethod
    def evaluate_numerical_accuracy(simulated_values: List[float], reference_values: List[float], tolerance: float = 0.05) -> Dict[str, Any]:
        sim = np.array(simulated_values, dtype=float)
        ref = np.array(reference_values, dtype=float)

        if len(sim) != len(ref):
            return {
                "passed": False,
                "error": f"Dimension mismatch: simulated {len(sim)} vs reference {len(ref)}",
                "max_deviation": None,
                "mean_squared_error": None
            }

        abs_diff = np.abs(sim - ref)
        rel_diff = np.where(ref != 0, abs_diff / np.abs(ref), abs_diff)
        max_dev = float(np.max(rel_diff))
        mse = float(np.mean((sim - ref) ** 2))

        return {
            "passed": max_dev <= tolerance,
            "max_deviation": round(max_dev, 4),
            "mean_squared_error": round(mse, 6),
            "tolerance": tolerance,
            "reference_benchmark_immutable": True
        }
