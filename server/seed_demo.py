import json
from datetime import datetime, timezone
from app.database.session import SessionLocal
from app.models.entities import (
    ResearchProject,
    ResearchPaper,
    Source,
    Finding,
    ResearchGap,
    RelationshipEntity,
    Hypothesis,
    ReviewFeedback,
    Experiment,
    SimulationReport
)

db = SessionLocal()

demo_id = "demo-battery-ev-2026"

# Clear any previous demo
existing = db.query(ResearchProject).filter(ResearchProject.id == demo_id).first()
if existing:
    db.delete(existing)
    db.commit()

now = datetime.now(timezone.utc)

project = ResearchProject(
    id=demo_id,
    title="Suppressing Lithium Dendrite Formation in Fast-Charging Solid-State EV Batteries",
    question="How can localized phase-change thermal interfaces suppress lithium dendrite nucleation and short-circuits in solid-state batteries during sub-zero fast charging?",
    domain="Materials Science & Electrochemistry",
    scope="Comprehensive Synthesis",
    enable_simulation=True,
    status="completed",
    current_stage="simulation",
    progress=100,
    status_message="Autonomous multi-agent investigation completed with verified in silico simulation.",
    created_at=now,
    completed_at=now,
    updated_at=now
)
db.add(project)
db.flush()

# Papers
p1 = ResearchPaper(
    id="pap-01",
    project_id=demo_id,
    title="Mechanistic Insights into Lithium Dendrite Growth Across Ceramic Solid Electrolytes",
    authors=["Q. Zhang", "L. Chen", "Y. Wang"],
    publication_date="2024",
    url="https://doi.org/10.1016/j.ensm.2024.01.012",
    doi="10.1016/j.ensm.2024.01.012",
    source_provider="energy_storage_materials"
)
p2 = ResearchPaper(
    id="pap-02",
    project_id=demo_id,
    title="Thermal Fluctuations and Electro-Chemo-Mechanical Breakdown in Solid-State Lithium Batteries",
    authors=["D. Kundu", "L. F. Nazar"],
    publication_date="2023",
    url="https://doi.org/10.1038/s41560-023-01290-x",
    doi="10.1038/s41560-023-01290-x",
    source_provider="nature_energy"
)
p3 = ResearchPaper(
    id="pap-03",
    project_id=demo_id,
    title="In Silico Multiphysics Modeling of Interfacial Stress and Dendrite Propagation at Sub-Zero Temperatures",
    authors=["M. S. Park", "H. K. Liu"],
    publication_date="2024",
    url="https://arxiv.org/abs/2403.08912",
    doi="arXiv:2403.08912",
    source_provider="arxiv"
)
db.add_all([p1, p2, p3])
db.flush()

# Sources
s1 = Source(
    id="src-energy-01",
    project_id=demo_id,
    paper_id=p1.id,
    source_type="external_paper",
    citation_label="Zhang et al. (2024)"
)
s2 = Source(
    id="src-nature-02",
    project_id=demo_id,
    paper_id=p2.id,
    source_type="external_paper",
    citation_label="Kundu & Nazar (2023)"
)
s3 = Source(
    id="src-arxiv-03",
    project_id=demo_id,
    paper_id=p3.id,
    source_type="external_paper",
    citation_label="Park & Liu (2024)"
)
db.add_all([s1, s2, s3])
db.flush()

# Findings
f1 = Finding(
    id="fnd-01",
    project_id=demo_id,
    source_id=s1.id,
    description="Dendrite nucleation accelerates exponentially when local current density exceeds 3.5 mA/cm2 under sub-ambient temperatures (-10C).",
    supporting_quote="At sub-ambient temperatures, current constriction induces local thermal-runaway micro-domains exceeding the 3.5 mA/cm2 threshold.",
    document_location="Page 4, Col 2",
    confidence=0.94,
    extraction_status="extracted"
)
f2 = Finding(
    id="fnd-02",
    project_id=demo_id,
    source_id=s2.id,
    description="Local interfacial temperature spikes of 6 to 12C occur due to non-uniform charge transfer impedance across ceramic grain boundaries.",
    supporting_quote="Micro-scale temperature gradients across grain boundaries exacerbate non-uniform ion flux by up to 48%.",
    document_location="Page 8, Figure 5",
    confidence=0.91,
    extraction_status="extracted"
)
f3 = Finding(
    id="fnd-03",
    project_id=demo_id,
    source_id=s3.id,
    description="Phase-change thermal buffers effectively clamp peak localized junction temperature, maintaining uniform lithium-ion flux.",
    supporting_quote="Latent heat absorption via localized wax/graphene matrices dissipates critical thermal spikes within 15 ms.",
    document_location="Page 12, Discussion",
    confidence=0.95,
    extraction_status="extracted"
)
db.add_all([f1, f2, f3])

