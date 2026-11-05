from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Project title")
    question: str = Field(..., min_length=3, description="Research question to investigate")
    domain: Optional[str] = Field(None, max_length=100, description="Optional scientific domain")


class ProjectResponse(BaseModel):
    id: str
    title: str
    question: str
    domain: Optional[str] = None
    status: str
    current_stage: Optional[str] = None
    progress: int
    status_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectStatusResponse(BaseModel):
    project_id: str
    status: str
    current_stage: Optional[str] = None
    progress: int
    message: Optional[str] = None


class FindingItem(BaseModel):
    finding_id: str
    description: str
    source_id: str
    document_location: Optional[str] = None
    supporting_quote: Optional[str] = None
    parameters: List[Dict[str, Any]] = []
    confidence: float
    extraction_status: str
    is_extracted: bool = True
    limitations: Optional[str] = None


class GapItem(BaseModel):
    gap_id: str
    gap_type: str
    title: str
    description: str
    why_it_matters: str
    existing_coverage: str
    remaining_uncertainty: str
    suggested_investigation: str
    supporting_sources: List[str] = []


class RelationshipItem(BaseModel):
    relationship_id: str
    source_concept: str
    target_concept: str
    relation_type: str
    connection_type: str  # explicitly_supported OR ai_inferred
    rationale: str
    source_references: List[str] = []


class HypothesisItem(BaseModel):
    hypothesis_id: str
    title: str
    statement: str
    motivation: str
    evidence: List[str] = []
    related_papers: List[str] = []
    assumptions: List[str] = []
    variables: List[Dict[str, Any]] = []
    methodology: List[str] = []
    limitations: List[str] = []
    review_status: str
    review_details: Optional[Dict[str, Any]] = None


class ProjectResultsResponse(BaseModel):
    project_id: str
    title: str
    question: str
    domain: Optional[str] = None
    status: str
    progress: int
    total_sources: int
    findings_count: int
    gaps_count: int
    hypotheses_count: int
    findings: List[FindingItem] = []
    gaps: List[GapItem] = []
    relationships: List[RelationshipItem] = []
    hypotheses: List[HypothesisItem] = []
