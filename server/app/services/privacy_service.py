import re
import hashlib
from typing import Dict, Any, List, Tuple, Optional

class PrivacyService:
    """
    HypothesisLab AI — Research Privacy & Confidential IP Shield Layer.
    
    Protects confidential research papers, unpublished patent data, proprietary chemical/
    biological compounds, and researcher PII from leakage to external AI endpoints or logs.
    """

    # Core Regex Patterns for Sensitive Research Information
    EMAIL_PATTERN = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
    
    # Patent references & grant numbers (e.g. US Patent Application 17/984,231 or WO 2024/10492)
    PATENT_PATTERN = re.compile(
        r'\b(?:US|EP|WO|PCT|CN|JP)[\s-]*(?:Patent|Application|Publication|Pub\.?|App\.?|\s)*[\s-]*#?[\d,/-]{4,}\b',
        re.IGNORECASE
    )
    GRANT_PATTERN = re.compile(
        r'\b(?:NIH|NSF|DARPA|ERC|DOE|DOD|HHS)[\s-]*(?:Grant|Award|Contract)?[\s-]*#?([A-Za-z0-9_-]{5,})\b',
        re.IGNORECASE
    )

    # Proprietary compound, molecular, or trial identifiers (e.g. Compound-X99, BMS-986165, Compound 4b)
    COMPOUND_ID_PATTERN = re.compile(
        r'\b(?:Compound|Molecule|Batch|Inhibitor|Candidate|Agonist|Antagonist|Variant)[-\s]+([A-Za-z0-9_-]+)\b',
        re.IGNORECASE
    )
    GENERIC_CODE_PATTERN = re.compile(
        r'\b([A-Z]{2,4}-[0-9]{3,6}(?:-[A-Z0-9]+)?)\b'
    )

    # Confidentiality markings
    CONFIDENTIAL_WATERMARK_PATTERN = re.compile(
        r'\b(?:CONFIDENTIAL|STRICTLY PROPRIETARY|TRADE SECRET|DO NOT DISTRIBUTE|INTERNAL USE ONLY|DRAFT - NOT FOR CITATION)\b',
        re.IGNORECASE
    )

    # Institutional affiliation headers
    AFFILIATION_PATTERN = re.compile(
        r'\b(?:Department of|School of|Institute of|Faculty of|Laboratory of|Center for)\s+[A-Za-z\s,]+(?:University|Institute|Hospital|Foundation|Inc\.|Corp\.|Ltd\.)',
        re.IGNORECASE
    )

    @classmethod
    def sanitize_research_text(cls, text: str, preserve_structure: bool = True) -> Tuple[str, Dict[str, Any]]:
        """
        Scans and sanitizes confidential research text, replacing sensitive entities
        with structured pseudonym tokens before LLM analysis.
        """
        if not text:
            return "", {"redacted_count": 0, "categories": {}}

        audit = {
            "emails": 0,
            "phones": 0,
            "patents": 0,
            "grants": 0,
            "compounds": 0,
            "confidential_markers": 0,
            "affiliations": 0,
            "total_redactions": 0
        }

        sanitized = text

        # 1. Confidentiality headers & watermarks
        markers = cls.CONFIDENTIAL_WATERMARK_PATTERN.findall(sanitized)
        if markers:
            audit["confidential_markers"] += len(markers)
            sanitized = cls.CONFIDENTIAL_WATERMARK_PATTERN.sub("[CONFIDENTIAL_NOTICE_REDACTED]", sanitized)

        # 2. Email addresses
        emails = cls.EMAIL_PATTERN.findall(sanitized)
        if emails:
            audit["emails"] += len(emails)
            sanitized = cls.EMAIL_PATTERN.sub("[EMAIL_REDACTED]", sanitized)

        # 3. Phone numbers
        phones = cls.PHONE_PATTERN.findall(sanitized)
        if phones:
            audit["phones"] += len(phones)
            sanitized = cls.PHONE_PATTERN.sub("[PHONE_REDACTED]", sanitized)

        # 4. Patent citations
        patents = cls.PATENT_PATTERN.findall(sanitized)
        if patents:
            audit["patents"] += len(patents)
            sanitized = cls.PATENT_PATTERN.sub("[PATENT_REF_REDACTED]", sanitized)

        # 5. Grant numbers
        grants = cls.GRANT_PATTERN.findall(sanitized)
        if grants:
            audit["grants"] += len(grants)
            sanitized = cls.GRANT_PATTERN.sub("[GRANT_REF_REDACTED]", sanitized)

        # 6. Proprietary compound codes
        compounds = cls.COMPOUND_ID_PATTERN.findall(sanitized)
        if compounds:
            audit["compounds"] += len(compounds)
            sanitized = cls.COMPOUND_ID_PATTERN.sub("[CONFIDENTIAL_COMPOUND_ID]", sanitized)

        generic_codes = cls.GENERIC_CODE_PATTERN.findall(sanitized)
        if generic_codes:
            audit["compounds"] += len(generic_codes)
            sanitized = cls.GENERIC_CODE_PATTERN.sub("[PROPRIETARY_CODE_ID]", sanitized)

        # 7. Affiliations
        affiliations = cls.AFFILIATION_PATTERN.findall(sanitized)
        if affiliations:
            audit["affiliations"] += len(affiliations)
            sanitized = cls.AFFILIATION_PATTERN.sub("[ACADEMIC_INSTITUTION_REDACTED]", sanitized)

        audit["total_redactions"] = sum(
            v for k, v in audit.items() if k != "total_redactions"
        )
        audit["privacy_shield_active"] = True
        audit["sha256_hash"] = hashlib.sha256(sanitized.encode("utf-8")).hexdigest()

        return sanitized, audit

    @classmethod
    def sanitize_external_search_query(cls, query: str) -> str:
        """
        Ensures search queries passed to external literature search providers (arXiv, CrossRef)
        do not leak internal proprietary codenames, patent numbers, or confidential markers.
        """
        clean = cls.CONFIDENTIAL_WATERMARK_PATTERN.sub("", query)
        clean = cls.PATENT_PATTERN.sub("", clean)
        clean = cls.EMAIL_PATTERN.sub("", clean)
        clean = cls.COMPOUND_ID_PATTERN.sub("", clean)
        clean = cls.GENERIC_CODE_PATTERN.sub("", clean)
        # Collapse multiple spaces
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean or "peer reviewed scientific methodology baseline"

    @classmethod
    def get_privacy_level_metadata(cls, privacy_level: str) -> Dict[str, Any]:
        """Returns security guarantees according to configured privacy level."""
        level = (privacy_level or "standard").lower()
        if level in ("confidential", "air_gapped"):
            return {
                "level": level,
                "label": "Confidential IP Shield (Active)",
                "redaction_enabled": True,
                "query_leak_prevention": True,
                "in_silico_air_gapped": True,
                "external_api_policy": "Sanitized query anonymization enabled",
                "badge_color": "emerald"
            }
        return {
            "level": "standard",
            "label": "Standard Academic Research",
            "redaction_enabled": False,
            "query_leak_prevention": False,
            "in_silico_air_gapped": True,
            "external_api_policy": "Full literature search enabled",
            "badge_color": "blue"
        }
