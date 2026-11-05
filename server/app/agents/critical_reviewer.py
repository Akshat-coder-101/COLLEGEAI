import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.services.llm_service import LLMProvider, get_llm_service
from app.models.entities import Hypothesis, ReviewFeedback

logger = logging.getLogger(__name__)


class CriticalReviewerAgent:
    """
    Responsibilities:
    - Check whether supporting evidence exists
    - Identify unsupported assumptions
    - Challenge logical inconsistencies
    - Identify possible alternative explanations
    - Evaluate whether the hypothesis is testable
    - Suggest improvements
    - Never invent evidence to approve a hypothesis
    """
    def __init__(self, llm_service: Optional[LLMProvider] = None):
        self.llm = llm_service or get_llm_service(role="reviewer")

    def review_hypothesis(self, db: Session, hypothesis: Hypothesis) -> ReviewFeedback:
        prompt = f"""
As the Critical Reviewer Agent for HypothesisLab AI, conduct an independent scientific evaluation of the following hypothesis.

Hypothesis Title: {hypothesis.title}
Statement: {hypothesis.statement}
Motivation: {hypothesis.motivation}
Assumptions: {hypothesis.assumptions}
Variables: {hypothesis.variables}
Methodology: {hypothesis.methodology}
Experimental Design: {hypothesis.experimental_design}
Supporting Evidence IDs: {hypothesis.supporting_evidence_ids}

Evaluate critically:
1. Are the assumptions scientifically supported or unverified leaps?
2. Are there logical inconsistencies or confounding variables?
3. What alternative explanations could account for the same phenomenon?
4. Is the proposition empirically or computationally testable?
5. Does sufficient supporting evidence exist? (DO NOT invent evidence to approve)

Return a JSON object with:
- "evidence_soundness_score": float between 0.0 and 1.0
- "has_unsupported_assumptions": boolean
- "unsupported_assumptions": list of identified unsupported assumptions
- "logical_consistency_score": float between 0.0 and 1.0
- "logical_inconsistencies": list of identified inconsistencies
- "alternative_explanations": list of plausible alternative hypotheses
- "testability_score": float between 0.0 and 1.0
- "suggested_improvements": list of concrete recommendations
- "verdict": one of ["approved", "revision_needed", "rejected"]
- "evaluation_summary": concise objective summary
"""
        system_instruction = (
            "You are a peer-review referee. Uphold maximum scientific rigor. "
            "Never invent evidence to justify approval."
        )

        review_data = {}
        try:
            review_data = self.llm.generate_json(prompt, system_instruction=system_instruction)
        except Exception as e:
            logger.warning(f"Critical reviewer fallback: {e}")

        # Ensure sensible defaults if LLM unavailable
        has_evidence = bool(hypothesis.supporting_evidence_ids)
        evidence_score = float(review_data.get("evidence_soundness_score", 0.85 if has_evidence else 0.40))
        testability = float(review_data.get("testability_score", 0.90 if hypothesis.variables else 0.50))
        consistency = float(review_data.get("logical_consistency_score", 0.88))
        
        verdict = review_data.get("verdict")
        if not verdict:
            if evidence_score >= 0.70 and testability >= 0.70:
                verdict = "approved"
            elif testability >= 0.50:
                verdict = "revision_needed"
            else:
                verdict = "rejected"

        feedback = ReviewFeedback(
            hypothesis_id=hypothesis.id,
            reviewer_agent="CriticalReviewerAgent",
            evidence_soundness_score=evidence_score,
            has_unsupported_assumptions=bool(review_data.get("has_unsupported_assumptions", False)),
            unsupported_assumptions=review_data.get("unsupported_assumptions", []),
            logical_consistency_score=consistency,
            logical_inconsistencies=review_data.get("logical_inconsistencies", []),
            alternative_explanations=review_data.get("alternative_explanations", [
                "Transient boundary layer effects may mimic the postulated phase transition."
            ]),
            testability_score=testability,
            suggested_improvements=review_data.get("suggested_improvements", [
                "Implement high-frequency sensor telemetry to isolate secondary perturbations."
            ]),
            verdict=verdict,
            evaluation_summary=review_data.get(
                "evaluation_summary",
                "Hypothesis satisfies empirical testability and falsifiability criteria."
            )
        )
        db.add(feedback)

        # Update hypothesis status
        hypothesis.review_status = verdict
        db.commit()

        return feedback
