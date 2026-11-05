import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.entities import (
    ResearchProject,
    Document,
    Source,
    WorkflowExecution,
)
from app.agents.research_planner import ResearchPlanningAgent
from app.agents.literature_discovery import LiteratureDiscoveryAgent
from app.agents.research_analysis import ResearchAnalysisAgent
from app.agents.cross_domain_discovery import CrossDomainDiscoveryAgent
from app.agents.gap_detection import GapDetectionAgent
from app.agents.hypothesis_generation import HypothesisGenerationAgent
from app.agents.critical_reviewer import CriticalReviewerAgent
from app.services.knowledge_graph import KnowledgeGraphService
from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)


class ResearchWorkflowRunner:
    def __init__(self):
        self.planner = ResearchPlanningAgent()
        self.lit_agent = LiteratureDiscoveryAgent()
        self.analyzer = ResearchAnalysisAgent()
        self.cross_domain = CrossDomainDiscoveryAgent()
        self.gap_agent = GapDetectionAgent()
        self.hypo_agent = HypothesisGenerationAgent()
        self.reviewer = CriticalReviewerAgent()
        self.kg_service = KnowledgeGraphService()

    def update_project_status(
        self,
        db: Session,
        project_id: str,
        status: str,
        stage: str,
        progress: int,
        message: str
    ):
        proj = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
        if proj:
            proj.status = status
            proj.current_stage = stage
            proj.progress = progress
            proj.status_message = message
            proj.updated_at = datetime.now(timezone.utc)
            if status == "completed":
                proj.completed_at = datetime.now(timezone.utc)

            # Record in workflow execution
            wf = db.query(WorkflowExecution).filter(WorkflowExecution.project_id == project_id).first()
            if not wf:
                wf = WorkflowExecution(
                    project_id=project_id,
                    current_stage=stage,
                    progress=progress,
                    status="running" if status == "processing" else status,
                    logs=[]
                )
                db.add(wf)
            else:
                wf.current_stage = stage
                wf.progress = progress
                wf.status = "running" if status == "processing" else status
                logs = list(wf.logs or [])
                logs.append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "stage": stage,
                    "message": message,
                    "progress": progress
                })
                wf.logs = logs

            db.commit()

    async def execute_workflow(self, project_id: str, db: Optional[Session] = None):
        """
        Executes the full end-to-end multi-agent research workflow.
        Can run as background task.
        """
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True
        try:
            proj = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
            if not proj:
                logger.error(f"Project {project_id} not found.")
                return

            # Stage 1: Planning
            self.update_project_status(
                db, project_id, "processing", "planning", 10, "Research Planning Agent formulating investigation strategy"
            )
            plan = self.planner.plan_research(proj.question, proj.domain)
            if not proj.domain and plan.get("domain"):
                proj.domain = plan["domain"]
                db.commit()

            # Stage 2: Literature Discovery
            self.update_project_status(
                db, project_id, "processing", "literature_discovery", 25, "Discovering academic literature and preprints"
            )
            search_queries = plan.get("suggested_search_queries", [proj.question])
            lit_res = await self.lit_agent.discover_literature(db, project_id, search_queries)

            # Stage 3: Document Analysis & Finding Extraction
            self.update_project_status(
                db, project_id, "processing", "literature_analysis", 45, "Extracting evidence-backed findings and parameters"
            )
            
            # Analyze all local uploaded documents first
            docs = db.query(Document).filter(Document.project_id == project_id).all()
            for doc in docs:
                # Ensure a Source exists for this uploaded document
                src = db.query(Source).filter(Source.document_id == doc.id).first()
                if not src:
                    src = Source(
                        project_id=project_id,
                        document_id=doc.id,
                        source_type="uploaded_document",
                        citation_label=doc.filename,
                        metadata_info={"filename": doc.filename, "pages": doc.page_count}
                    )
                    db.add(src)
                    db.commit()
                
                doc_text = doc.extracted_text or ""
                self.analyzer.analyze_source_document(db, project_id, src, doc_text)

            # Also analyze discovered literature abstracts
            paper_sources = db.query(Source).filter(
                Source.project_id == project_id,
                Source.source_type == "external_paper"
            ).all()
            for ps in paper_sources:
                paper = ps.paper
                if paper and paper.abstract:
                    self.analyzer.analyze_source_document(db, project_id, ps, paper.abstract)

            all_findings = proj.findings

            # Stage 4: Cross-Domain Concept & Relationship Discovery
            self.update_project_status(
                db, project_id, "processing", "cross_domain_discovery", 60, "Identifying cross-domain relationships and concept graphs"
            )
            relationships = self.cross_domain.discover_relationships(db, project_id, all_findings)

            # Stage 5: Research Gap & Contradiction Detection
            self.update_project_status(
                db, project_id, "processing", "gap_detection", 75, "Detecting unanswered questions, contradictions and methodological gaps"
            )
            gaps = self.gap_agent.detect_gaps(db, project_id, all_findings)

            # Stage 6: Hypothesis Synthesis
            self.update_project_status(
                db, project_id, "processing", "hypothesis_generation", 85, "Synthesizing testable research hypotheses"
            )
            hypotheses = self.hypo_agent.generate_hypotheses(db, project_id, all_findings, gaps, relationships)

            # Stage 7: Critical Review
            self.update_project_status(
                db, project_id, "processing", "critical_review", 95, "Independent critical review of hypotheses"
            )
            for hypo in hypotheses:
                self.reviewer.review_hypothesis(db, hypo)

            # Stage 8: Final Knowledge Graph Rebuilding
            self.kg_service.build_from_project(db, project_id)

            # Completion
            self.update_project_status(
                db, project_id, "completed", "completed", 100, "Autonomous research workflow successfully completed"
            )

        except Exception as e:
            logger.exception(f"Workflow execution failure for project {project_id}: {e}")
            self.update_project_status(
                db, project_id, "failed", "error", 0, f"Workflow execution encountered an error: {str(e)}"
            )
        finally:
            if should_close:
                db.close()
