import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, TypedDict
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, START, END

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


class SimulationGraphState(TypedDict, total=False):
    experiment_id: str
    hypothesis_id: str
    simulation_path: str
    repository_url: Optional[str]
    code_to_run: str
    equations: List[str]
    current_iteration: int
    max_iterations: int
    execution_logs: List[str]
    test_results: Dict[str, Any]
    test_exec: Dict[str, Any]
    status: str
    db: Any


class SimulationWorkflowRunner:
    def __init__(self):
        self.repo_discovery = RepositoryDiscoveryAgent()
        self.repo_validation = RepositoryValidationAgent()
        self.model_builder = ModelBuilderAgent()
        self.sim_testing = SimulationTestingAgent()
        self.correction_agent = CorrectionAgent()
        self.evidence_validator = EvidenceValidationAgent()
        self.graph = self._build_langgraph()

    def _build_langgraph(self):
        builder = StateGraph(SimulationGraphState)

        # 1. Setup Node (Path A vs Path B)
        async def setup_node(state: SimulationGraphState) -> Dict[str, Any]:
            db: Session = state["db"]
            exp = db.query(Experiment).filter(Experiment.id == state["experiment_id"]).first()
            hypo = exp.hypothesis if exp else None
            
            logs = list(state.get("execution_logs", []))
            sim_path = state.get("simulation_path", "github_repo")
            code_to_run = ""
            equations = []
            repo_url = state.get("repository_url")

            # Path A: GitHub
            if sim_path == "github_repo":
                logs.append("LangGraph: Inspecting GitHub simulation repository candidate")
                domain = (hypo.project.domain if hypo and hypo.project else None) or "computational science"
                if not repo_url:
                    repos = await self.repo_discovery.discover_repositories(domain)
                    if repos:
                        repo_url = repos[0]["url"]
                        if exp:
                            exp.repository_url = repo_url
                            exp.repository_name = repos[0]["name"]
                            db.commit()

                val_res = await self.repo_validation.validate_repository(repo_url) if repo_url else {"valid": False}
                if val_res.get("valid"):
                    equations = val_res.get("documented_equations", [])
                    logs.append(f"LangGraph: Validated repository {repo_url}")
                else:
                    logs.append("LangGraph: Falling back to grounded model builder")

                spec = self.model_builder.build_simulation_code(hypo)
                code_to_run = spec["code"]
                if not equations:
                    equations = spec["equations"]

            # Path B: Model Builder
            else:
                logs.append("LangGraph: Building grounded numerical ODE simulation model")
                spec = self.model_builder.build_simulation_code(hypo)
                code_to_run = spec["code"]
                equations = spec["equations"]

            return {
                "code_to_run": code_to_run,
                "equations": equations,
                "execution_logs": logs,
                "current_iteration": 1
            }

        # 2. Test Execution Node
        async def test_node(state: SimulationGraphState) -> Dict[str, Any]:
            curr_iter = state.get("current_iteration", 1)
            max_iter = state.get("max_iterations", 3)
            logs = list(state.get("execution_logs", []))
            logs.append(f"LangGraph: Running simulation iteration {curr_iter}/{max_iter}")

            test_exec = self.sim_testing.test_simulation(state["code_to_run"])
            logs.extend(test_exec.get("logs", []))
            test_results = test_exec.get("benchmark_eval", {})

            return {
                "test_exec": test_exec,
                "test_results": test_results,
                "execution_logs": logs
            }

        # 3. Correction Node
        async def correction_node(state: SimulationGraphState) -> Dict[str, Any]:
            logs = list(state.get("execution_logs", []))
            curr_iter = state.get("current_iteration", 1)
            next_iter = curr_iter + 1

            logs.append(f"LangGraph: Benchmark threshold unmet. Engaging correction loop (iteration {next_iter})")
            corr = self.correction_agent.analyze_failure_and_correct(
                state["code_to_run"], state["test_exec"], next_iter
            )

            new_code = corr.get("adjusted_code", state["code_to_run"])
            db: Session = state["db"]
            exp = db.query(Experiment).filter(Experiment.id == state["experiment_id"]).first()
            if exp:
                exp.current_iteration = next_iter
                db.commit()

            return {
                "code_to_run": new_code,
                "current_iteration": next_iter,
                "execution_logs": logs
            }

        # 4. Report Node
        async def report_node(state: SimulationGraphState) -> Dict[str, Any]:
            db: Session = state["db"]
            test_exec = state.get("test_exec", {})
            test_results = state.get("test_results", {})
            success = bool(test_exec and test_exec.get("execution_success"))
            bench_passed = bool(test_results and test_results.get("passed"))

            exp = db.query(Experiment).filter(Experiment.id == state["experiment_id"]).first()
            hypo = exp.hypothesis if exp else None

            validation_levels = self.evidence_validator.evaluate_levels(
                execution_success=success,
                benchmark_passed=bench_passed,
                empirical_data_available=bool(hypo and hypo.supporting_evidence_ids),
                empirical_error_margin=test_results.get("max_deviation", 0.04) if test_results.get("max_deviation") is not None else 0.5
            )

            report = SimulationReport(
                experiment_id=state["experiment_id"],
                status="completed" if success else "failed",
                implementation_source="github" if state.get("simulation_path") == "github_repo" else "built_model",
                code_tests=validation_levels["code_tests"],
                model_verification=validation_levels["model_verification"],
                empirical_validation=validation_levels["empirical_validation"],
                iterations=state.get("current_iteration", 1),
                execution_logs=state.get("execution_logs", []),
                test_results=test_results,
                limitations=[
                    "Assumes idealized boundary conditions",
                    "Requires physical in vitro calibration"
                ],
                mathematical_equations=state.get("equations", []),
                numerical_metrics=test_exec.get("metrics", {})
            )
            db.add(report)

            if exp:
                exp.status = "completed" if success else "failed"
                exp.updated_at = datetime.now(timezone.utc)
                db.commit()

            return {"status": "completed" if success else "failed"}

        # Conditional Edge Routing
        def route_after_test(state: SimulationGraphState) -> str:
            test_exec = state.get("test_exec", {})
            test_results = state.get("test_results", {})
            curr_iter = state.get("current_iteration", 1)
            max_iter = state.get("max_iterations", 3)

            if test_exec.get("execution_success") and test_results.get("passed"):
                return "report"
            elif curr_iter < max_iter:
                return "correct"
            else:
                return "report"

        builder.add_node("setup", setup_node)
        builder.add_node("test", test_node)
        builder.add_node("correct", correction_node)
        builder.add_node("report", report_node)

        builder.add_edge(START, "setup")
        builder.add_edge("setup", "test")
        builder.add_conditional_edges("test", route_after_test, {
            "correct": "correct",
            "report": "report"
        })
        builder.add_edge("correct", "test")
        builder.add_edge("report", END)

        return builder.compile()

    async def execute_simulation(self, experiment_id: str, db: Optional[Session] = None):
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True

        try:
            exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
            if not exp:
                logger.error(f"Experiment {experiment_id} not found.")
                return

            exp.status = "running"
            exp.updated_at = datetime.now(timezone.utc)
            db.commit()

            initial_state: SimulationGraphState = {
                "experiment_id": experiment_id,
                "hypothesis_id": exp.hypothesis_id,
                "simulation_path": exp.simulation_path,
                "repository_url": exp.repository_url,
                "max_iterations": exp.max_iterations or settings.MAX_SIMULATION_ITERATIONS,
                "execution_logs": [],
                "db": db
            }

            await self.graph.ainvoke(initial_state)

        except Exception as e:
            logger.exception(f"LangGraph simulation failure: {e}")
            if exp:
                exp.status = "failed"
                db.commit()
        finally:
            if should_close:
                db.close()
