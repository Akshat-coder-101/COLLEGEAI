import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import settings
from app.services.rate_limiter import global_rate_limiter, RateLimiter

logger = logging.getLogger(__name__)

# Role to model resolution
ROLE_MODEL_MAPPING = {
    "planner": lambda: settings.MODEL_PLANNER,
    "analyzer": lambda: settings.MODEL_ANALYZER,
    "cross_domain": lambda: settings.MODEL_CROSS_DOMAIN,
    "gaps": lambda: settings.MODEL_GAP_DETECTION,
    "hypothesis": lambda: settings.MODEL_HYPOTHESIS,
    "reviewer": lambda: settings.MODEL_REVIEWER,
    "simulation": lambda: settings.MODEL_SIMULATION,
}


class LLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def generate_json(self, prompt: str, system_instruction: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        pass


class LangChainGeminiProvider(LLMProvider):
    """
    Multi-model LangChain provider with sliding-window rate limit protection,
    per-model RPM/RPD management, and automatic failover.
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        rate_limiter: Optional[RateLimiter] = None
    ):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.preferred_model = model_name or settings.GEMINI_MODEL
        self.model_name = self.preferred_model
        self.limiter = rate_limiter or global_rate_limiter
        self._llm_cache: Dict[str, Any] = {}

    def _get_client_for_model(self, model: str):
        if model not in self._llm_cache:
            from langchain_google_genai import ChatGoogleGenerativeAI
            self._llm_cache[model] = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=self.api_key,
                temperature=0.2
            )
        return self._llm_cache[model]

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        if not self.api_key:
            raise RuntimeError("Gemini API key is not configured. Set GEMINI_API_KEY.")

        messages = []
        if system_instruction:
            messages.append(SystemMessage(content=system_instruction))
        messages.append(HumanMessage(content=prompt))

        # Attempt with effective model and failover pool
        current_model = self.limiter.get_effective_model(self.preferred_model)
        candidates = [current_model] + [
            m for m in RateLimiter.FAILOVER_POOLS.get(current_model, [])
            if m != current_model
        ]

        last_error = None
        for candidate in candidates:
            try:
                # 1. Enforce rate limit & polite spacing
                self.limiter.acquire(candidate)
                
                # 2. Invoke model
                llm = self._get_client_for_model(candidate)
                response = llm.invoke(messages)
                content = response.content
                if isinstance(content, list):
                    text_parts = []
                    for part in content:
                        if isinstance(part, dict) and "text" in part:
                            text_parts.append(part["text"])
                        elif isinstance(part, str):
                            text_parts.append(part)
                        else:
                            text_parts.append(str(part))
                    return "".join(text_parts)
                return str(content or "")

            except Exception as e:
                err_str = str(e).lower()
                if "429" in err_str or "resource_exhausted" in err_str or "quota" in err_str:
                    logger.warning(f"Rate limit reached on {candidate}. Triggering failover cooldown.")
                    self.limiter.record_cooldown(candidate, duration_seconds=45.0)
                    last_error = e
                    continue
                else:
                    logger.error(f"Error invoking model {candidate}: {e}")
                    raise e

        if last_error:
            raise RuntimeError(f"All model candidates in failover pool exhausted quotas: {last_error}")

        return ""

    def generate_json(self, prompt: str, system_instruction: Optional[str] = None) -> Dict[str, Any]:
        json_instruction = (
            (system_instruction or "") + 
            "\n\nCRITICAL: Respond ONLY with a valid JSON object. Do not include markdown code fences or conversational text."
        )
        response_text = self.generate_text(prompt, system_instruction=json_instruction)
        
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON: {e}\nRaw: {response_text}")
            raise ValueError(f"LLM output could not be parsed as JSON: {e}")

    def get_embedding(self, text: str) -> List[float]:
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            response = client.models.embed_content(
                model=settings.EMBEDDING_MODEL,
                contents=text
            )
            return response.embedding.values
        except Exception as e:
            logger.warning(f"Embedding error: {e}")
            return [0.0] * 768


class MockLLMProvider(LLMProvider):
    """
    Deterministic mock provider for unit tests and offline environments.
    Tracks model role requests and respects the rate limiter.
    """
    def __init__(self, model_name: str = "mock-model", rate_limiter: Optional[RateLimiter] = None):
        self.model_name = model_name
        self.limiter = rate_limiter or global_rate_limiter
        self.call_history: List[Dict[str, Any]] = []

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        self.limiter.acquire(self.model_name)
        self.call_history.append({
            "model": self.model_name,
            "prompt": prompt,
            "system_instruction": system_instruction
        })
        return f"Deterministic response from {self.model_name}."

    def generate_json(self, prompt: str, system_instruction: Optional[str] = None) -> Dict[str, Any]:
        self.limiter.acquire(self.model_name)
        self.call_history.append({
            "model": self.model_name,
            "prompt": prompt,
            "system_instruction": system_instruction
        })
        prompt_lower = prompt.lower()
        
        if "research_plan" in prompt_lower or "investigate" in prompt_lower:
            return {
                "objective": "Investigate mechanisms and empirical evidence for the research question",
                "domain": "Biomedical / Materials Science",
                "investigation_plan": [
                    "Extract primary findings and parameters from sources",
                    "Identify inconsistencies or gaps in experimental conditions",
                    "Formulate cross-domain hypotheses and testable parameters"
                ],
                "relevant_areas": ["Domain A", "Domain B"],
                "suggested_search_queries": ["experimental evaluation", "comparative benchmark"],
                "required_evidence": ["Quantified effect sizes", "Empirical error bounds"]
            }
        
        if "gap" in prompt_lower:
            return {
                "gaps": [
                    {
                        "gap_type": "underexplored_condition",
                        "title": "Temperature dependency at extreme operating conditions",
                        "description": "Existing papers observe behavior at room temperature but lack validation under high thermal stress.",
                        "why_it_matters": "Critical for determining operational safety boundaries.",
                        "existing_coverage": "Room temperature trials (20-25 deg C) documented.",
                        "remaining_uncertainty": "Behavior above 100 deg C remains uncharacterized.",
                        "suggested_investigation": "Conduct thermal sweep experiments from 50 to 150 deg C.",
                        "supporting_sources": []
                    }
                ]
            }

        if "cross_domain" in prompt_lower or "relationship" in prompt_lower:
            return {
                "relationships": [
                    {
                        "source_concept": "Concept A",
                        "target_concept": "Concept B",
                        "relation_type": "correlates_with",
                        "connection_type": "ai_inferred",
                        "rationale": "Inferred from analogical principles in related physical systems.",
                        "source_references": []
                    }
                ]
            }

        if "critical_review" in prompt_lower or "reviewer" in prompt_lower:
            return {
                "evidence_soundness_score": 0.88,
                "has_unsupported_assumptions": False,
                "unsupported_assumptions": [],
                "logical_consistency_score": 0.92,
                "logical_inconsistencies": [],
                "alternative_explanations": ["Confounding environmental factors could influence rate constants"],
                "testability_score": 0.90,
                "suggested_improvements": ["Incorporate explicit control groups for ambient humidity"],
                "verdict": "approved",
                "evaluation_summary": "Strong hypothesis with sound empirical evidence from source documents."
            }

        if "peer-reviewed research" in prompt_lower or "scientific inquiry queries" in prompt_lower or "literature" in prompt_lower:
            return [
                {
                    "title": "Empirical parameter scaling in multi-phase regimes",
                    "authors": ["J. Miller", "A. Davis"],
                    "abstract": "Investigation of parameter scaling under thermal gradient of 300 K with measured rate constant k=0.012 s^-1.",
                    "publication_date": "2023",
                    "doi": "10.1038/s41586-023-00001-1",
                    "url": "https://doi.org/10.1038/s41586-023-00001-1"
                },
                {
                    "title": "Thermodynamic stability boundaries under operational stress",
                    "authors": ["L. Chen", "K. Tanaka"],
                    "abstract": "Analysis of phase boundary decomposition at 350 K with degradation rate 0.05% per hour.",
                    "publication_date": "2023",
                    "doi": "10.1038/s41586-023-00002-2",
                    "url": "https://doi.org/10.1038/s41586-023-00002-2"
                }
            ]

        return {
            "status": "success",
            "findings": [
                {
                    "description": "Rate constant scales with temperature following Arrhenius kinetics",
                    "methodology": "Spectroscopic measurements",
                    "parameters": [{"name": "Temperature", "value": 300.0, "unit": "K"}],
                    "supporting_quote": "The electrical resistivity rho was measured at 1.2e-5 Ohm*m at 300 K.",
                    "location": "Page 2, Section 3.1",
                    "limitations": "Evaluated only up to 450 K",
                    "confidence": 0.94
                }
            ],
            "analysis": f"Mock analysis generated by {self.model_name}."
        }

    def get_embedding(self, text: str) -> List[float]:
        return [(hash(text + str(i)) % 1000) / 1000.0 for i in range(128)]


def get_llm_service(
    role: Optional[str] = None,
    model_name: Optional[str] = None
) -> LLMProvider:
    """
    Returns an LLM service configured with the designated model for a specific agent role,
    protecting against rate-limit breaches across different tasks.
    """
    selected_model = model_name
    if not selected_model and role and role in ROLE_MODEL_MAPPING:
        selected_model = ROLE_MODEL_MAPPING[role]()
    
    if not selected_model:
        selected_model = settings.GEMINI_MODEL

    if settings.GEMINI_API_KEY:
        try:
            return LangChainGeminiProvider(model_name=selected_model)
        except Exception as e:
            logger.warning(f"Falling back to MockLLMProvider for {selected_model}: {e}")
            return MockLLMProvider(model_name=selected_model)
    return MockLLMProvider(model_name=selected_model)
