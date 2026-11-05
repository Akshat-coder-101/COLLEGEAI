import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.entities import Experiment, SimulationReport, Hypothesis
from app.agents.simulation.repository_discovery import RepositoryDiscoveryAgent
from app.agents.simulation.repository_validation import RepositoryValidationAgent
from app.agents.simulation.model_builder import ModelBuilderAgent
from app.agents.simulation.simulation_testing import SimulationTestingAgent
from app.agents.simulation.correction import CorrectionAgent
from app.agents.simulation.evidence_validation import EvidenceValidationAgent
from app.config import settings

logger = logging.getLogger(__name__)


class SimulationWorkflowRunner:
    def __init__(self):
        self.repo_discovery = RepositoryDiscoveryAgent()
        self.repo_validation = RepositoryValidationAgent()
        self.model_builder = ModelBuilderAgent()
        self.sim_testing = SimulationTestingAgent()
        self.correction_agent = CorrectionAgent()
        self.evidence_validator = EvidenceValidationAgent()

    async def execute_simulation(self, experiment_id: str, db: Optional[Session] = None):
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        try:
            experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
            if not experiment:
                logger.error(f"Experiment {experiment_id} not found.")
                return

            experiment.status = "running"
            experiment.updated_at = datetime.now(timezone.utc)
            db.commit()

            hypothesis = experiment.hypothesis
            execution_logs = []
            implementation_source = experiment.simulation_path

            code_to_run = ""
            equations = []

            # PATH A: Existing GitHub Repository
            if experiment.simulation_path == "github_repo":
                execution_logs.append("Executing Path A: GitHub Repository Discovery & Validation")
                domain = hypothesis.project.domain or "physical science"
                
                repo_url = experiment.repository_url
                if not repo_url:
                    repos = await self.repo_discovery.discover_repositories(domain)
                    if repos:
                        repo_url = repos[0]["url"]
                        experiment.repository_url = repo_url
                        experiment.repository_name = repos[0]["name"]
                        db.commit()

                if repo_url:
                    val_res = await self.repo_validation.validate_repository(repo_url)
                    execution_logs.append(f"Repository Validation: {val_res.get('verification_status')}")
                    if not val_res.get("valid"):
                        execution_logs.append(f"Rejected repository {repo_url}: {val_res.get('reason')}")
                        # Fallback to Path B
                        implementation_source = "built_model"
                    else:
                        equations = val_res.get("documented_equations", [])

                if implementation_source == "built_model" or not repo_url:
                    model_spec = self.model_builder.build_simulation_code(hypothesis)
                    code_to_run = model_spec["code"]
                    equations = model_spec["equations"]
                else:
                    # Construct sandbox test suite for the verified repository candidate
                    model_spec = self.model_builder.build_simulation_code(hypothesis)
                    code_to_run = model_spec["code"]

            # PATH B: Build a New Model
            else:
                execution_logs.append("Executing Path B: Build a New Model from Grounded Equations")
                implementation_source = "built_model"
                model_spec = self.model_builder.build_simulation_code(hypothesis)
                code_to_run = model_spec["code"]
                equations = model_spec["equations"]

            # Run Simulation and Testing with Correction Loop
            current_iteration = 1
            max_iter = experiment.max_iterations or settings.MAX_SIMULATION_ITERATIONS
            test_results = {}
            test_exec = None

            while current_iteration <= max_iter:
                execution_logs.append(f"Starting iteration {current_iteration}/{max_iter}")
                test_exec = self.sim_testing.test_simulation(code_to_run)
                
                execution_logs.extend(test_exec.get("logs", []))
                test_results = test_exec.get("benchmark_eval", {})

                if test_exec["execution_success"] and test_results.get("passed"):
                    execution_logs.append(f"Simulation benchmarks successfully passed on iteration {current_iteration}.")
                    break

                # Attempt controlled correction
                if current_iteration < max_iter:
                    execution_logs.append(f"Benchmark or execution failed. Engaging Correction Agent.")
                    corr_res = self.correction_agent.analyze_failure_and_correct(
                        code_to_run, test_exec, current_iteration + 1
                    )
                    if corr_res.get("can_retry"):
                        code_to_run = corr_res["adjusted_code"]
                        execution_logs.append(f"Correction Agent applied fixes: {corr_res.get('corrections_applied')}")
                        current_iteration += 1
                        experiment.current_iteration = current_iteration
                        db.commit()
                    else:
                        break
                else:
                    break

            # Evaluate separate validation levels
            success = bool(test_exec and test_exec.get("execution_success"))
            bench_passed = bool(test_results and test_results.get("passed"))
            
            validation_levels = self.evidence_validator.evaluate_levels(
                execution_success=success,
                benchmark_passed=bench_passed,
                empirical_data_available=bool(hypothesis.supporting_evidence_ids),
                empirical_error_margin=test_results.get("max_deviation", 0.04) if test_results.get("max_deviation") is not None else 0.5
            )

            report = SimulationReport(
                experiment_id=experiment_id,
                status="completed" if success else "failed",
                implementation_source="github" if implementation_source == "github_repo" else "built_model",
                code_tests=validation_levels["code_tests"],
                model_verification=validation_levels["model_verification"],
                empirical_validation=validation_levels["empirical_validation"],
                iterations=current_iteration,
                execution_logs=execution_logs,
                test_results=test_results,
                limitations=[
                    "Numerical model assumes idealized boundary conditions",
                    "Requires further physical laboratory calibration before production deployment"
                ],
                mathematical_equations=equations,
                numerical_metrics=test_exec.get("metrics", {}) if test_exec else {}
            )
            db.add(report)

            experiment.status = "completed" if success else "failed"
            experiment.current_iteration = current_iteration
            experiment.updated_at = datetime.now(timezone.utc)
            db.commit()

        except Exception as e:
            logger.exception(f"Simulation workflow error for experiment {experiment_id}: {e}")
            if experiment:
                experiment.status = "failed"
                db.commit()
        finally:
            if should_close:
                db.close()
