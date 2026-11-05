import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
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


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        self._client = None

        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize google-genai Client: {e}")

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        if not self._client:
            raise RuntimeError("Gemini API client is not configured. Set GEMINI_API_KEY.")
        
        config = {}
        if system_instruction:
            config["system_instruction"] = system_instruction

        response = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config if config else None,
        )
        return response.text or ""

    def generate_json(self, prompt: str, system_instruction: Optional[str] = None) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("Gemini API client is not configured. Set GEMINI_API_KEY.")
        
        json_instruction = (
            (system_instruction or "") + 
            "\n\nCRITICAL: Respond ONLY with a valid JSON object. No Markdown code fences, no prefix, no postfix."
        )
        response_text = self.generate_text(prompt, system_instruction=json_instruction)
        
        # Clean response text if code block backticks exist
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
            logger.error(f"Failed to parse LLM JSON: {e}\nRaw output: {response_text}")
            raise ValueError(f"LLM output could not be parsed as JSON: {e}")

    def get_embedding(self, text: str) -> List[float]:
        if not self._client:
            raise RuntimeError("Gemini API client is not configured.")
        try:
            response = self._client.models.embed_content(
                model=settings.EMBEDDING_MODEL,
                contents=text
            )
            return response.embedding.values
        except Exception as e:
            logger.warning(f"Embedding generation error: {e}")
            return [0.0] * 768


class MockLLMProvider(LLMProvider):
    """
    Predictable LLM provider for unit tests, offline environments,
    and fallback operation without external API dependencies.
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

        # Default fallback structure
        return {
            "status": "success",
            "findings": [],
            "analysis": "Mock analysis generated."
        }

    def get_embedding(self, text: str) -> List[float]:
        # Simple deterministic vector based on text length and hashing
        seed = len(text)
        return [(hash(text + str(i)) % 1000) / 1000.0 for i in range(128)]


def get_llm_service() -> LLMProvider:
    if settings.GEMINI_API_KEY:
        try:
            return GeminiProvider()
        except Exception as e:
            logger.warning(f"Falling back to MockLLMProvider: {e}")
            return MockLLMProvider()
    return MockLLMProvider()