# Relationships for Knowledge Graph
rel1 = RelationshipEntity(
    id="rel-01",
    project_id=demo_id,
    source_concept_id="Grain Boundary Overpotential",
    target_concept_id="Localized Joule Heating",
    relation_type="causes",
    connection_type="explicitly_supported",
    rationale="Non-uniform interfacial impedance at ceramic grain boundaries drives concentrated local current and Joule heating spikes.",
    source_references=[s1.id, s2.id]
)
rel2 = RelationshipEntity(
    id="rel-02",
    project_id=demo_id,
    source_concept_id="Localized Joule Heating",
    target_concept_id="Dendrite Nucleation Velocity",
    relation_type="correlates_with",
    connection_type="explicitly_supported",
    rationale="Elevated local temperature spikes distort electro-chemo-mechanical stress fields, exponentially accelerating dendrite propagation.",
    source_references=[s2.id]
)
rel3 = RelationshipEntity(
    id="rel-03",
    project_id=demo_id,
    source_concept_id="Phase-Change Latent Heat Matrix",
    target_concept_id="Interfacial Temperature Clamping",
    relation_type="supports",
    connection_type="ai_inferred",
    rationale="Cross-domain synthesis: Applying micro-encapsulated phase change material buffers to the solid electrolyte interface absorbs transient heat spikes.",
    source_references=[s3.id]
)
db.add_all([rel1, rel2, rel3])

# Gaps
gap1 = ResearchGap(
    id="gap-01",
    project_id=demo_id,
    gap_type="underexplored_condition",
    title="Lack of Real-Time Micro-Thermal Regulation at the Solid-State Electrolyte Interface",
    description="Existing research focuses either entirely on chemical SEI additives or bulky external pack cooling, neglecting micro-scale latent heat buffers directly at the anode surface.",
    why_it_matters="Unregulated micro-thermal spikes directly trigger rapid dendrite penetration causing catastrophic cell short-circuits during 15-minute fast charging.",
    existing_coverage="Macro-scale pack cooling and static polymer interlayer coating.",
    remaining_uncertainty="How interfacial phase change latency affects continuous ion transport kinetics across high C-rate cycles.",
    suggested_investigation="Coupled electrochemical-thermal numerical simulation combining Butler-Volmer kinetics with transient heat dissipation.",
    supporting_sources=[s1.id, s2.id]
)
db.add(gap1)

# Hypotheses
hyp1 = Hypothesis(
    id="hyp-01",
    project_id=demo_id,
    title="Localized Latent Heat Buffer Suppresses Dendrite Nucleation Rate by >40%",
    statement="Integrating a 45nm phase-change thermal interface material (PCM) at the lithium/solid-electrolyte boundary absorbs transient Joule heating spikes, reducing localized peak temperatures below 3.5C and decreasing dendrite nucleation velocity by at least 42% under 4C fast charging at -5C.",
    motivation="Resolves the fundamental trade-off between rapid sub-zero charging and dendrite-induced catastrophic thermal breakdown in next-generation solid-state batteries.",
    variables=[
        {"name": "PCM layer thickness (nm)", "type": "independent"},
        {"name": "Local peak temperature rise (C)", "type": "dependent"},
        {"name": "Dendrite nucleation rate (events/s)", "type": "dependent"}
    ],
    methodology=["In silico numerical ODE modeling", "FIB-SEM operando cross-section validation"],
    experimental_design={"control": "Bare Li/LLZO cell", "treatment": "45nm PCM-coated cell", "cycles": 500, "rate": "4C"},
    limitations_uncertainties=[
        "Assumes uniform thermal conductivity of the composite matrix",
        "Evaluated primarily for operating temperatures between -20C and 45C"
    ],
    review_status="approved"
)
db.add(hyp1)
db.flush()

# Review Feedback
rev1 = ReviewFeedback(
    id="rev-01",
    hypothesis_id=hyp1.id,
    reviewer_agent="CriticalReviewerAgent",
    evidence_soundness_score=0.94,
    testability_score=0.96,
    verdict="approved",
    evaluation_summary="Hypothesis is rigorously grounded in multi-paper evidence (Zhang 2024, Kundu 2023). Variables are clearly defined with testable metric thresholds (>40% suppression). Recommended for immediate computational validation."
)
db.add(rev1)

# Experiment
exp1 = Experiment(
    id="exp-01",
    hypothesis_id=hyp1.id,
    status="completed",
    simulation_path="model_builder",
    current_iteration=1,
    max_iterations=3
)
db.add(exp1)
db.flush()

# Simulation Report
rep1 = SimulationReport(
    id="rep-01",
    experiment_id=exp1.id,
    status="completed",
    implementation_source="model_builder",
    code_tests="passed",
    model_verification="verified",
    empirical_validation="provisional",
    iterations=1,
    limitations=["1D spatial boundary assumption", "Linear thermal contact resistance"],
    mathematical_equations=[
        "dY/dt = -k_eff * Y",
        "k_eff = k0 * exp(-Ea / (R * T))",
        "J_ion = -D_eff * (dC/dx) + (z*F*D_eff/(R*T))*E"
    ],
    execution_logs=[
        "LangGraph: Initializing computational sandbox environment",
        "Sandbox: Formulating numerical ODE model for hypothesis 'Localized Latent Heat Buffer Suppresses Dendrite Nucleation Rate by >40%'",
        "Sandbox: Executing numerical integration across 100 timesteps",
        "BenchmarkValidator: Verifying physical non-divergence boundary constraints",
        "BenchmarkValidator: Comparing against reference parameter values (Accuracy: 97.4%)",
        "EvidenceValidator: Level 1: PASSED | Level 2: PASSED | Level 3: PROVISIONAL"
    ],
    test_results={
        "accuracy": 0.974,
        "max_deviation": 0.026,
        "passed": True
    },
    numerical_metrics={
        "k_eff": 0.00342,
        "final_state": 12.4,
        "time_horizon": "100.0 s"
    }
)
db.add(rep1)

db.commit()
db.close()
print("Demo project successfully seeded with full graph, evidence, and simulation models!")
