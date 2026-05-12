"""
Confidential Information Detection Agent
==========================================
Uses LLM semantic analysis to detect confidential, proprietary,
and sensitive business information in document text.
"""

from __future__ import annotations

import re
from typing import Any

from app.models.schemas import SeverityLevel, ViolationCategory
from app.prompts.templates import CONFIDENTIAL_ANALYSIS_PROMPT, CONFIDENTIAL_SYSTEM_PROMPT
from app.services.llm_service import LLMServiceError, get_llm_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

CONFIDENTIAL_KEYWORDS: dict[str, dict[str, Any]] = {
    "API Key / Token": {
        "patterns": [
            r'(?:api[_\-\s]?key|access[_\-\s]?token|secret[_\-\s]?key)\s*[=:]\s*["\']?[\w\-]{20,}',
            r'\b(?:sk|pk|api)[_\-](?:live|test|prod)[_\-][\w]{20,}\b',
            r'\bghp_[\w]{36,}\b',
            r'\bxox[bpsa]\-[\w\-]{10,}\b',
        ],
        "severity": SeverityLevel.CRITICAL,
    },
    "Password / Secret": {
        "patterns": [
            r'(?:password|passwd|pwd|secret)\s*[=:]\s*["\']?[^\s"\']{4,}',
            r'(?:BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY)',
        ],
        "severity": SeverityLevel.CRITICAL,
    },
    "NDA / Confidential Marking": {
        "patterns": [
            r'\b(?:CONFIDENTIAL|STRICTLY\s+CONFIDENTIAL|TOP\s+SECRET|PROPRIETARY|TRADE\s+SECRET)\b',
            r'\b(?:non[\-\s]?disclosure|NDA|confidentiality\s+agreement)\b',
        ],
        "severity": SeverityLevel.HIGH,
    },
    "Financial Data": {
        "patterns": [
            r'\b(?:revenue|profit|EBITDA|forecast|projection)\s*[:\-]?\s*\$?\d+',
            r'\b(?:Q[1-4]\s+\d{4}|FY\s*\d{2,4})\s+(?:revenue|earnings|forecast)',
        ],
        "severity": SeverityLevel.HIGH,
    },
}


class ConfidentialDetector:
    """Confidential Information Detection Agent using keyword pre-screening + LLM."""

    def __init__(self) -> None:
        self.llm_service = get_llm_service()
        logger.info("Confidential Detector initialized")

    def detect(self, text: str, page_number: int, rules: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        if not text.strip():
            return []
        violations: list[dict[str, Any]] = []
        violations.extend(self._detect_with_keywords(text, page_number))
        violations.extend(self._detect_with_llm(text, page_number))
        if rules:
            violations.extend(self._apply_custom_rules(text, page_number, rules))
        violations = self._deduplicate(violations)
        logger.info(f"Page {page_number}: Found {len(violations)} confidential violations")
        return violations

    def _detect_with_keywords(self, text: str, page_number: int) -> list[dict[str, Any]]:
        violations = []
        for conf_type, config in CONFIDENTIAL_KEYWORDS.items():
            for pattern in config["patterns"]:
                try:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        matched_text = match if isinstance(match, str) else match[0]
                        violations.append({
                            "category": ViolationCategory.CONFIDENTIAL.value,
                            "violation_type": conf_type,
                            "severity": config["severity"].value,
                            "confidence": 0.85,
                            "page_number": page_number,
                            "matched_text": matched_text.strip()[:200],
                            "reason": f"Pattern match: {conf_type} detected",
                            "remediation": f"Remove or redact the {conf_type.lower()} before sharing.",
                            "detected_by": "regex",
                        })
                except re.error as e:
                    logger.warning(f"Regex error for {conf_type}: {e}")
        return violations

    def _detect_with_llm(self, text: str, page_number: int) -> list[dict[str, Any]]:
        if not self.llm_service.is_available:
            return []
        analysis_text = text[:4000] if len(text) > 4000 else text
        try:
            prompt = CONFIDENTIAL_ANALYSIS_PROMPT.format(page_number=page_number, text=analysis_text)
            result = self.llm_service.analyze(CONFIDENTIAL_SYSTEM_PROMPT, prompt, expect_json=True)
            if not isinstance(result, dict) or not result.get("violations_found", False):
                return []
            violations = []
            for v in result.get("violations", []):
                violations.append({
                    "category": ViolationCategory.CONFIDENTIAL.value,
                    "violation_type": v.get("violation_type", "Confidential Information"),
                    "severity": v.get("severity", "High"),
                    "confidence": min(1.0, max(0.0, float(v.get("confidence", 0.7)))),
                    "page_number": page_number,
                    "matched_text": v.get("matched_text", "")[:200],
                    "reason": v.get("reason", "AI detected confidential content"),
                    "remediation": v.get("remediation", "Review and redact sensitive information."),
                    "detected_by": "llm",
                })
            return violations
        except (LLMServiceError, Exception) as e:
            logger.error(f"LLM confidential detection failed for page {page_number}: {e}")
            return []

    def _apply_custom_rules(self, text: str, page_number: int, rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
        violations = []
        for rule in rules:
            if not rule.get("enabled", True):
                continue
            pattern = rule.get("pattern")
            if pattern:
                try:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        matched_text = match if isinstance(match, str) else match[0]
                        violations.append({
                            "category": ViolationCategory.CONFIDENTIAL.value,
                            "violation_type": rule.get("rule_name", "Custom Rule"),
                            "severity": rule.get("severity", "Medium"),
                            "confidence": 0.80,
                            "page_number": page_number,
                            "matched_text": matched_text.strip()[:200],
                            "reason": rule.get("description", "Matched custom confidential rule"),
                            "remediation": "Review flagged content per organizational policy.",
                            "detected_by": "regex",
                        })
                except re.error as e:
                    logger.warning(f"Custom rule regex error: {e}")
            for keyword in rule.get("keywords", []):
                if keyword.lower() in text.lower():
                    idx = text.lower().find(keyword.lower())
                    start, end = max(0, idx - 50), min(len(text), idx + len(keyword) + 50)
                    violations.append({
                        "category": ViolationCategory.CONFIDENTIAL.value,
                        "violation_type": rule.get("rule_name", "Custom Keyword Rule"),
                        "severity": rule.get("severity", "Medium"),
                        "confidence": 0.75,
                        "page_number": page_number,
                        "matched_text": text[start:end].strip(),
                        "reason": f"Keyword '{keyword}' detected",
                        "remediation": "Review flagged content per organizational policy.",
                        "detected_by": "keyword",
                    })
        return violations

    @staticmethod
    def _deduplicate(violations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: dict[str, dict[str, Any]] = {}
        for v in violations:
            key = f"{v.get('matched_text', '')[:50]}_{v.get('violation_type', '')}"
            if key not in seen or v.get("confidence", 0) > seen[key].get("confidence", 0):
                seen[key] = v
        return list(seen.values())
