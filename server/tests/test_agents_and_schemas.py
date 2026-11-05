import pytest
from app.agents.research_planner import ResearchPlanningAgent
from app.agents.literature_discovery import LiteratureDiscoveryAgent
from app.agents.research_analysis import ResearchAnalysisAgent
from app.agents.cross_domain_discovery import CrossDomainDiscoveryAgent
from app.agents.gap_detection import GapDetectionAgent
from app.agents.hypothesis_generation import HypothesisGenerationAgent
from app.agents.critical_reviewer import CriticalReviewerAgent
from app.models.entities import ResearchProject, Source, Finding, Hypothesis


def test_research_planner_output_schema(mock_llm):
    planner = ResearchPlanningAgent(llm_service=mock_llm)
    plan = planner.plan_research("How does biofilm density modulate antibiotic diffusion resistance?")

    assert "objective" in plan
    assert "domain" in plan
    assert "investigation_plan" in plan
    assert isinstance(plan["investigation_plan"], list)
    assert len(plan["suggested_search_queries"]) >= 1
    assert "required_evidence" in plan


@pytest.mark.asyncio
async def test_literature_discovery_agent_no_hallucinations(db_session):
    proj = ResearchProject(title="Lit Test", question="Lit Question")
    db_session.add(proj)
    db_session.commit()

    agent = LiteratureDiscoveryAgent()
    # Query with mock search results
    result = await agent.discover_literature(
        db_session,
        project_id=proj.id,
        queries=["high temperature superconductivity mechanisms"],
        max_papers=3
    )

    assert "papers_discovered" in result
    assert isinstance(result["records"], list)
    # Check that each saved paper has a genuine source entity and citation
    for rec in result["records"]:
        assert rec["paper_id"] is not None
        assert rec["source_id"] is not None
        assert rec["title"] != ""


def test_research_analysis_agent_parameter_extraction(db_session, mock_llm):
    proj = ResearchProject(title="Analysis Test", question="Analysis Question")
    db_session.add(proj)
    db_session.flush()

    source = Source(
        project_id=proj.id,
        source_type="uploaded_document",
        citation_label="Nanotube Electrical Conductivity Trial"
    )
    db_session.add(source)
    db_session.commit()

    raw_text = (
        "Single-walled carbon nanotubes exhibited electrical resistivity rho = 1.05e-4 Ohm*cm "
        "at 298 K. The observed mean breakdown voltage was 4.2 V. Measurement uncertainty was +/- 3%."
    )

    agent = ResearchAnalysisAgent(llm_service=mock_llm)
    findings = agent.analyze_source_document(db_session, proj.id, source, raw_text)

    assert len(findings) >= 1
    assert findings[0].source_id == source.id
    assert findings[0].confidence > 0.0
    assert findings[0].is_extracted is True


def test_cross_domain_discovery_labeling(db_session, mock_llm):
    proj = ResearchProject(title="Cross Domain", question="Interdisciplinary Q")
    db_session.add(proj)
    db_session.flush()

    source = Source(project_id=proj.id, source_type="uploaded_document", citation_label="Source A")
    db_session.add(source)
    db_session.flush()

    f1 = Finding(project_id=proj.id, source_id=source.id, description="Acoustic phonon scattering rate increases above 400 K")
    f2 = Finding(project_id=proj.id, source_id=source.id, description="Thermocouple voltage stability degrades above 400 K")
    db_session.add_all([f1, f2])
    db_session.commit()

    agent = CrossDomainDiscoveryAgent(llm_service=mock_llm)
    relationships = agent.discover_relationships(db_session, proj.id, [f1, f2])

    assert len(relationships) >= 1
    for rel in relationships:
        # PRD rule: must strictly be labelled as explicitly_supported or ai_inferred
        assert rel.connection_type in ("explicitly_supported", "ai_inferred")
        assert rel.rationale != ""


def test_gap_detection_agent(db_session, mock_llm):
    proj = ResearchProject(title="Gap Test", question="Gap Question")
    db_session.add(proj)
    db_session.flush()

    source = Source(project_id=proj.id, source_type="uploaded_document", citation_label="Source G")
    db_session.add(source)
    db_session.flush()

    finding = Finding(project_id=proj.id, source_id=source.id, description="Tested steady-state only", limitations="No dynamic transient testing")
    db_session.add(finding)
    db_session.commit()

    agent = GapDetectionAgent(llm_service=mock_llm)
    gaps = agent.detect_gaps(db_session, proj.id, [finding])

    assert len(gaps) >= 1
    gap = gaps[0]
    assert gap.why_it_matters != ""
    assert gap.existing_coverage != ""
    assert gap.remaining_uncertainty != ""
    assert gap.suggested_investigation != ""


def test_hypothesis_generation_10_required_fields(db_session, mock_llm):
    proj = ResearchProject(title="Hypo Test", question="Hypo Question")
    db_session.add(proj)
    db_session.flush()

    source = Source(project_id=proj.id, source_type="uploaded_document", citation_label="Source H")
    db_session.add(source)
    db_session.flush()

    finding = Finding(project_id=proj.id, source_id=source.id, description="Empirical rate constant k=0.045 s^-1")
    db_session.add(finding)
    db_session.commit()

    agent = HypothesisGenerationAgent(llm_service=mock_llm)
    hypos = agent.generate_hypotheses(db_session, proj.id, [finding], [], [])

    assert len(hypos) >= 1
    h = hypos[0]

    # Verify all 10 PRD specifications:
    assert h.statement != ""                             # 1. Hypothesis statement
    assert h.motivation != ""                            # 2. Research motivation
    assert isinstance(h.supporting_evidence_ids, list)   # 3. Supporting evidence
    assert isinstance(h.related_paper_ids, list)         # 4. Related research papers
    assert isinstance(h.assumptions, list)               # 5. Assumptions
    assert isinstance(h.variables, list)                 # 6. Variables involved
    assert isinstance(h.methodology, list)               # 7. Potential methodology
    assert isinstance(h.experimental_design, dict)       # 8. Possible experimental design
    assert isinstance(h.limitations_uncertainties, list) # 9. Limitations and uncertainties
    assert isinstance(h.suggested_next_steps, list)      # 10. Suggested next steps


def test_critical_reviewer_agent(db_session, mock_llm):
    proj = ResearchProject(title="Review Test", question="Review Question")
    db_session.add(proj)
    db_session.flush()

    hypo = Hypothesis(
        project_id=proj.id,
        title="Reaction Acceleration",
        statement="Increasing pressure from 1 atm to 5 atm doubles yield.",
        motivation="Industrial synthesis acceleration",
        supporting_evidence_ids=["ev_123"],
        variables=[{"name": "Pressure", "type": "independent"}],
        review_status="pending"
    )
    db_session.add(hypo)
    db_session.commit()

    agent = CriticalReviewerAgent(llm_service=mock_llm)
    feedback = agent.review_hypothesis(db_session, hypo)

    assert feedback.evidence_soundness_score > 0.0
    assert feedback.testability_score > 0.0
    assert feedback.verdict in ("approved", "revision_needed", "rejected")
    assert hypo.review_status == feedback.verdict
    assert feedback.evaluation_summary != ""
