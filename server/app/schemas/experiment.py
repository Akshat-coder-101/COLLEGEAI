from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class SimulateRequest(BaseModel):
    simulation_path: Optional[str] = "github_repo"  # "github_repo" or "built_model"
    repository_url: Optional[str] = None
    max_iterations: Optional[int] = 3


class ExperimentResponse(BaseModel):
    experiment_id: str
    hypothesis_id: str
    status: str
    simulation_path: str
    repository_url: Optional[str] = None
    current_iteration: int
    max_iterations: int
    created_at: datetime


class ExperimentStatusResponse(BaseModel):
    experiment_id: str
    status: str
    current_iteration: int
    max_iterations: int
    message: Optional[str] = None


class SimulationReportResponse(BaseModel):
    experiment_id: str
    status: str
    implementation_source: str
    code_tests: str  # passed, failed, not_evaluated
    model_verification: str  # verified, unverified, not_evaluated
    empirical_validation: str  # validated, unvalidated, not_evaluated
    iterations: int
    limitations: List[str] = []
    execution_logs: List[str] = []
    test_results: Dict[str, Any] = {}
    mathematical_equations: List[str] = []
    numerical_metrics: Dict[str, Any] = {}
