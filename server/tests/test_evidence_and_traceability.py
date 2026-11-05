import pytest
from app.services.evidence_service import EvidenceService
from app.services.knowledge_graph import KnowledgeGraphService
from app.models.entities import (
    ResearchProject,
    Source,
    Document,
    Finding,
    Hypothesis,
    RelationshipEntity
)


def test_evidence_span_verification():
    doc_text = """
    In our 2024 trials, the synthesized perovskite solar cells demonstrated a power conversion
    efficiency of 24.3% with an active area of 0.16 cm^2. Thermal degradation was negligible below 340 K.
    """
    
    # 1. Exact quote match
    valid_quote = "synthesized perovskite solar cells demonstrated a power conversion efficiency of 24.3%"
    result = EvidenceService.verify_evidence_span(doc_text, valid_quote)
    assert result["verified"] is True
    assert result["match_ratio"] == 1.0

    # 2. Fabricated / non-existent quote
    fake_quote = "the solar cell converted 99.9% of photon energy into perpetual motion"
    fake_result = EvidenceService.verify_evidence_span(doc_text, fake_quote)
    assert fake_result["verified"] is False
    assert fake_result["match_ratio"] < 0.5


def test_source_and_citation_traceability(db_session):
    # Create project
    proj = ResearchProject(title="Traceability Project", question="Traceability Question")
    db_session.add(proj)
    db_session.flush()

    # Create document and source
    doc = Document(
        project_id=proj.id,
        filename="perovskite_study.pdf",
        file_path="/tmp/perovskite_study.pdf",
        file_size=1024,
        file_hash="dummyhash123",
        page_count=5,
        extracted_text="Power conversion efficiency reached 24.3%."
    )
    db_session.add(doc)
    db_session.flush()

    source = Source(
        project_id=proj.id,
        document_id=doc.id,
        source_type="uploaded_document",
        citation_label="Smith et al. (2024). Perovskite Study"
    )
    db_session.add(source)
    db_session.flush()

    # Create finding strictly linked to source and evidence
    finding = EvidenceService.create_traceable_finding(
        db=db_session,
        project_id=proj.id,
        source_id=source.id,
        description="Power conversion efficiency reached 24.3%.",
        location="Page 2, Section 3.1",
        quote="Power conversion efficiency reached 24.3%.",
        parameters=[{"name": "PCE", "value": 24.3, "unit": "%"}],
        confidence=0.98,
        is_extracted=True
    )
    db_session.commit()

    assert finding.id is not None
    assert finding.source_id == source.id
    assert finding.evidence_id is not None
    assert finding.evidence.exact_quote == "Power conversion efficiency reached 24.3%."
    assert finding.is_extracted is True
    assert finding.parameters[0]["unit"] == "%"


def test_knowledge_graph_provenance_tracing(db_session):
    proj = ResearchProject(title="KG Provenance", question="Test KG")
    db_session.add(proj)
    db_session.flush()

    source = Source(
        project_id=proj.id,
        source_type="uploaded_document",
        citation_label="Reference Paper A"
    )
    db_session.add(source)
    db_session.flush()

    finding = Finding(
        project_id=proj.id,
        source_id=source.id,
        description="Discovered parameter ceiling at 500 MPa",
        confidence=0.95
    )
    db_session.add(finding)
    db_session.flush()

    hypo = Hypothesis(
        project_id=proj.id,
        title="Pressure Invariance Hypothesis",
        statement="Exceeding 500 MPa yields linear creep velocity.",
        motivation="Pressure boundary investigation",
        supporting_evidence_ids=[finding.id]
    )
    db_session.add(hypo)
    db_session.commit()

    # Reconstruct Knowledge Graph
    kg_service = KnowledgeGraphService()
    graph = kg_service.build_from_project(db_session, proj.id)

    assert graph.has_node(proj.id)
    assert graph.has_node(source.id)
    assert graph.has_node(finding.id)
    assert graph.has_node(hypo.id)

    # Verify edge connectivity
    assert graph.has_edge(source.id, finding.id)
    assert graph.has_edge(finding.id, hypo.id)

    # Trace provenance backwards from hypothesis
    provenance = kg_service.trace_hypothesis_provenance(hypo.id)
    prov_ids = [p["node_id"] for p in provenance]
    assert finding.id in prov_ids
    assert source.id in prov_ids

    # Export graph to JSON
    json_graph = kg_service.export_graph_json()
    assert json_graph["total_nodes"] >= 4
    assert json_graph["total_edges"] >= 3
