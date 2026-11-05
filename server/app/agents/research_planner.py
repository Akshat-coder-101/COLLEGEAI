import logging
from typing import Dict, Any, List
from app.services.llm_service import LLMProvider, get_llm_service

logger = logging.getLogger(__name__)


class ResearchPlanningAgent:
    """
    Responsibilities:
    - Understand user's research question
    - Determine research domain
    - Identify what information needs to be investigated
    - Create a structured research plan
    - Decide which external sources are needed
    - Identify missing information
    """
    def __init__(self, llm_service: LLMProvider = None):
        self.llm = llm_service or get_llm_service()

    def plan_research(self, question: str, domain_hint: str = None) -> Dict[str, Any]:
        prompt = f"""
You are the Lead Scientific Research Planning Agent for HypothesisLab AI.
Analyze the user's research inquiry and output a structured research plan.

Research Question: "{question}"
Domain Hint: "{domain_hint or 'Not specified'}"

Produce a structured JSON response with:
1. "objective": concise statement of research objective
2. "domain": identified primary scientific discipline
3. "investigation_plan": list of concrete investigation stages
4. "relevant_areas": list of key scientific subfields to examine
5. "suggested_search_queries": list of 3-5 academic literature search queries
6. "required_evidence": list of empirical/quantifiable evidence needed to answer the question
"""
        system_instruction = (
            "You are a rigorous scientific research planner. "
            "Formulate comprehensive, verifiable investigation strategies."
        )

        try:
            result = self.llm.generate_json(prompt, system_instruction=system_instruction)
            return {
                "objective": result.get("objective", f"Investigate {question}"),
                "domain": result.get("domain", domain_hint or "Interdisciplinary Sciences"),
                "investigation_plan": result.get("investigation_plan", [
                    "Literature retrieval and source indexing",
                    "Evidence extraction and parameter cataloging",
                    "Contradiction and gap detection",
                    "Hypothesis synthesis and critical review"
                ]),
                "relevant_areas": result.get("relevant_areas", ["Core Domain"]),
                "suggested_search_queries": result.get("suggested_search_queries", [question]),
                "required_evidence": result.get("required_evidence", ["Empirical measurements", "Peer-reviewed findings"])
            }
        except Exception as e:
            logger.warning(f"Planning agent LLM fallback: {e}")
            return {
                "objective": f"Investigate empirical evidence and theoretical models for: {question}",
                "domain": domain_hint or "General Science",
                "investigation_plan": [
                    "Extract findings from uploaded documents",
                    "Query external literature databases",
                    "Detect limitations and research gaps",
                    "Formulate testable hypotheses"
                ],
                "relevant_areas": ["Empirical Evaluation", "Methodology"],
                "suggested_search_queries": [question, f"{question} experimental findings"],
                "required_evidence": ["Quantitative parameter bounds", "Empirically validated models"]
            }
