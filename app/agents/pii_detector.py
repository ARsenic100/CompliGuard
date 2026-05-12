"""
PII Detection Agent
=====================
Hybrid PII detection using regex patterns (high recall) and LLM verification (high precision).
Detects emails, phone numbers, Aadhaar, PAN, SSN, passport numbers, and addresses.
"""

from __future__ import annotations

import re
from typing import Any

from app.models.schemas import SeverityLevel, ViolationCategory
from app.prompts.templates import PII_ANALYSIS_PROMPT, PII_SYSTEM_PROMPT
from app.services.llm_service import LLMServiceError, get_llm_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# REGEX PATTERNS FOR PII DETECTION
# ============================================================================

PII_PATTERNS: dict[str, dict[str, Any]] = {
    "Email Address": {
        "pattern": r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b',
        "severity": SeverityLevel.HIGH,
        "confidence": 0.95,
    },
    "Phone Number": {
        "pattern": r'(?:\+?\d{1,3}[\s\-.]?)?\(?\d{2,4}\)?[\s\-.]?\d{3,4}[\s\-.]?\d{3,4}\b',
        "severity": SeverityLevel.HIGH,
        "confidence": 0.85,
    },
    "Aadhaar Number": {
        "pattern": r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',
        "severity": SeverityLevel.CRITICAL,
        "confidence": 0.80,
    },
    "PAN Number": {
        "pattern": r'\b[A-Z]{5}\d{4}[A-Z]\b',
        "severity": SeverityLevel.CRITICAL,
        "confidence": 0.90,
    },
    "SSN": {
        "pattern": r'\b\d{3}[\s\-]?\d{2}[\s\-]?\d{4}\b',
        "severity": SeverityLevel.CRITICAL,
        "confidence": 0.80,
    },
    "Passport Number": {
        "pattern": r'\b[A-Z]{1,2}\d{6,9}\b',
        "severity": SeverityLevel.CRITICAL,
        "confidence": 0.70,
    },
    "Credit Card": {
        "pattern": r'\b(?:\d{4}[\s\-]?){3}\d{4}\b',
        "severity": SeverityLevel.CRITICAL,
        "confidence": 0.85,
    },
    "IP Address": {
        "pattern": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        "severity": SeverityLevel.MEDIUM,
        "confidence": 0.80,
    },
    "Date of Birth": {
        "pattern": r'\b(?:DOB|Date of Birth|Born|Birthday)\s*[:\-]?\s*\d{1,2}[\s/\-]\d{1,2}[\s/\-]\d{2,4}\b',
        "severity": SeverityLevel.HIGH,
        "confidence": 0.85,
    },
}


