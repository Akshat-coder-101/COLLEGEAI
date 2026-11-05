from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.entities import ResearchProject, ResearchGap, RelationshipEntity, Hypothesis, ReviewFeedback
from app.schemas.discovery import DiscoveriesResponse
from app.schemas.hypothesis import HypothesisDetail, HypothesisListResponse

router = APIRouter(tags=["Discoveries & Hypotheses"])


@router.get("/research/{project_id}/discoveries", response_model=DiscoveriesResponse)
def get_discoveries(project_id: str, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found")

    gaps = db.query(ResearchGap).filter(ResearchGap.project_id == project_id).all()
    relationships = db.query(RelationshipEntity).filter(RelationshipEntity.project_id == project_id).all()

    # Distinguish general gaps vs contradictions
    contradictions = [g for g in gaps if g.gap_type == "contradiction"]
    general_gaps = [g for g in gaps if g.gap_type != "contradiction"]

    return DiscoveriesResponse(
        project_id=project_id,
        gaps=[
            {
                "gap_id": g.id,
                "gap_type": g.gap_type,
                "title": g.title,
                "description": g.description,
                "why_it_matters": g.why_it_matters,
                "existing_coverage": g.existing_coverage,
                "remaining_uncertainty": g.remaining_uncertainty,
                "suggested_investigation": g.suggested_investigation,
                "supporting_sources": g.supporting_sources or []
            }
            for g in general_gaps
        ],
        relationships=[
            {
                "relationship_id": r.id,
                "source_concept": r.source_concept_id,
                "target_concept": r.target_concept_id,
                "relation_type": r.relation_type,
                "connection_type": r.connection_type,  # explicitly_supported OR ai_inferred
                "rationale": r.rationale,
                "source_references": r.source_references or []
            }
            for r in relationships
        ],
        contradictions=[
            {
                "gap_id": c.id,
                "title": c.title,
                "description": c.description,
                "why_it_matters": c.why_it_matters,
                "suggested_investigation": c.suggested_investigation,
                "supporting_sources": c.supporting_sources or []
            }
            for c in contradictions
        ]
    )


@router.get("/research/{project_id}/hypotheses", response_model=HypothesisListResponse)
def list_hypotheses(project_id: str, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found")

    hypotheses = db.query(Hypothesis).filter(Hypothesis.project_id == project_id).all()

    return HypothesisListResponse(
        project_id=project_id,
        hypotheses=[
            {
                "hypothesis_id": h.id,
                "title": h.title,
                "statement": h.statement,
                "motivation": h.motivation,
                "evidence": h.supporting_evidence_ids or [],
                "related_papers": h.related_paper_ids or [],
                "assumptions": h.assumptions or [],
                "variables": h.variables or [],
                "methodology": h.methodology or [],
                "experimental_design": h.experimental_design or {},
                "limitations": h.limitations_uncertainties or [],
                "suggested_next_steps": h.suggested_next_steps or [],
                "review_status": h.review_status
            }
            for h in hypotheses
        ]
    )


@router.get("/hypotheses/{hypothesis_id}", response_model=HypothesisDetail)
def get_hypothesis(hypothesis_id: str, db: Session = Depends(get_db)):
    hypo = db.query(Hypothesis).filter(Hypothesis.id == hypothesis_id).first()
    if not hypo:
        raise HTTPException(status_code=404, detail="Hypothesis not found")

    review = hypo.reviews[0] if hypo.reviews else None
    review_info = None
    if review:
        review_info = {
            "reviewer_agent": review.reviewer_agent,
            "evidence_soundness_score": review.evidence_soundness_score,
            "has_unsupported_assumptions": review.has_unsupported_assumptions,
            "unsupported_assumptions": review.unsupported_assumptions or [],
            "logical_consistency_score": review.logical_consistency_score,
            "logical_inconsistencies": review.logical_inconsistencies or [],
            "alternative_explanations": review.alternative_explanations or [],
            "testability_score": review.testability_score,
            "suggested_improvements": review.suggested_improvements or [],
            "verdict": review.verdict,
            "evaluation_summary": review.evaluation_summary
        }

    return HypothesisDetail(
        hypothesis_id=hypo.id,
        title=hypo.title,
        statement=hypo.statement,
        motivation=hypo.motivation,
        evidence=[{"id": eid} for eid in (hypo.supporting_evidence_ids or [])],
        related_papers=[{"id": pid} for pid in (hypo.related_paper_ids or [])],
        assumptions=hypo.assumptions or [],
        variables=hypo.variables or [],
        methodology=hypo.methodology or [],
        experimental_design=hypo.experimental_design or {},
        limitations=hypo.limitations_uncertainties or [],
        suggested_next_steps=hypo.suggested_next_steps or [],
        review_status=hypo.review_status,
        review_feedback=review_info,
        created_at=hypo.created_at
    )
