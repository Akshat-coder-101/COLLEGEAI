from unittest.mock import AsyncMock, patch
import pytest
from app.models.entities import ResearchProject, Hypothesis, Experiment, SimulationReport, ReviewFeedback


def test_health_endpoints(client):
    res_root = client.get("/health")
    assert res_root.status_code == 200
    assert res_root.json()["status"] == "healthy"

    res_v1 = client.get("/api/v1/health")
    assert res_v1.status_code == 200
    assert res_v1.json()["service"] == "HypothesisLab AI"


def test_research_project_crud(client):
    # 1. Create project
    create_payload = {
        "title": "Quantum Thermal Transport",
        "question": "How does nanoscale thermal gradient affect coherent phonon transport?",
        "domain": "Condensed Matter Physics"
    }
    create_res = client.post("/api/v1/research", json=create_payload)
    assert create_res.status_code == 201
    proj_data = create_res.json()
    assert proj_data["title"] == create_payload["title"]
    project_id = proj_data["id"]

    # 2. List projects
    list_res = client.get("/api/v1/research")
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(p["id"] == project_id for p in items)

    # 3. Get single project
    get_res = client.get(f"/api/v1/research/{project_id}")
    assert get_res.status_code == 200
    assert get_res.json()["domain"] == "Condensed Matter Physics"

    # 4. Status endpoint
    status_res = client.get(f"/api/v1/research/{project_id}/status")
    assert status_res.status_code == 200
    assert status_res.json()["project_id"] == project_id
    assert status_res.json()["progress"] == 0

    # 5. Results endpoint before workflow run
    res_endpoint = client.get(f"/api/v1/research/{project_id}/results")
    assert res_endpoint.status_code == 200
    assert res_endpoint.json()["findings_count"] == 0

    # 6. Delete project
    del_res = client.delete(f"/api/v1/research/{project_id}")
    assert del_res.status_code == 204

    # Verify deleted
    not_found_res = client.get(f"/api/v1/research/{project_id}")
    assert not_found_res.status_code == 404


def test_research_run_endpoint(client):
    create_payload = {
        "title": "Enzymatic Kinetics",
        "question": "What limits enzymatic catalytic efficiency under varying pH?"
    }
    create_res = client.post("/api/v1/research", json=create_payload)
    project_id = create_res.json()["id"]

    with patch("app.workflows.research_workflow.ResearchWorkflowRunner.execute_workflow", new_callable=AsyncMock) as mock_exec:
        run_res = client.post(f"/api/v1/research/{project_id}/run")
        assert run_res.status_code == 200
        assert run_res.json()["status"] == "processing"
        assert run_res.json()["project_id"] == project_id


def test_discoveries_and_hypotheses_endpoints(client, db_session):
    # Setup test project with hypothesis in DB
    proj = ResearchProject(
        title="Test Discovery Project",
        question="What controls reaction kinetics?",
        domain="Chemistry"
    )
    db_session.add(proj)
    db_session.flush()

    hypo = Hypothesis(
        project_id=proj.id,
        title="Catalytic Rate Shift",
        statement="Increased substrate concentration enhances steady-state flux by 30%.",
        motivation="Addresses reaction saturation rate.",
        variables=[{"name": "Substrate", "type": "independent"}],
        review_status="approved"
    )
    db_session.add(hypo)
    db_session.flush()

    feedback = ReviewFeedback(
        hypothesis_id=hypo.id,
        reviewer_agent="CriticalReviewerAgent",
        evidence_soundness_score=0.90,
        testability_score=0.95,
        verdict="approved",
        evaluation_summary="Validated against empirical kinetic models."
    )
    db_session.add(feedback)
    db_session.commit()

    # Discoveries endpoint
    disc_res = client.get(f"/api/v1/research/{proj.id}/discoveries")
    assert disc_res.status_code == 200
    assert "gaps" in disc_res.json()
    assert "relationships" in disc_res.json()

    # Hypotheses list endpoint
    hypos_res = client.get(f"/api/v1/research/{proj.id}/hypotheses")
    assert hypos_res.status_code == 200
    assert len(hypos_res.json()["hypotheses"]) >= 1

    # Single hypothesis detail endpoint
    single_hypo_res = client.get(f"/api/v1/hypotheses/{hypo.id}")
    assert single_hypo_res.status_code == 200
    assert single_hypo_res.json()["title"] == "Catalytic Rate Shift"
    assert single_hypo_res.json()["review_status"] == "approved"
    assert single_hypo_res.json()["review_feedback"]["testability_score"] == 0.95


