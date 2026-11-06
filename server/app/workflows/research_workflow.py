import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, TypedDict
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, START, END

import app.database.session as db_session_module
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

logger = logging.getLogger(__name__)


class ResearchGraphState(TypedDict, total=False):
    project_id: str
    question: str
    domain: Optional[str]
    plan: Dict[str, Any]
    search_queries: List[str]
    current_stage: str
    progress: int
    status: str
    status_message: str
    db: Any


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
        self.graph = self._build_langgraph()

    def _update_db_status(self, db: Session, project_id: str, status: str, stage: str, progress: int, message: str):
        proj = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
        if proj:
            proj.status = status
            proj.current_stage = stage
            proj.progress = progress
            proj.status_message = message
            proj.updated_at = datetime.now(timezone.utc)
            if status == "completed":
                proj.completed_at = datetime.now(timezone.utc)

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

    def _build_langgraph(self):
        """
        Constructs a LangGraph StateGraph representing the autonomous multi-agent pipeline.
        """
        builder = StateGraph(ResearchGraphState)

        # 1. Plan Node
        async def plan_node(state: ResearchGraphState) -> Dict[str, Any]:
            db: Session = state["db"]
            p_id = state["project_id"]
            self._update_db_status(db, p_id, "processing", "planning", 10, "Formulating research plan")
            
            plan = self.planner.plan_research(state["question"], state.get("domain"))
            queries = plan.get("suggested_search_queries", [state["question"]])

            proj = db.query(ResearchProject).filter(ResearchProject.id == p_id).first()
            if proj and not proj.domain and plan.get("domain"):
                proj.domain = plan["domain"]
                db.commit()

            return {
                "plan": plan,
                "domain": plan.get("domain", state.get("domain")),
                "search_queries": queries,
                "current_stage": "planning",
                "progress": 10
            }

        # 2. Literature Discovery Node
        async def literature_node(state: ResearchGraphState) -> Dict[str, Any]:
            db: Session = state["db"]
            p_id = state["project_id"]
            self._update_db_status(db, p_id, "processing", "literature_discovery", 25, "Discovering research literature")
            
            queries = state.get("search_queries", [state["question"]])
            await self.lit_agent.discover_literature(db, p_id, queries)

            return {
                "current_stage": "literature_discovery",
                "progress": 25
            }

        # 3. Document Analysis Node
        async def analysis_node(state: ResearchGraphState) -> Dict[str, Any]:
            db: Session = state["db"]
            p_id = state["project_id"]
            self._update_db_status(db, p_id, "processing", "literature_analysis", 45, "Extracting evidence-backed findings")

            # Analyze uploaded PDFs
            docs = db.query(Document).filter(Document.project_id == p_id).all()
            for doc in docs:
                src = db.query(Source).filter(Source.document_id == doc.id).first()
                if not src:
                    src = Source(
                        project_id=p_id,
                        document_id=doc.id,
                        source_type="uploaded_document",
                        citation_label=doc.filename,
                        metadata_info={"filename": doc.filename, "pages": doc.page_count}
                    )
                    db.add(src)
                    db.commit()
                self.analyzer.analyze_source_document(db, p_id, src, doc.extracted_text or "")

            # Analyze external paper abstracts
            external_sources = db.query(Source).filter(
                Source.project_id == p_id,
                Source.source_type == "external_paper"
            ).all()
            for es in external_sources:
                if es.paper and es.paper.abstract:
                    self.analyzer.analyze_source_document(db, p_id, es, es.paper.abstract)

            return {
                "current_stage": "literature_analysis",
                "progress": 45
            }

        # 4. Cross Domain Discovery Node
        async def cross_domain_node(state: ResearchGraphState) -> Dict[str, Any]:
            db: Session = state["db"]
            p_id = state["project_id"]
            self._update_db_status(db, p_id, "processing", "cross_domain_discovery", 60, "Synthesizing cross-domain relationships")

            proj = db.query(ResearchProject).filter(ResearchProject.id == p_id).first()
            findings = proj.findings if proj else []
            self.cross_domain.discover_relationships(db, p_id, findings)

            return {
                "current_stage": "cross_domain_discovery",
                "progress": 60
            }

        # 5. Gap Detection Node
        async def gaps_node(state: ResearchGraphState) -> Dict[str, Any]:
            db: Session = state["db"]
            p_id = state["project_id"]
            self._update_db_status(db, p_id, "processing", "gap_detection", 75, "Detecting scientific gaps and contradictions")

            proj = db.query(ResearchProject).filter(ResearchProject.id == p_id).first()
            findings = proj.findings if proj else []
            self.gap_agent.detect_gaps(db, p_id, findings)

            return {
                "current_stage": "gap_detection",
                "progress": 75
            }

        # 6. Hypothesis Generation Node
        async def hypotheses_node(state: ResearchGraphState) -> Dict[str, Any]:
            db: Session = state["db"]
            p_id = state["project_id"]
            self._update_db_status(db, p_id, "processing", "hypothesis_generation", 85, "Synthesizing testable hypotheses")

            proj = db.query(ResearchProject).filter(ResearchProject.id == p_id).first()
            findings = proj.findings if proj else []
            gaps = proj.gaps if proj else []
            rels = proj.relationships_data if proj else []
            q_text = proj.question if proj else None
            t_text = proj.title if proj else None
            self.hypo_agent.generate_hypotheses(db, p_id, findings, gaps, rels, question=q_text, title=t_text)

            return {
                "current_stage": "hypothesis_generation",
                "progress": 85
            }

        # 7. Critical Review Node
        async def review_node(state: ResearchGraphState) -> Dict[str, Any]:
            db: Session = state["db"]
            p_id = state["project_id"]
            self._update_db_status(db, p_id, "processing", "critical_review", 95, "Independent critical review")

            proj = db.query(ResearchProject).filter(ResearchProject.id == p_id).first()
            hypos = proj.hypotheses if proj else []
            for h in hypos:
                self.reviewer.review_hypothesis(db, h)

            return {
                "current_stage": "critical_review",
                "progress": 95
            }

        # 8. In Silico Computational Simulation Node
        async def simulation_node(state: ResearchGraphState) -> Dict[str, Any]:
            db: Session = state["db"]
            p_id = state["project_id"]
            proj = db.query(ResearchProject).filter(ResearchProject.id == p_id).first()
            
            if proj and proj.enable_simulation and proj.hypotheses:
                self._update_db_status(db, p_id, "processing", "simulation", 95, "Running in silico computational validation")
                try:
                    from app.workflows.simulation_workflow import SimulationWorkflowRunner
                    from app.models.entities import Experiment
                    
                    top_hypo = proj.hypotheses[0]
                    exp = db.query(Experiment).filter(Experiment.hypothesis_id == top_hypo.id).first()
                    if not exp:
                        exp = Experiment(
                            hypothesis_id=top_hypo.id,
                            simulation_path="model_builder",
                            status="pending"
                        )
                        db.add(exp)
                        db.commit()
                    
                    sim_runner = SimulationWorkflowRunner()
                    await sim_runner.run_simulation_langgraph(exp.id, db)
                except Exception as e:
                    logger.warning(f"In silico simulation execution error: {e}")

            return {
                "current_stage": "simulation",
                "progress": 98
            }

        # 9. Final Knowledge Graph Node
        async def knowledge_graph_node(state: ResearchGraphState) -> Dict[str, Any]:
            db: Session = state["db"]
            p_id = state["project_id"]
            self.kg_service.build_from_project(db, p_id)
            self._update_db_status(db, p_id, "completed", "completed", 100, "Research workflow completed")

            return {
                "current_stage": "completed",
                "progress": 100,
                "status": "completed"
            }

        # Connect LangGraph nodes
        builder.add_node("plan", plan_node)
        builder.add_node("literature", literature_node)
        builder.add_node("analysis", analysis_node)
        builder.add_node("cross_domain", cross_domain_node)
        builder.add_node("gaps", gaps_node)
        builder.add_node("hypotheses", hypotheses_node)
        builder.add_node("review", review_node)
        builder.add_node("simulation", simulation_node)
        builder.add_node("knowledge_graph", knowledge_graph_node)

        builder.add_edge(START, "plan")
        builder.add_edge("plan", "literature")
        builder.add_edge("literature", "analysis")
        builder.add_edge("analysis", "cross_domain")
        builder.add_edge("cross_domain", "gaps")
        builder.add_edge("gaps", "hypotheses")
        builder.add_edge("hypotheses", "review")
        builder.add_edge("review", "simulation")
        builder.add_edge("simulation", "knowledge_graph")
        builder.add_edge("knowledge_graph", END)

        return builder.compile()

    async def execute_workflow(self, project_id: str, db: Optional[Session] = None):
        """
        Executes the LangGraph StateGraph research workflow.
        """
        should_close = False
        if db is None:
            db = db_session_module.SessionLocal()
            should_close = True

        try:
            proj = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
            if not proj:
                logger.error(f"Project {project_id} not found.")
                return

            initial_state: ResearchGraphState = {
                "project_id": project_id,
                "question": proj.question,
                "domain": proj.domain,
                "status": "processing",
                "current_stage": "planning",
                "progress": 5,
                "db": db
            }

            # Invoke the LangGraph workflow
            await self.graph.ainvoke(initial_state)

        except Exception as e:
            logger.exception(f"LangGraph research workflow failure: {e}")
            self._update_db_status(db, project_id, "failed", "error", 0, f"Workflow error: {str(e)}")
        finally:
            if should_close:
                db.close()
