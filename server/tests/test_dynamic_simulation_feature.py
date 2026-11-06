import pytest
from app.simulation.scientific_models import ScientificModelRegistry
from app.models.entities import ResearchProject
from app.api.routes.projects import serialize_project_full

def test_domain_classification():
    # Computing
    c1 = ScientificModelRegistry.classify_domain(
        "Resource Optimization and Energy Optimization across High-Performance Computing Clusters using Dynamic Voltage and Frequency Scaling"
    )
    assert c1 == "computing_energy"

    # Materials / Batteries
    c2 = ScientificModelRegistry.classify_domain(
        "Why do 2D/3D hybrid perovskite solar cells suffer phase segregation under light soaking?"
    )
    assert c2 == "materials_electrochemistry"

    # Biomedical
    c3 = ScientificModelRegistry.classify_domain(
        "How does microglial TREM2 signaling modulate tau spreading in early-stage Alzheimer's disease?"
    )
    assert c3 == "biomedical_pk"

    # Qualitative (Honest verdict required)
    c4 = ScientificModelRegistry.classify_domain(
        "What are the ethical, sociological, and philosophical implications of AI copyright under international law?"
    )
    assert c4 == "qualitative_not_feasible"


def test_qualitative_inquiry_returns_not_feasible_zero_api():
    model = ScientificModelRegistry.build_simulation_model(
        question="What are the ethical and legal foundations of digital copyright policy?",
        domain="Legal & Philosophy"
    )
    assert model["feasible"] is False
    assert model["status"] == "not_applicable"
    assert "Not Mathematically Feasible" in model["model"]
    assert "qualitative" in model["verdictMessage"].lower()
    assert len(model["inputFeatures"]) > 0
    assert len(model["outputFeatures"]) > 0


def test_computing_energy_optimization_dynamic_model():
    demands = {
        "frequency_ghz": 3.0,
        "voltage": 1.15,
        "capacitance_nf": 1.2,
        "arrival_rate": 900.0,
        "service_rate": 1300.0
    }
    model = ScientificModelRegistry.build_simulation_model(
        question="Energy optimization in datacenters using dynamic voltage frequency scaling",
        domain="Computer Science",
        user_demands=demands
    )
    assert model["feasible"] is True
    assert model["category"] == "Computer Systems & Energy Efficiency"
    assert "DVFS" in model["model"]
    assert any("P_dyn = C * V^2 * f" in eq for eq in model["equations"])
    assert any(f["name"] == "Clock Frequency (f)" and "3.0" in f["value"] for f in model["inputFeatures"])
    assert any("Dynamic Power Dissipation" in f["name"] for f in model["outputFeatures"])


def test_simulation_disabled_serialization(db_session):
    proj = ResearchProject(
        title="Disabled Sim Test",
        question="How does energy optimization work?",
        enable_simulation=False
    )
    db_session.add(proj)
    db_session.commit()

    serialized = serialize_project_full(proj, db_session)
    exp = serialized.get("experiments")
    assert exp is not None
    assert exp["simulationRequired"] is False
    assert exp["status"] == "disabled"
    assert exp["feasible"] is False


def test_python_script_generation_varies_by_domain():
    # Computing script
    script_comp = ScientificModelRegistry.generate_python_script(
        question="Resource and energy optimization across servers with DVFS",
        user_demands={"frequency_ghz": 2.8, "voltage": 1.05}
    )
    assert "CMOS Dynamic Power Scaling" in script_comp
    assert "FREQUENCY_GHZ = 2.8" in script_comp

    # Electrochemistry script
    script_batt = ScientificModelRegistry.generate_python_script(
        question="Lithium dendrite growth and solid-state battery degradation",
        user_demands={"temperature": 320.0}
    )
    assert "Butler-Volmer & Arrhenius" in script_batt
    assert "T = 320.0" in script_batt
