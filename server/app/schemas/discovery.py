from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class DiscoveriesResponse(BaseModel):
    project_id: str
    gaps: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    contradictions: List[Dict[str, Any]]
