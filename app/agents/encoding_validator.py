"""
UTF-8 Encoding Validation Agent
=================================
Validates text encoding consistency, detects malformed characters,
garbled symbols, broken Unicode, and unsupported characters.
Pure Python implementation — no LLM needed.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from app.models.schemas import SeverityLevel, ViolationCategory
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Characters that typically indicate encoding issues
ENCODING_ISSUE_PATTERNS = [
    (r'�', "Replacement character (U+FFFD)"),
    (r'[\x00-\x08\x0b\x0c\x0e-\x1f]', "Control characters"),
    (r'[\ufff0-\uffff]', "Unicode specials block"),
    (r'Ã[\x80-\xbf]', "UTF-8 decoded as Latin-1 (mojibake)"),
    (r'Â[\xa0-\xff]', "UTF-8 double-decoded (mojibake)"),
    (r'[\udce0-\udcff]', "Surrogate escape characters"),
]

# Common mojibake patterns (UTF-8 misinterpreted as other encodings)
MOJIBAKE_PATTERNS = [
    (r'Ã©', "é misencoded"),
    (r'Ã¨', "è misencoded"),
    (r'Ã¼', "ü misencoded"),
    (r'Ã¶', "ö misencoded"),
    (r'Ã¤', "ä misencoded"),
    (r'Ã±', "ñ misencoded"),
    (r'â€™', "' misencoded"),
    (r'â€œ', '" misencoded'),
    (r'â€\x9d', '" misencoded'),
    (r'â€"', "— misencoded"),
    (r'â€"', "– misencoded"),
]


class EncodingValidator:
    """
    UTF-8 Encoding Validation Agent.
    
    Checks for:
        - Replacement characters (U+FFFD)
        - Control characters
        - Mojibake (encoding misinterpretation artifacts)
        - Non-printable characters
        - Mixed encoding indicators
    """

    def __init__(self) -> None:
        logger.info("Encoding Validator initialized")

    def validate(self, text: str, page_number: int) -> dict[str, Any]:
        """
        Validate encoding consistency of extracted text.

        Args:
            text: Extracted text to validate.
            page_number: Page number for reference.

        Returns:
            Dict with encoding_valid flag, issues list, and violations.
        """
        if not text:
            return {
                "page_number": page_number,
                "encoding_valid": True,
                "issues": [],
                "violations": [],
            }

        issues: list[str] = []
        violations: list[dict[str, Any]] = []

        # Check for replacement characters
        replacement_count = text.count('�')
        if replacement_count > 0:
            issue = f"Found {replacement_count} replacement character(s) (U+FFFD)"
            issues.append(issue)
            violations.append(self._create_violation(
                page_number, "Replacement Characters",
                f"Found {replacement_count} '�' characters",
                SeverityLevel.MEDIUM if replacement_count < 5 else SeverityLevel.HIGH,
                min(1.0, 0.7 + replacement_count * 0.05),
            ))

        # Check for encoding issue patterns
        for pattern, description in ENCODING_ISSUE_PATTERNS:
            try:
                matches = re.findall(pattern, text)
                if matches:
                    issue = f"{description}: found {len(matches)} occurrence(s)"
                    issues.append(issue)
                    if description != "Replacement character (U+FFFD)":  # Avoid duplicate
                        violations.append(self._create_violation(
                            page_number, "Encoding Anomaly",
                            f"{description} ({len(matches)} occurrences)",
                            SeverityLevel.MEDIUM,
                            0.85,
                        ))
            except re.error:
                pass

        # Check for mojibake patterns
        for pattern, description in MOJIBAKE_PATTERNS:
            if pattern in text:
                count = text.count(pattern)
                issue = f"Mojibake detected: {description} ({count} occurrences)"
                issues.append(issue)
                violations.append(self._create_violation(
                    page_number, "Mojibake / Encoding Corruption",
                    f"{description} - '{pattern}' found {count} time(s)",
                    SeverityLevel.MEDIUM,
                    0.90,
                ))

        # Check for non-printable characters (excluding standard whitespace)
        non_printable = []
        for char in text:
            if not char.isprintable() and char not in ('\n', '\r', '\t', ' '):
                cat = unicodedata.category(char)
                if cat.startswith('C'):  # Control/format characters
                    non_printable.append(f"U+{ord(char):04X} ({unicodedata.name(char, 'UNKNOWN')})")

        if non_printable:
            unique_chars = list(set(non_printable))[:10]
            issue = f"Non-printable characters: {', '.join(unique_chars)}"
            issues.append(issue)
            violations.append(self._create_violation(
                page_number, "Non-Printable Characters",
                f"Found {len(non_printable)} non-printable characters",
                SeverityLevel.LOW,
                0.80,
            ))

        # Check for mixed scripts that might indicate garbled text
        scripts = set()
        for char in text[:500]:  # Sample first 500 chars
            if char.isalpha():
                try:
                    script = unicodedata.name(char, "").split()[0]
                    scripts.add(script)
                except (ValueError, IndexError):
                    pass

        encoding_valid = len(violations) == 0

        result = {
            "page_number": page_number,
            "encoding_valid": encoding_valid,
            "issues": issues,
            "violations": violations,
        }

        if not encoding_valid:
            logger.info(f"Page {page_number}: {len(issues)} encoding issues found")

        return result

    @staticmethod
    def _create_violation(
        page_number: int,
        violation_type: str,
        matched_text: str,
        severity: SeverityLevel,
        confidence: float,
    ) -> dict[str, Any]:
        return {
            "category": ViolationCategory.ENCODING.value,
            "violation_type": violation_type,
            "severity": severity.value,
            "confidence": confidence,
            "page_number": page_number,
            "matched_text": matched_text,
            "reason": f"Encoding validation: {violation_type}",
            "remediation": "Re-export the PDF with proper UTF-8 encoding from the source document.",
            "detected_by": "encoding_check",
        }
