import pytest
from app.simulation.sandbox_service import SandboxService, SandboxSecurityException
from app.simulation.benchmark_service import IndependentBenchmarkService
from app.simulation.execution_service import SimulationExecutionService
from app.agents.simulation.repository_discovery import RepositoryDiscoveryAgent
from app.agents.simulation.repository_validation import RepositoryValidationAgent
from app.agents.simulation.model_builder import ModelBuilderAgent
from app.agents.simulation.correction import CorrectionAgent
from app.agents.simulation.evidence_validation import EvidenceValidationAgent
from app.models.entities import Hypothesis


def test_sandbox_security_rejection():
    sandbox = SandboxService()
    hazardous_codes = [
        "import os; os.system('rm -rf /')",
        "eval('__import__(\"os\").system(\"calc\")')",
        "import subprocess; subprocess.Popen(['powershell -enc', 'abc'])"
    ]

    for bad_code in hazardous_codes:
        with pytest.raises(SandboxSecurityException):
            sandbox.inspect_code_safety(bad_code)


def test_sandbox_safe_execution():
    sandbox = SandboxService(timeout_seconds=5)
    safe_code = """
import sys
print("SANDBOX_OK")
"""
    result = sandbox.execute_python_code(safe_code)
    assert result["success"] is True
    assert "SANDBOX_OK" in result["stdout"]


def test_independent_benchmark_accuracy():
    benchmarks = IndependentBenchmarkService()
    ref_values = [100.0, 90.48, 81.87, 74.08]
    
    # 1. Matching simulation
    good_sim = [100.0, 90.50, 81.90, 74.10]
    eval_good = benchmarks.evaluate_numerical_accuracy(good_sim, ref_values, tolerance=0.05)
    assert eval_good["passed"] is True
    assert eval_good["max_deviation"] <= 0.05

    # 2. Diverging simulation
    bad_sim = [100.0, 60.00, 30.00, 10.00]
    eval_bad = benchmarks.evaluate_numerical_accuracy(bad_sim, ref_values, tolerance=0.05)
    assert eval_bad["passed"] is False
    assert eval_bad["max_deviation"] > 0.05


@pytest.mark.asyncio
async def test_github_repository_discovery_and_validation():
    discovery = RepositoryDiscoveryAgent()
    repos = await discovery.discover_repositories("thermal dissipation")
    assert len(repos) >= 1
    assert "url" in repos[0]

    validation = RepositoryValidationAgent()
    val_res = await validation.validate_repository(repos[0]["url"])
    assert "valid" in val_res
    assert "can_execute" in val_res


def test_model_builder_and_simulation_execution():
    hypo = Hypothesis(
        title="Decay Hypothesis",
        statement="Concentration decays exponentially with rate k_eff.",
        motivation="Chemical degradation",
        variables=[
            {"name": "Concentration", "type": "dependent", "unit": "mol/L"},
            {"name": "Temperature", "type": "independent", "unit": "K"}
        ],
        assumptions=["Isothermal system"]
    )

    builder = ModelBuilderAgent()
    model_spec = builder.build_simulation_code(hypo)

    assert "code" in model_spec
    assert "dY/dt" in model_spec["equations"][0]

    exec_service = SimulationExecutionService()
    exec_res = exec_service.run_simulation(model_spec["code"])

    assert exec_res["success"] is True
    assert "simulated_values" in exec_res["metrics"]
    assert len(exec_res["metrics"]["simulated_values"]) > 0


def test_correction_agent_enforces_iteration_limit():
    agent = CorrectionAgent(max_iterations=3)
    sample_code = "print('Iteration test')"
    failure_report = {"stderr": "ValueError: mismatch", "benchmark_eval": {"passed": False, "max_deviation": 0.25}}

    # Iteration 1-3 allowed
    res1 = agent.analyze_failure_and_correct(sample_code, failure_report, iteration=2)
    assert res1["can_retry"] is True

    # Iteration exceeding max_iterations (4 > 3) rejected!
    res_exceeded = agent.analyze_failure_and_correct(sample_code, failure_report, iteration=4)
    assert res_exceeded["can_retry"] is False
    assert "exceeded" in res_exceeded["reason"].lower()


def test_correction_agent_protects_benchmark_integrity():
    agent = CorrectionAgent(max_iterations=3)
    tampered_code = "import benchmark\ntolerance = 1.0"
    failure_report = {"stderr": "mismatch", "benchmark_eval": {"passed": False}}

    with pytest.raises(RuntimeError) as exc_info:
        agent.analyze_failure_and_correct(tampered_code, failure_report, iteration=2)
    assert "Integrity violation" in str(exc_info.value)


def test_separate_simulation_validation_levels():
    # Scenario A: Code runs and benchmarks pass, but no empirical comparison data
    levels_a = EvidenceValidationAgent.evaluate_levels(
        execution_success=True,
        benchmark_passed=True,
        empirical_data_available=False
    )
    assert levels_a["code_tests"] == "passed"
    assert levels_a["model_verification"] == "verified"
    assert levels_a["empirical_validation"] == "not_evaluated"

    # Scenario B: Code fails to execute
    levels_b = EvidenceValidationAgent.evaluate_levels(
        execution_success=False,
        benchmark_passed=False,
        empirical_data_available=True
    )
    assert levels_b["code_tests"] == "failed"
    assert levels_b["model_verification"] == "not_evaluated"
    assert levels_b["empirical_validation"] == "not_evaluated"

    # Scenario C: Code passes, verified against benchmark, and calibrated with empirical data
    levels_c = EvidenceValidationAgent.evaluate_levels(
        execution_success=True,
        benchmark_passed=True,
        empirical_data_available=True,
        empirical_error_margin=0.04
    )
    assert levels_c["code_tests"] == "passed"
    assert levels_c["model_verification"] == "verified"
    assert levels_c["empirical_validation"] == "validated"
