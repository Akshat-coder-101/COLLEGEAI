from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.entities import Hypothesis, Experiment, SimulationReport
from app.schemas.experiment import (
    SimulateRequest,
    ExperimentResponse,
    ExperimentStatusResponse,
    SimulationReportResponse,
)
from app.workflows.simulation_workflow import SimulationWorkflowRunner
from app.config import settings

router = APIRouter(tags=["Simulation & Experiments"])
simulation_runner = SimulationWorkflowRunner()


@router.post("/hypotheses/{hypothesis_id}/simulate", response_model=ExperimentResponse, status_code=status.HTTP_202_ACCEPTED)
def start_simulation(
    hypothesis_id: str,
    payload: SimulateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    hypo = db.query(Hypothesis).filter(Hypothesis.id == hypothesis_id).first()
    if not hypo:
        raise HTTPException(status_code=404, detail="Hypothesis not found")

    sim_path = payload.simulation_path or "github_repo"
    if sim_path not in ("github_repo", "built_model"):
        sim_path = "github_repo"

    experiment = Experiment(
        hypothesis_id=hypothesis_id,
        status="running",
        simulation_path=sim_path,
        repository_url=payload.repository_url,
        current_iteration=1,
        max_iterations=payload.max_iterations or settings.MAX_SIMULATION_ITERATIONS
    )
    db.add(experiment)
    db.commit()
    db.refresh(experiment)

    # Launch asynchronous background simulation workflow
    background_tasks.add_task(simulation_runner.execute_simulation, experiment.id)

    return ExperimentResponse(
        experiment_id=experiment.id,
        hypothesis_id=experiment.hypothesis_id,
        status=experiment.status,
        simulation_path=experiment.simulation_path,
        repository_url=experiment.repository_url,
        current_iteration=experiment.current_iteration,
        max_iterations=experiment.max_iterations,
        created_at=experiment.created_at
    )


@router.get("/experiments/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(experiment_id: str, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return ExperimentResponse(
        experiment_id=exp.id,
        hypothesis_id=exp.hypothesis_id,
        status=exp.status,
        simulation_path=exp.simulation_path,
        repository_url=exp.repository_url,
        current_iteration=exp.current_iteration,
        max_iterations=exp.max_iterations,
        created_at=exp.created_at
    )


@router.get("/experiments/{experiment_id}/status", response_model=ExperimentStatusResponse)
def get_experiment_status(experiment_id: str, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    msg = f"Experiment is {exp.status} (Iteration {exp.current_iteration}/{exp.max_iterations})"
    return ExperimentStatusResponse(
        experiment_id=exp.id,
        status=exp.status,
        current_iteration=exp.current_iteration,
        max_iterations=exp.max_iterations,
        message=msg
    )


@router.post("/experiments/{experiment_id}/retry", response_model=ExperimentStatusResponse)
def retry_experiment(
    experiment_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if exp.current_iteration >= exp.max_iterations:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot retry: maximum permitted correction iterations ({exp.max_iterations}) already reached."
        )

    exp.status = "retrying"
    exp.current_iteration += 1
    db.commit()

    background_tasks.add_task(simulation_runner.execute_simulation, exp.id)

    return ExperimentStatusResponse(
        experiment_id=exp.id,
        status=exp.status,
        current_iteration=exp.current_iteration,
        max_iterations=exp.max_iterations,
        message=f"Retrying experiment with iteration {exp.current_iteration}/{exp.max_iterations}"
    )


@router.get("/experiments/{experiment_id}/report", response_model=SimulationReportResponse)
def get_simulation_report(experiment_id: str, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    report = exp.reports[0] if exp.reports else None
    if not report:
        raise HTTPException(
            status_code=404,
            detail="Simulation report not yet generated. Experiment may still be executing."
        )

    return SimulationReportResponse(
        experiment_id=report.experiment_id,
        status=report.status,
        implementation_source=report.implementation_source,
        code_tests=report.code_tests,
        model_verification=report.model_verification,
        empirical_validation=report.empirical_validation,
        iterations=report.iterations,
        limitations=report.limitations or [],
        execution_logs=report.execution_logs or [],
        test_results=report.test_results or {},
        mathematical_equations=report.mathematical_equations or [],
        numerical_metrics=report.numerical_metrics or {}
    )