class PIIDetector:
    """
    PII Detection Agent using a hybrid regex + LLM approach.

    Strategy:
        1. Run regex patterns for high-recall detection
        2. Use LLM to verify ambiguous matches and find contextual PII
        3. Merge and deduplicate results
    """

    def __init__(self) -> None:
        """Initialize the PII detector."""
        self.llm_service = get_llm_service()
        logger.info("PII Detector initialized")

    def detect(
        self,
        text: str,
        page_number: int,
        rules: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Detect PII in text using hybrid regex + LLM approach.

        Args:
            text: Text content to analyze.
            page_number: Page number for reference.
            rules: Optional list of custom PII rules with patterns.

        Returns:
            List of violation dicts.
        """
        if not text.strip():
            return []

        violations: list[dict[str, Any]] = []

        # Step 1: Regex-based detection
        regex_violations = self._detect_with_regex(text, page_number, rules)
        violations.extend(regex_violations)

        # Step 2: LLM-based detection for contextual PII
        llm_violations = self._detect_with_llm(text, page_number)
        violations.extend(llm_violations)

        # Step 3: Deduplicate
        violations = self._deduplicate(violations)

        logger.info(f"Page {page_number}: Found {len(violations)} PII violations")
        return violations

    def _detect_with_regex(
        self,
        text: str,
        page_number: int,
        custom_rules: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Detect PII using regex patterns.

        Args:
            text: Text to scan.
            page_number: Page number.
            custom_rules: Optional custom regex rules.

        Returns:
            List of regex-detected violation dicts.
        """
        violations = []

        # Built-in patterns
        for pii_type, config in PII_PATTERNS.items():
            try:
                matches = re.findall(config["pattern"], text, re.IGNORECASE)
                for match in matches:
                    matched_text = match if isinstance(match, str) else match[0]
                    violations.append({
                        "category": ViolationCategory.PII.value,
                        "violation_type": pii_type,
                        "severity": config["severity"].value,
                        "confidence": config["confidence"],
                        "page_number": page_number,
                        "matched_text": matched_text.strip(),
                        "reason": f"Regex pattern matched: {pii_type}",
                        "remediation": f"Redact or remove the {pii_type.lower()} before distribution.",
                        "detected_by": "regex",
                    })
            except re.error as e:
                logger.warning(f"Regex error for {pii_type}: {e}")

        # Custom rules
        if custom_rules:
            for rule in custom_rules:
                if not rule.get("enabled", True) or not rule.get("pattern"):
                    continue
                try:
                    matches = re.findall(rule["pattern"], text, re.IGNORECASE)
                    for match in matches:
                        matched_text = match if isinstance(match, str) else match[0]
                        violations.append({
                            "category": ViolationCategory.PII.value,
                            "violation_type": rule.get("rule_name", "Custom PII Rule"),
                            "severity": rule.get("severity", "Medium"),
                            "confidence": 0.85,
                            "page_number": page_number,
                            "matched_text": matched_text.strip(),
                            "reason": rule.get("description", "Matched custom PII rule"),
                            "remediation": "Review and redact if confirmed as PII.",
                            "detected_by": "regex",
                        })
                except re.error as e:
                    logger.warning(f"Custom rule regex error: {e}")

        return violations

    def _detect_with_llm(self, text: str, page_number: int) -> list[dict[str, Any]]:
        """
        Detect PII using LLM contextual analysis.

        Args:
            text: Text to analyze.
            page_number: Page number.

        Returns:
            List of LLM-detected violation dicts.
        """
        if not self.llm_service.is_available:
            logger.warning("LLM not available, skipping LLM-based PII detection")
            return []

        # Truncate very long text to avoid token limits
        analysis_text = text[:4000] if len(text) > 4000 else text

        try:
            prompt = PII_ANALYSIS_PROMPT.format(
                page_number=page_number,
                text=analysis_text,
            )
            result = self.llm_service.analyze(PII_SYSTEM_PROMPT, prompt, expect_json=True)

            if not isinstance(result, dict):
                return []

            if not result.get("violations_found", False):
                return []

            violations = []
            for v in result.get("violations", []):
                violations.append({
                    "category": ViolationCategory.PII.value,
                    "violation_type": v.get("violation_type", "PII Detected"),
                    "severity": v.get("severity", "Medium"),
                    "confidence": min(1.0, max(0.0, float(v.get("confidence", 0.7)))),
                    "page_number": page_number,
                    "matched_text": v.get("matched_text", ""),
                    "reason": v.get("reason", "Detected by AI analysis"),
                    "remediation": f"Review and redact the detected {v.get('violation_type', 'PII')}.",
                    "detected_by": "llm",
                })

            return violations

        except LLMServiceError as e:
            logger.error(f"LLM PII detection failed for page {page_number}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in LLM PII detection: {e}")
            return []

    @staticmethod
    def _deduplicate(violations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Remove duplicate violations based on matched text and type.

        Keeps the detection with higher confidence when duplicates are found.

        Args:
            violations: List of violation dicts.

        Returns:
            Deduplicated list.
        """
        seen: dict[str, dict[str, Any]] = {}
        for v in violations:
            key = f"{v.get('matched_text', '')}_{v.get('violation_type', '')}"
            if key in seen:
                # Keep the one with higher confidence
                if v.get("confidence", 0) > seen[key].get("confidence", 0):
                    seen[key] = v
            else:
                seen[key] = v
        return list(seen.values())
