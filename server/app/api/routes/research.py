import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.entities import ResearchProject, WorkflowExecution
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectStatusResponse,
    ProjectResultsResponse,
    FindingItem,
    GapItem,
    RelationshipItem,
    HypothesisItem,
)
from app.workflows.research_workflow import ResearchWorkflowRunner

router = APIRouter(tags=["Research Projects"])
workflow_runner = ResearchWorkflowRunner()


@router.post("/research", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = ResearchProject(
        title=payload.title,
        question=payload.question,
        domain=payload.domain,
        status="created",
        current_stage="initialized",
        progress=0,
        status_message="Project initialized. Ready for document upload or research run."
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/research", response_model=List[ProjectResponse])
def list_projects(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    projects = db.query(ResearchProject).offset(skip).limit(limit).all()
    return projects


@router.get("/research/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found")
    return project


@router.delete("/research/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found")
    db.delete(project)
    db.commit()
    return None


@router.post("/research/{project_id}/run", response_model=ProjectStatusResponse)
def run_research(
    project_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found")

    if project.status == "processing":
        return ProjectStatusResponse(
            project_id=project.id,
            status=project.status,
            current_stage=project.current_stage,
            progress=project.progress,
            message="Research workflow is already in progress"
        )

    project.status = "processing"
    project.current_stage = "planning"
    project.progress = 5
    project.status_message = "Research workflow started"
    db.commit()

    # Launch asynchronous background workflow execution
    background_tasks.add_task(workflow_runner.execute_workflow, project.id)

    return ProjectStatusResponse(
        project_id=project.id,
        status=project.status,
        current_stage=project.current_stage,
        progress=project.progress,
        message="Research workflow dispatched asynchronously"
    )


@router.get("/research/{project_id}/status", response_model=ProjectStatusResponse)
def get_project_status(project_id: str, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found")

    return ProjectStatusResponse(
        project_id=project.id,
        status=project.status,
        current_stage=project.current_stage,
        progress=project.progress,
        message=project.status_message
    )


@router.get("/research/{project_id}/results", response_model=ProjectResultsResponse)
def get_project_results(project_id: str, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found")

    findings = [
        FindingItem(
            finding_id=f.id,
            description=f.description,
            source_id=f.source_id,
            document_location=f.document_location,
            supporting_quote=f.supporting_quote,
            parameters=f.parameters or [],
            confidence=f.confidence,
            extraction_status=f.extraction_status,
            is_extracted=f.is_extracted,
            limitations=f.limitations
        )
        for f in project.findings
    ]

    gaps = [
        GapItem(
            gap_id=g.id,
            gap_type=g.gap_type,
            title=g.title,
            description=g.description,
            why_it_matters=g.why_it_matters,
            existing_coverage=g.existing_coverage,
            remaining_uncertainty=g.remaining_uncertainty,
            suggested_investigation=g.suggested_investigation,
            supporting_sources=g.supporting_sources or []
        )
        for g in project.gaps
    ]

    relationships = [
        RelationshipItem(
            relationship_id=r.id,
            source_concept=r.source_concept_id,
            target_concept=r.target_concept_id,
            relation_type=r.relation_type,
            connection_type=r.connection_type,
            rationale=r.rationale,
            source_references=r.source_references or []
        )
        for r in project.relationships_data
    ]

    hypotheses = [
        HypothesisItem(
            hypothesis_id=h.id,
            title=h.title,
            statement=h.statement,
            motivation=h.motivation,
            evidence=h.supporting_evidence_ids or [],
            related_papers=h.related_paper_ids or [],
            assumptions=h.assumptions or [],
            variables=h.variables or [],
            methodology=h.methodology or [],
            limitations=h.limitations_uncertainties or [],
            review_status=h.review_status,
            review_details={
                "verdict": h.reviews[0].verdict,
                "evidence_soundness_score": h.reviews[0].evidence_soundness_score,
                "testability_score": h.reviews[0].testability_score,
                "evaluation_summary": h.reviews[0].evaluation_summary
            } if h.reviews else None
        )
        for h in project.hypotheses
    ]

    return ProjectResultsResponse(
        project_id=project.id,
        title=project.title,
        question=project.question,
        domain=project.domain,
        status=project.status,
        progress=project.progress,
        total_sources=len(project.sources),
        findings_count=len(findings),
        gaps_count=len(gaps),
        hypotheses_count=len(hypotheses),
        findings=findings,
        gaps=gaps,
        relationships=relationships,
        hypotheses=hypotheses
    )
