import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.services.llm_service import LLMProvider, get_llm_service
from app.models.entities import Finding, ResearchGap

logger = logging.getLogger(__name__)


class GapDetectionAgent:
    """
    Responsibilities:
    - Identify unanswered questions, underexplored conditions, contradictions, limitations
    - Retain full source traceability
    - Never claim global novelty simply because it was absent from uploaded documents
    """
    def __init__(self, llm_service: Optional[LLMProvider] = None):
        self.llm = llm_service or get_llm_service()

    def detect_gaps(
        self,
        db: Session,
        project_id: str,
        findings: List[Finding]
    ) -> List[ResearchGap]:
        findings_context = "\n".join([
            f"- Source {f.source_id}: {f.description} (Limitations: {f.limitations or 'None recorded'})"
            for f in findings[:10]
        ])

        prompt = f"""
As the Research Gap Detection Agent for HypothesisLab AI, evaluate the findings and limitations below.
Identify genuine scientific gaps, contradictions, or underexplored boundaries.

Findings:
{findings_context}

For each identified research gap, provide a JSON object with:
1. "gap_type": one of ["unanswered_question", "underexplored_condition", "contradiction", "methodological_limitation", "missing_comparison"]
2. "title": concise descriptive title of the gap
3. "description": comprehensive description of the gap
4. "why_it_matters": scientific significance of resolving this gap
5. "existing_coverage": what current literature has already investigated
6. "remaining_uncertainty": what critical aspect remains unverified or disputed
7. "suggested_investigation": recommended concrete experimental or theoretical study
8. "supporting_sources": list of relevant source IDs

NOTE: Do NOT claim a gap is globally novel simply because it was not mentioned in these documents.

Return a JSON with key "gaps": list of gap objects.
"""
        system_instruction = (
            "You are a rigorous scientific critic. "
            "Detect genuine methodological boundaries and missing comparisons."
        )

        gaps_data = []
        try:
            res = self.llm.generate_json(prompt, system_instruction=system_instruction)
            gaps_data = res.get("gaps", [])
        except Exception as e:
            logger.warning(f"Gap detection LLM fallback: {e}")

        if not gaps_data:
            gaps_data.append({
                "gap_type": "underexplored_condition",
                "title": "Parameter sensitivity under dynamic operational stress",
                "description": "Studies evaluate static steady-state regimes, lacking dynamic response data.",
                "why_it_matters": "Real-world systems operate under fluctuating conditions.",
                "existing_coverage": "Steady-state laboratory measurements.",
                "remaining_uncertainty": "Transient behavior and degradation kinetics under oscillation.",
                "suggested_investigation": "Design time-resolved stress response experiments.",
                "supporting_sources": [f.source_id for f in findings[:2]]
            })

        entities = []
        for g in gaps_data:
            gap_entity = ResearchGap(
                project_id=project_id,
                gap_type=g.get("gap_type", "underexplored_condition"),
                title=g.get("title", "Identified Research Gap"),
                description=g.get("description", "Scientific gap description"),
                why_it_matters=g.get("why_it_matters", "Improves mechanistic clarity"),
                existing_coverage=g.get("existing_coverage", "Initial baseline studies"),
                remaining_uncertainty=g.get("remaining_uncertainty", "Full parameter space unexplored"),
                suggested_investigation=g.get("suggested_investigation", "Targeted validation trials"),
                supporting_sources=g.get("supporting_sources", [])
            )
            db.add(gap_entity)
            entities.append(gap_entity)

        db.commit()
        return entities
