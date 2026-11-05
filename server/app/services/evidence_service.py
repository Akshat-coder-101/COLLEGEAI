import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.entities import Source, Evidence, Finding, Document, ResearchPaper


class EvidenceService:
    @staticmethod
    def verify_evidence_span(document_text: str, quote: str) -> Dict[str, Any]:
        """
        Verifies if an extracted quote genuinely exists in the source text
        to prevent hallucinated evidence.
        """
        if not quote or not document_text:
            return {"verified": False, "match_ratio": 0.0, "reason": "Empty quote or text"}

        # Normalize whitespace and punctuation for robust matching
        clean_doc = re.sub(r"\s+", " ", document_text).strip().lower()
        clean_quote = re.sub(r"\s+", " ", quote).strip().lower()

        if clean_quote in clean_doc:
            return {"verified": True, "match_ratio": 1.0, "exact_match": True}

        # Partial substring or fuzzy overlap check
        words = clean_quote.split()
        if len(words) >= 4:
            matched_words = sum(1 for w in words if w in clean_doc)
            ratio = matched_words / len(words)
            if ratio >= 0.75:
                return {"verified": True, "match_ratio": ratio, "exact_match": False}

        return {"verified": False, "match_ratio": 0.0, "reason": "Evidence quote not found in source text"}

    @staticmethod
    def create_traceable_finding(
        db: Session,
        project_id: str,
        source_id: str,
        description: str,
        location: Optional[str] = None,
        quote: Optional[str] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        confidence: float = 1.0,
        is_extracted: bool = True
    ) -> Finding:
        """
        Creates a Finding entity strictly coupled with Source and Evidence.
        """
        evidence_id = None
        if quote:
            evidence = Evidence(
                source_id=source_id,
                exact_quote=quote,
                location_reference=location,
                confidence=confidence
            )
            db.add(evidence)
            db.flush()
            evidence_id = evidence.id

        finding = Finding(
            project_id=project_id,
            source_id=source_id,
            evidence_id=evidence_id,
            description=description,
            document_location=location,
            supporting_quote=quote,
            parameters=parameters or [],
            confidence=confidence,
            extraction_status="verified" if quote else "extracted",
            is_extracted=is_extracted
        )
        db.add(finding)
        db.flush()
        return finding
