import pytest
from app.models.entities import ResearchProject, Document, Source, Finding, Hypothesis
from app.workflows.research_workflow import ResearchWorkflowRunner
from app.workflows.simulation_workflow import SimulationWorkflowRunner
from app.services.knowledge_graph import KnowledgeGraphService


@pytest.mark.asyncio
async def test_end_to_end_research_and_simulation_workflow(db_session, client):
    # 1. Create project via API
    create_res = client.post("/api/v1/research", json={
        "title": "Thermoelectric Nanomaterials",
        "question": "How does grain boundary scattering optimize the thermoelectric figure of merit ZT?",
        "domain": "Materials Physics"
    })
    assert create_res.status_code == 201
    project_id = create_res.json()["id"]

    # 2. Add an uploaded document with scientific text
    doc_text = """
    Nanostructured bismuth telluride alloys exhibit strong phonon scattering at grain boundaries.
    The electrical resistivity rho was measured at 1.2e-5 Ohm*m at 300 K.
    The Seebeck coefficient alpha reached +210 uV/K.
    Figure of merit ZT achieved a peak of 1.45 at 380 K.
    However, stability under long-term thermal cycling above 450 K remains underexplored.
    """
    doc = Document(
        project_id=project_id,
        filename="bismuth_telluride_study.pdf",
        file_path="/tmp/bismuth_telluride_study.pdf",
        file_size=2048,
        file_hash="hash_bismuth_123",
        page_count=6,
        extracted_text=doc_text
    )
    db_session.add(doc)
    db_session.commit()

    # 3. Execute the full multi-agent research workflow
    workflow_runner = ResearchWorkflowRunner()
    await workflow_runner.execute_workflow(project_id, db=db_session)

    # 4. Refresh project and verify completion
    proj = db_session.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    assert proj.status == "completed"
    assert proj.progress == 100
    assert proj.current_stage == "completed"

    # 5. Verify extracted entities and provenance
    findings = proj.findings
    assert len(findings) >= 1
    assert any(f.is_extracted for f in findings)

    gaps = proj.gaps
    assert len(gaps) >= 1

    hypotheses = proj.hypotheses
    assert len(hypotheses) >= 1
    hypo = hypotheses[0]
    assert hypo.statement != ""
    assert hypo.review_status in ("approved", "revision_needed")

    # 6. Verify Knowledge Graph
    kg = KnowledgeGraphService()
    graph = kg.build_from_project(db_session, project_id)
    assert graph.has_node(project_id)
    assert graph.has_node(hypo.id)

    # 7. Test Results API endpoint
    results_res = client.get(f"/api/v1/research/{project_id}/results")
    assert results_res.status_code == 200
    res_data = results_res.json()
    assert res_data["status"] == "completed"
    assert res_data["findings_count"] >= 1
    assert res_data["gaps_count"] >= 1
    assert res_data["hypotheses_count"] >= 1

    # 8. Trigger Simulation Workflow on the generated hypothesis
    sim_runner = SimulationWorkflowRunner()
    sim_res = client.post(
        f"/api/v1/hypotheses/{hypo.id}/simulate",
        json={"simulation_path": "built_model", "max_iterations": 2}
    )
    assert sim_res.status_code == 202
    exp_id = sim_res.json()["experiment_id"]

    await sim_runner.execute_simulation(exp_id, db=db_session)

    # 9. Verify Simulation Report
    report_res = client.get(f"/api/v1/experiments/{exp_id}/report")
    assert report_res.status_code == 200
    report_data = report_res.json()
    assert report_data["status"] == "completed"
    assert report_data["code_tests"] == "passed"
    assert report_data["model_verification"] in ("verified", "unverified")
    assert report_data["empirical_validation"] in ("validated", "not_evaluated")
    assert report_data["iterations"] >= 1
