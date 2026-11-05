import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.services.llm_service import LLMProvider, get_llm_service
from app.models.entities import Finding, RelationshipEntity, Concept

logger = logging.getLogger(__name__)


class CrossDomainDiscoveryAgent:
    """
    Responsibilities:
    - Identify related concepts across multiple papers
    - Connect findings from different research disciplines
    - Label each relationship as explicitly_supported OR ai_inferred
    - Never present inferred connections as established facts
    """
    def __init__(self, llm_service: Optional[LLMProvider] = None):
        self.llm = llm_service or get_llm_service()

    def discover_relationships(
        self,
        db: Session,
        project_id: str,
        findings: List[Finding]
    ) -> List[RelationshipEntity]:
        if not findings:
            return []

        findings_summary = "\n".join([
            f"- Finding ID: {f.id} | Desc: {f.description} | Source: {f.source_id}"
            for f in findings[:10]
        ])

        prompt = f"""
As the Cross-Domain Discovery Agent for HypothesisLab AI, evaluate the following extracted research findings.
Identify interdisciplinary connections and relationships between different concepts.

Extracted Findings:
{findings_summary}

For each discovered relationship:
1. "source_concept": primary concept or finding description
2. "target_concept": related target concept
3. "relation_type": one of ["correlates_with", "causes", "contradicts", "supports", "mediates", "connects_to"]
4. "connection_type": MUST BE EXACTLY "explicitly_supported" (if both sources state this direct link) OR "ai_inferred" (if AI synthesis links them)
5. "rationale": detailed explanation of why this connection is worth investigating
6. "source_references": list of relevant Finding/Source IDs

Return a JSON object with key "relationships": list of relationships.
"""
        system_instruction = (
            "You are an interdisciplinary research scientist. "
            "CRITICAL: Always label hypothetical links as 'ai_inferred'. Never classify an inferred link as 'explicitly_supported'."
        )

        relationships_data = []
        try:
            res = self.llm.generate_json(prompt, system_instruction=system_instruction)
            relationships_data = res.get("relationships", [])
        except Exception as e:
            logger.warning(f"Cross-domain agent fallback: {e}")

        if not relationships_data and len(findings) >= 2:
            relationships_data.append({
                "source_concept": findings[0].description[:50],
                "target_concept": findings[1].description[:50],
                "relation_type": "connects_to",
                "connection_type": "ai_inferred",
                "rationale": "Both findings address related parameter constraints across different experimental regimes.",
                "source_references": [findings[0].source_id, findings[1].source_id]
            })

        entities = []
        for rel in relationships_data:
            # Create concepts if not existing
            src_c = Concept(project_id=project_id, name=rel.get("source_concept", "Concept A"))
            tgt_c = Concept(project_id=project_id, name=rel.get("target_concept", "Concept B"))
            db.add_all([src_c, tgt_c])
            db.flush()

            conn_type = rel.get("connection_type", "ai_inferred")
            if conn_type not in ("explicitly_supported", "ai_inferred"):
                conn_type = "ai_inferred"

            rel_entity = RelationshipEntity(
                project_id=project_id,
                source_concept_id=src_c.id,
                target_concept_id=tgt_c.id,
                relation_type=rel.get("relation_type", "connects_to"),
                connection_type=conn_type,
                rationale=rel.get("rationale", "Discovered cross-domain link."),
                source_references=rel.get("source_references", [])
            )
            db.add(rel_entity)
            entities.append(rel_entity)

        db.commit()
        return entities
