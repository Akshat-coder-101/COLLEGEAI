from typing import Dict, Any, List, Optional
import networkx as nx
from sqlalchemy.orm import Session
from app.models.entities import (
    ResearchProject,
    Document,
    ResearchPaper,
    Source,
    Evidence,
    Finding,
    Concept,
    Variable,
    RelationshipEntity,
    ResearchGap,
    Hypothesis,
)


class KnowledgeGraphService:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_from_project(self, db: Session, project_id: str) -> nx.DiGraph:
        """
        Reconstructs the directed knowledge graph from database entities for a project.
        """
        self.graph.clear()

        # 1. Add Research Project Node
        project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
        if not project:
            return self.graph

        self.graph.add_node(
            project.id,
            node_type="Project",
            title=project.title,
            question=project.question
        )

        # 2. Add Sources and Papers
        sources = db.query(Source).filter(Source.project_id == project_id).all()
        for src in sources:
            self.graph.add_node(
                src.id,
                node_type="Source",
                label=src.citation_label,
                source_type=src.source_type
            )
            self.graph.add_edge(project.id, src.id, relation="investigates")

        # 3. Add Findings and connect to Sources
        findings = db.query(Finding).filter(Finding.project_id == project_id).all()
        for f in findings:
            self.graph.add_node(
                f.id,
                node_type="Finding",
                description=f.description,
                is_extracted=f.is_extracted,
                confidence=f.confidence
            )
            self.graph.add_edge(f.source_id, f.id, relation="supports")

        # 4. Add Concepts
        concepts = db.query(Concept).filter(Concept.project_id == project_id).all()
        for c in concepts:
            self.graph.add_node(
                c.id,
                node_type="Concept",
                name=c.name,
                domain=c.domain
            )

        # 5. Add Relationships
        relationships = db.query(RelationshipEntity).filter(RelationshipEntity.project_id == project_id).all()
        for rel in relationships:
            self.graph.add_edge(
                rel.source_concept_id,
                rel.target_concept_id,
                relation_id=rel.id,
                relation=rel.relation_type,
                connection_type=rel.connection_type,  # explicitly_supported OR ai_inferred
                rationale=rel.rationale
            )

        # 6. Add Research Gaps
        gaps = db.query(ResearchGap).filter(ResearchGap.project_id == project_id).all()
        for g in gaps:
            self.graph.add_node(
                g.id,
                node_type="ResearchGap",
                title=g.title,
                gap_type=g.gap_type
            )
            # Connect supporting sources to the gap
            for src_id in (g.supporting_sources or []):
                if self.graph.has_node(src_id):
                    self.graph.add_edge(src_id, g.id, relation="indicates_gap")

        # 7. Add Hypotheses
        hypotheses = db.query(Hypothesis).filter(Hypothesis.project_id == project_id).all()
        for h in hypotheses:
            self.graph.add_node(
                h.id,
                node_type="Hypothesis",
                title=h.title,
                statement=h.statement,
                review_status=h.review_status
            )
            # Connect evidence items / findings to hypothesis
            for ev_id in (h.supporting_evidence_ids or []):
                if self.graph.has_node(ev_id):
                    self.graph.add_edge(ev_id, h.id, relation="evidences")

        return self.graph

    def trace_hypothesis_provenance(self, hypothesis_id: str) -> List[Dict[str, Any]]:
        """
        Backtracks the graph from hypothesis to its original sources, ensuring complete provenance.
        """
        if not self.graph.has_node(hypothesis_id):
            return []

        provenance_chains = []
        # Find all ancestor nodes of the hypothesis
        ancestors = nx.ancestors(self.graph, hypothesis_id)
        for anc in ancestors:
            node_data = self.graph.nodes[anc]
            if node_data.get("node_type") in ("Source", "Finding", "ResearchGap"):
                provenance_chains.append({
                    "node_id": anc,
                    "type": node_data.get("node_type"),
                    "details": node_data
                })
        return provenance_chains

    def export_graph_json(self) -> Dict[str, Any]:
        """
        Exports graph into JSON format with nodes and edges.
        """
        nodes = []
        for n, data in self.graph.nodes(data=True):
            nodes.append({"id": n, **data})

        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({"source": u, "target": v, **data})

        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }
