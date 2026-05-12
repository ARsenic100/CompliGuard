"""
Toxicity / Abusive Content Detection Agent
=============================================
Uses LLM moderation prompts to detect hate speech, threats,
harassment, illegal activities, and toxic content.
"""

from __future__ import annotations

import re
from typing import Any

from app.models.schemas import SeverityLevel, ViolationCategory
from app.prompts.templates import TOXICITY_ANALYSIS_PROMPT, TOXICITY_SYSTEM_PROMPT
from app.services.llm_service import LLMServiceError, get_llm_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Quick pre-screening keywords (not exhaustive — LLM does the heavy lifting)
TOXICITY_KEYWORDS = [
    "kill", "murder", "bomb", "attack", "destroy", "terrorist",
    "hate", "slur", "racist", "sexist",
    "threat", "harass", "abuse", "exploit",
    "illegal", "fraud", "launder", "bribe",
]


class ToxicityDetector:
    """Abusive/Unlawful Content Detection Agent using LLM moderation."""

    def __init__(self) -> None:
        self.llm_service = get_llm_service()
        logger.info("Toxicity Detector initialized")

    def detect(self, text: str, page_number: int, rules: list[dict[str, Any]] | None = None, rag_context: str = "") -> list[dict[str, Any]]:
        """Detect abusive/unlawful content in text."""
        if not text.strip():
            return []

        # Quick pre-screen: only send to LLM if potentially toxic content exists
        has_potential_toxicity = self._pre_screen(text)

        violations: list[dict[str, Any]] = []
        if has_potential_toxicity:
            llm_violations = self._detect_with_llm(text, page_number, rag_context)
            violations.extend(llm_violations)
        else:
            # Still run LLM for subtle/contextual toxicity on shorter texts
            if len(text) < 2000:
                llm_violations = self._detect_with_llm(text, page_number, rag_context)
                violations.extend(llm_violations)

        logger.info(f"Page {page_number}: Found {len(violations)} toxicity violations")
        return violations

    def _pre_screen(self, text: str) -> bool:
        """Quick keyword pre-screening to decide if LLM analysis is needed."""
        text_lower = text.lower()
        for keyword in TOXICITY_KEYWORDS:
            if keyword in text_lower:
                return True
        return False

    def _detect_with_llm(self, text: str, page_number: int, rag_context: str = "") -> list[dict[str, Any]]:
        """Detect toxic content using LLM moderation prompt."""
        if not self.llm_service.is_available:
            return []

        analysis_text = text[:4000] if len(text) > 4000 else text

        try:
            prompt = TOXICITY_ANALYSIS_PROMPT.format(page_number=page_number, text=analysis_text, rag_context=rag_context)
            result = self.llm_service.analyze(TOXICITY_SYSTEM_PROMPT, prompt, expect_json=True)

            if not isinstance(result, dict) or not result.get("violations_found", False):
                return []

            violations = []
            for v in result.get("violations", []):
                violations.append({
                    "category": ViolationCategory.TOXICITY.value,
                    "violation_type": v.get("violation_type", "Toxic Content"),
                    "severity": v.get("severity", "High"),
                    "confidence": min(1.0, max(0.0, float(v.get("confidence", 0.7)))),
                    "page_number": page_number,
                    "matched_text": v.get("matched_text", "")[:200],
                    "reason": v.get("reason", "AI detected potentially toxic content"),
                    "remediation": "Remove or revise the flagged content. Escalate to legal/compliance if needed.",
                    "detected_by": "llm",
                })
            return violations

        except (LLMServiceError, Exception) as e:
            logger.error(f"LLM toxicity detection failed for page {page_number}: {e}")
            return []
