import uuid
from datetime import datetime, timezone
from typing import Optional, List, Any
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)



class ResearchProject(Base):
    __tablename__ = "research_projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    question = Column(Text, nullable=False)
    domain = Column(String(100), nullable=True)
    scope = Column(String(100), default="Comprehensive Synthesis")
    enable_simulation = Column(Boolean, default=True)
    status = Column(String(50), default="created")  # created, processing, completed, failed
    current_stage = Column(String(100), default="initialized")
    progress = Column(Integer, default=0)
    status_message = Column(Text, default="Project created")
    created_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    papers = relationship("ResearchPaper", back_populates="project", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="project", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="project", cascade="all, delete-orphan")
    gaps = relationship("ResearchGap", back_populates="project", cascade="all, delete-orphan")
    hypotheses = relationship("Hypothesis", back_populates="project", cascade="all, delete-orphan")
    relationships_data = relationship("RelationshipEntity", back_populates="project", cascade="all, delete-orphan")
    workflow_executions = relationship("WorkflowExecution", back_populates="project", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=False)  # SHA-256 for duplicate detection
    page_count = Column(Integer, default=0)
    extracted_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    project = relationship("ResearchProject", back_populates="documents")
    sources = relationship("Source", back_populates="document", cascade="all, delete-orphan")


class ResearchPaper(Base):
    __tablename__ = "research_papers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    authors = Column(JSON, default=list)  # list of author names
    abstract = Column(Text, nullable=True)
    publication_date = Column(String(50), nullable=True)
    url = Column(String(500), nullable=True)
    doi = Column(String(100), nullable=True)
    source_provider = Column(String(50), default="upload")  # semantic_scholar, arxiv, crossref, upload
    retrieval_date = Column(DateTime, default=utc_now)
    limitations = Column(Text, nullable=True)
    relevance_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=utc_now)

    project = relationship("ResearchProject", back_populates="papers")
    sources = relationship("Source", back_populates="paper", cascade="all, delete-orphan")


class Source(Base):
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    paper_id = Column(String(36), ForeignKey("research_papers.id", ondelete="SET NULL"), nullable=True)
    source_type = Column(String(50), nullable=False)  # uploaded_document, external_paper, user_url
    citation_label = Column(String(255), nullable=False)
    metadata_info = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)

    project = relationship("ResearchProject", back_populates="sources")
    document = relationship("Document", back_populates="sources")
    paper = relationship("ResearchPaper", back_populates="sources")
    evidence_items = relationship("Evidence", back_populates="source", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="source", cascade="all, delete-orphan")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_id = Column(String(36), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    exact_quote = Column(Text, nullable=False)
    location_reference = Column(String(255), nullable=True)  # e.g., Page 3, Section 2.1
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=utc_now)

    source = relationship("Source", back_populates="evidence_items")
    findings = relationship("Finding", back_populates="evidence")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(String(36), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    evidence_id = Column(String(36), ForeignKey("evidence.id", ondelete="SET NULL"), nullable=True)
    description = Column(Text, nullable=False)
    methodology = Column(Text, nullable=True)
    parameters = Column(JSON, default=list)  # list of {name, value, unit}
    document_location = Column(String(255), nullable=True)
    supporting_quote = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)
    extraction_status = Column(String(50), default="extracted")  # extracted, verified
    is_extracted = Column(Boolean, default=True)  # True = directly from source
    limitations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    project = relationship("ResearchProject", back_populates="findings")
    source = relationship("Source", back_populates="findings")
    evidence = relationship("Evidence", back_populates="findings")


class Concept(Base):
    __tablename__ = "concepts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    domain = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)


class Variable(Base):
    __tablename__ = "variables"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    variable_type = Column(String(50), default="independent")  # independent, dependent, control
    unit = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)


class RelationshipEntity(Base):
    __tablename__ = "relationships"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False)
    source_concept_id = Column(String(255), nullable=False)
    target_concept_id = Column(String(255), nullable=False)
    relation_type = Column(String(100), nullable=False)  # correlates_with, causes, contradicts, supports
    connection_type = Column(String(50), nullable=False)  # explicitly_supported OR ai_inferred
    rationale = Column(Text, nullable=False)
    source_references = Column(JSON, default=list)  # list of source IDs
    created_at = Column(DateTime, default=utc_now)

    project = relationship("ResearchProject", back_populates="relationships_data")


