import pytest
from app.services.privacy_service import PrivacyService
from app.services.document_service import DocumentService
from app.models.entities import ResearchProject, Document
from app.api.routes.projects import serialize_project_full

def test_privacy_service_redaction_rules():
    sample_paper = """
    CONFIDENTIAL - DO NOT DISTRIBUTE
    Title: Novel Kinase Inhibitor Candidate
    Authors: Dr. John Doe (johndoe@lab.stanford.edu) and Dr. Jane Smith
    Affiliation: Department of Chemical Biology, Stanford University
    Funding: Supported by NIH Grant #R01-HG009823 and DARPA Contract #HR0011-20-C-0091.
    Patents: US Patent Application 17/984,231 describes the core scaffold.
    Abstract:
    We evaluated proprietary Compound BMS-986165 and synthesized variant Compound-4b against
    mutant EGFR. Phone contact: (650) 555-0199.
    """

    sanitized, audit = PrivacyService.sanitize_research_text(sample_paper)

    # Asserts that sensitive entities were redacted
    assert "johndoe@lab.stanford.edu" not in sanitized
    assert "[EMAIL_REDACTED]" in sanitized
    assert "17/984,231" not in sanitized
    assert "[PATENT_REF_REDACTED]" in sanitized
    assert "R01-HG009823" not in sanitized
    assert "[GRANT_REF_REDACTED]" in sanitized
    assert "BMS-986165" not in sanitized
    assert "[CONFIDENTIAL_COMPOUND_ID]" in sanitized or "[PROPRIETARY_CODE_ID]" in sanitized
    assert "(650) 555-0199" not in sanitized
    assert "[PHONE_REDACTED]" in sanitized
    assert "CONFIDENTIAL" not in sanitized or "[CONFIDENTIAL_NOTICE_REDACTED]" in sanitized

    # Asserts audit counters
    assert audit["total_redactions"] >= 5
    assert audit["emails"] >= 1
    assert audit["patents"] >= 1
    assert audit["grants"] >= 1
    assert audit["privacy_shield_active"] is True


def test_sanitize_external_search_query():
    raw_query = "Evaluate proprietary Compound-X99 under US Patent 16/999,111 in CONFIDENTIAL clinical trials"
    cleaned = PrivacyService.sanitize_external_search_query(raw_query)

    assert "Compound-X99" not in cleaned
    assert "16/999,111" not in cleaned
    assert "CONFIDENTIAL" not in cleaned
    assert len(cleaned) > 5


def test_confidential_project_serialization(db_session):
    proj = ResearchProject(
        title="Confidential Drug Discovery",
        question="How does compound-x inhibit tau protein aggregation?",
        is_confidential=True,
        privacy_level="confidential"
    )
    db_session.add(proj)
    db_session.commit()

    serialized = serialize_project_full(proj, db_session)
    assert serialized["isConfidential"] is True
    assert serialized["privacyLevel"] == "confidential"
    assert "privacy" in serialized
    assert serialized["privacy"]["redaction_enabled"] is True
    assert serialized["privacy"]["query_leak_prevention"] is True
    assert serialized["privacy"]["in_silico_air_gapped"] is True
