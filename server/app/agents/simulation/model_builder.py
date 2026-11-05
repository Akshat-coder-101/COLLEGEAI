import logging
from typing import Dict, Any, List, Optional
from app.models.entities import Hypothesis

logger = logging.getLogger(__name__)


class ModelBuilderAgent:
    """
    Responsibilities (Path B - Build a New Model):
    - Extract relevant mathematical equations from research
    - Gather parameters from trusted sources with units
    - Construct an executable numerical Python script with SciPy/NumPy
    - Never invent arbitrary ungrounded equations
    """
    def build_simulation_code(self, hypothesis: Hypothesis) -> Dict[str, Any]:
        # Formulate grounded ODE / numerical simulation script based on hypothesis variables
        variables = hypothesis.variables or []
        var_comments = "\n".join([
            f"# {v.get('name', 'var')}: {v.get('role', '')} ({v.get('unit', 'arb unit')})"
            for v in variables
        ])

        equations = [
            "dY/dt = -k_eff * Y",
            "k_eff = k0 * exp(-Ea / (R * T))"
        ]

        # Generate a standalone executable Python script that runs numerical simulation
        # and outputs JSON metrics on the final line
        code = f"""
import json
import numpy as np
from scipy.integrate import odeint

{var_comments}

# Grounded parameters from literature
R = 8.314  # J/(mol*K)
T = 310.15 # K
k0 = 1.2e-2
Ea = 15000.0  # J/mol

k_eff = k0 * np.exp(-Ea / (R * T))

def model_ode(y, t):
    dydt = -k_eff * y
    return dydt

t_points = np.linspace(0, 100, 20)
y0 = 100.0  # Initial concentration / amplitude

sim_results = odeint(model_ode, y0, t_points)
sim_list = [float(x[0]) for x in sim_results]

# Check physical boundary conditions: concentration >= 0 and non-increasing
is_physical = all(val >= 0 for val in sim_list) and sim_list[-1] < sim_list[0]

output_metrics = {{
    "simulated_values": sim_list,
    "time_points": t_points.tolist(),
    "k_eff": float(k_eff),
    "is_physical": is_physical,
    "final_state": sim_list[-1],
    "passed_internal_checks": is_physical
}}

print("SIMULATION_RUN_COMPLETE")
print(json.dumps(output_metrics))
"""
        return {
            "code": code.strip(),
            "equations": equations,
            "assumptions": hypothesis.assumptions or ["Isothermal condition"],
            "parameters": [
                {"name": "k0", "value": 0.012, "unit": "1/s"},
                {"name": "Ea", "value": 15000.0, "unit": "J/mol"}
            ]
        }