class ResearchGap(Base):
    __tablename__ = "research_gaps"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False)
    gap_type = Column(String(100), nullable=False)  # unanswered_question, underexplored_condition, contradiction, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    why_it_matters = Column(Text, nullable=False)
    existing_coverage = Column(Text, nullable=False)
    remaining_uncertainty = Column(Text, nullable=False)
    suggested_investigation = Column(Text, nullable=False)
    supporting_sources = Column(JSON, default=list)  # list of source IDs
    created_at = Column(DateTime, default=utc_now)

    project = relationship("ResearchProject", back_populates="gaps")


class Hypothesis(Base):
    __tablename__ = "hypotheses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    statement = Column(Text, nullable=False)
    motivation = Column(Text, nullable=False)
    supporting_evidence_ids = Column(JSON, default=list)  # list of Evidence/Finding IDs
    related_paper_ids = Column(JSON, default=list)  # list of Paper/Source IDs
    assumptions = Column(JSON, default=list)  # list of strings
    variables = Column(JSON, default=list)  # list of {name, type, unit, role}
    methodology = Column(JSON, default=list)  # list of methodology steps
    experimental_design = Column(JSON, default=dict)  # control, metrics, conditions
    limitations_uncertainties = Column(JSON, default=list)  # list of limitations
    suggested_next_steps = Column(JSON, default=list)  # list of strings
    review_status = Column(String(50), default="pending")  # pending, reviewed, approved, revision_needed, rejected
    created_at = Column(DateTime, default=utc_now)

    project = relationship("ResearchProject", back_populates="hypotheses")
    reviews = relationship("ReviewFeedback", back_populates="hypothesis", cascade="all, delete-orphan")
    experiments = relationship("Experiment", back_populates="hypothesis", cascade="all, delete-orphan")


class ReviewFeedback(Base):
    __tablename__ = "review_feedbacks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    hypothesis_id = Column(String(36), ForeignKey("hypotheses.id", ondelete="CASCADE"), nullable=False)
    reviewer_agent = Column(String(100), default="CriticalReviewerAgent")
    evidence_soundness_score = Column(Float, default=0.0)
    has_unsupported_assumptions = Column(Boolean, default=False)
    unsupported_assumptions = Column(JSON, default=list)
    logical_consistency_score = Column(Float, default=0.0)
    logical_inconsistencies = Column(JSON, default=list)
    alternative_explanations = Column(JSON, default=list)
    testability_score = Column(Float, default=0.0)
    suggested_improvements = Column(JSON, default=list)
    verdict = Column(String(50), default="pending")  # approved, revision_needed, rejected
    evaluation_summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    hypothesis = relationship("Hypothesis", back_populates="reviews")


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    hypothesis_id = Column(String(36), ForeignKey("hypotheses.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="created")  # created, running, completed, failed, retrying
    simulation_path = Column(String(50), default="github_repo")  # github_repo OR built_model
    repository_url = Column(String(500), nullable=True)
    repository_name = Column(String(255), nullable=True)
    current_iteration = Column(Integer, default=1)
    max_iterations = Column(Integer, default=3)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    hypothesis = relationship("Hypothesis", back_populates="experiments")
    reports = relationship("SimulationReport", back_populates="experiment", cascade="all, delete-orphan")


class SimulationReport(Base):
    __tablename__ = "simulation_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experiment_id = Column(String(36), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="completed")  # completed, failed
    implementation_source = Column(String(50), default="github")  # github OR built_model
    code_tests = Column(String(50), default="not_evaluated")  # passed, failed, not_evaluated
    model_verification = Column(String(50), default="not_evaluated")  # verified, unverified, not_evaluated
    empirical_validation = Column(String(50), default="not_evaluated")  # validated, unvalidated, not_evaluated
    iterations = Column(Integer, default=1)
    execution_logs = Column(JSON, default=list)
    test_results = Column(JSON, default=dict)
    limitations = Column(JSON, default=list)
    mathematical_equations = Column(JSON, default=list)
    numerical_metrics = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)

    experiment = relationship("Experiment", back_populates="reports")


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False)
    current_stage = Column(String(100), default="started")
    progress = Column(Integer, default=0)
    status = Column(String(50), default="running")  # running, completed, failed, cancelled
    error_message = Column(Text, nullable=True)
    logs = Column(JSON, default=list)  # list of {timestamp, agent, message, level}
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    project = relationship("ResearchProject", back_populates="workflow_executions")
