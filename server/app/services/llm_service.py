import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import settings

logger = logging.getLogger(__name__)


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
    LangChain-powered Gemini provider using ChatGoogleGenerativeAI.
    """
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        self._llm = None

        if self.api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self._llm = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=self.api_key,
                    temperature=0.2
                )
            except Exception as e:
                logger.warning(f"Failed to initialize ChatGoogleGenerativeAI: {e}")

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        if not self._llm:
            raise RuntimeError("Gemini API is not configured. Set GEMINI_API_KEY.")
        
        messages = []
        if system_instruction:
            messages.append(SystemMessage(content=system_instruction))
        messages.append(HumanMessage(content=prompt))

        response = self._llm.invoke(messages)
        return response.content or ""

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
    """
    def __init__(self):
        self.call_history = []

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        self.call_history.append({"prompt": prompt, "system_instruction": system_instruction})
        return "Deterministic analysis response based on provided literature."

    def generate_json(self, prompt: str, system_instruction: Optional[str] = None) -> Dict[str, Any]:
        self.call_history.append({"prompt": prompt, "system_instruction": system_instruction})
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

        return {
            "status": "success",
            "findings": [],
            "analysis": "Mock analysis generated."
        }

    def get_embedding(self, text: str) -> List[float]:
        return [(hash(text + str(i)) % 1000) / 1000.0 for i in range(128)]


def get_llm_service() -> LLMProvider:
    if settings.GEMINI_API_KEY:
        try:
            return LangChainGeminiProvider()
        except Exception as e:
            logger.warning(f"Falling back to MockLLMProvider: {e}")
            return MockLLMProvider()
    return MockLLMProvider()
