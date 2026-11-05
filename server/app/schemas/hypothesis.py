from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class HypothesisDetail(BaseModel):
    hypothesis_id: str
    title: str
    statement: str
    motivation: str
    evidence: List[Dict[str, Any]] = []
    related_papers: List[Dict[str, Any]] = []
    assumptions: List[str] = []
    variables: List[Dict[str, Any]] = []
    methodology: List[str] = []
    experimental_design: Dict[str, Any] = {}
    limitations: List[str] = []
    suggested_next_steps: List[str] = []
    review_status: str
    review_feedback: Optional[Dict[str, Any]] = None
    created_at: datetime


class HypothesisListResponse(BaseModel):
    project_id: str
    hypotheses: List[Dict[str, Any]]