def test_simulation_endpoints(client, db_session):
    proj = ResearchProject(title="Sim Project", question="Sim Question")
    db_session.add(proj)
    db_session.flush()

    hypo = Hypothesis(
        project_id=proj.id,
        title="Thermal Model",
        statement="Thermal conductivity scales inversely with defect density.",
        motivation="Heat sink optimization"
    )
    db_session.add(hypo)
    db_session.commit()

    # Start simulation
    sim_res = client.post(
        f"/api/v1/hypotheses/{hypo.id}/simulate",
        json={"simulation_path": "built_model", "max_iterations": 3}
    )
    assert sim_res.status_code == 202
    exp_data = sim_res.json()
    exp_id = exp_data["experiment_id"]
    assert exp_data["status"] == "running"

    # Status check
    status_res = client.get(f"/api/v1/experiments/{exp_id}/status")
    assert status_res.status_code == 200
    assert status_res.json()["experiment_id"] == exp_id

    # Create report in DB
    report = SimulationReport(
        experiment_id=exp_id,
        status="completed",
        implementation_source="built_model",
        code_tests="passed",
        model_verification="verified",
        empirical_validation="not_evaluated",
        iterations=1,
        limitations=["Ideal boundary conditions"],
        mathematical_equations=["dY/dt = -k * Y"]
    )
    db_session.add(report)
    db_session.commit()

    # Report endpoint
    report_res = client.get(f"/api/v1/experiments/{exp_id}/report")
    assert report_res.status_code == 200
    assert report_res.json()["code_tests"] == "passed"
    assert report_res.json()["model_verification"] == "verified"


def test_frontend_projects_contract_endpoints(client, db_session):
    # 1. Create project via frontend contract endpoint POST /api/v1/projects
    create_payload = {
        "question": "How does microglial TREM2 signaling modulate tau spreading?",
        "domain": "Neuroscience",
        "scope": "Comprehensive Synthesis"
    }
    create_res = client.post("/api/v1/projects", json=create_payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    proj_id = created_data["id"]
    assert created_data["question"] == create_payload["question"]
    assert created_data["scope"] == "Comprehensive Synthesis"

    # 2. List projects via GET /api/v1/projects
    list_res = client.get("/api/v1/projects")
    assert list_res.status_code == 200
    assert isinstance(list_res.json(), list)
    assert any(p["id"] == proj_id for p in list_res.json())

    # 3. Status via GET /api/v1/projects/{id}/status
    status_res = client.get(f"/api/v1/projects/{proj_id}/status")
    assert status_res.status_code == 200
    assert "workflow" in status_res.json()
    assert "currentStage" in status_res.json()["workflow"]

    # 4. Full details via GET /api/v1/projects/{id}
    full_res = client.get(f"/api/v1/projects/{proj_id}")
    assert full_res.status_code == 200
    full_data = full_res.json()
    assert "overview" in full_data
    assert "sources" in full_data
    assert "comparisons" in full_data
    assert "discoveries" in full_data
    assert "hypotheses" in full_data
    assert "stats" in full_data
    assert "workflow" in full_data

    # 5. Granular detail endpoints
    sources_res = client.get(f"/api/v1/projects/{proj_id}/sources")
    assert sources_res.status_code == 200
    assert isinstance(sources_res.json(), list)

    comp_res = client.get(f"/api/v1/projects/{proj_id}/comparisons")
    assert comp_res.status_code == 200
    assert "agreements" in comp_res.json()

    disc_res = client.get(f"/api/v1/projects/{proj_id}/discoveries")
    assert disc_res.status_code == 200
    assert "knowledgeGraph" in disc_res.json()
    assert "nodes" in disc_res.json()["knowledgeGraph"]

    hypo_res = client.get(f"/api/v1/projects/{proj_id}/hypotheses")
    assert hypo_res.status_code == 200
    assert isinstance(hypo_res.json(), list)

    # 6. Delete project via DELETE /api/v1/projects/{id}
    del_res = client.delete(f"/api/v1/projects/{proj_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True
