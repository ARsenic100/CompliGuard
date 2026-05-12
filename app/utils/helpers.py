"""
Helper Utilities
=================
Scoring formulas, formatters, and general-purpose utility functions
used across the compliance scanning application.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.config.settings import COMPLIANCE_THRESHOLDS, SEVERITY_WEIGHTS
from app.models.schemas import ComplianceStatus, SeverityLevel


def calculate_compliance_score(violations: list[dict[str, Any]]) -> float:
    """
    Calculate the compliance score based on violation severities.

    Formula: score = max(0, 100 - sum(severity_weights))
    Each violation's severity has a weight:
        Critical=10, High=7, Medium=4, Low=1

    Args:
        violations: List of violation dicts, each containing a 'severity' key.

    Returns:
        Compliance score between 0.0 and 100.0.
    """
    if not violations:
        return 100.0

    total_penalty = 0.0
    for v in violations:
        severity = v.get("severity", "Medium")
        weight = SEVERITY_WEIGHTS.get(severity, 4)
        total_penalty += weight

    score = max(0.0, 100.0 - total_penalty)
    return round(score, 1)


def get_compliance_status(score: float) -> ComplianceStatus:
    """
    Determine compliance status from the score.

    Args:
        score: Compliance score (0-100).

    Returns:
        ComplianceStatus enum value.
    """
    for status_name, (low, high) in COMPLIANCE_THRESHOLDS.items():
        if low <= score <= high:
            return ComplianceStatus(status_name)
    return ComplianceStatus.NON_COMPLIANT


def get_severity_color(severity: str) -> str:
    """
    Get the display color for a severity level.

    Args:
        severity: Severity level string.

    Returns:
        Hex color code.
    """
    colors = {
        "Critical": "#FF1744",
        "High": "#FF6D00",
        "Medium": "#FFD600",
        "Low": "#00C853",
    }
    return colors.get(severity, "#9E9E9E")


def get_status_color(status: str) -> str:
    """
    Get the display color for a compliance status.

    Args:
        status: Compliance status string.

    Returns:
        Hex color code.
    """
    colors = {
        "Compliant": "#00C853",
        "Warning": "#FFD600",
        "Non-Compliant": "#FF1744",
    }
    return colors.get(status, "#9E9E9E")


def get_category_icon(category: str) -> str:
    """
    Get the emoji icon for a violation category.

    Args:
        category: Violation category string.

    Returns:
        Emoji string.
    """
    icons = {
        "PII / Personal Information": "🔐",
        "Confidential Information": "🔒",
        "Encoding Issue": "⚠️",
        "Abusive / Unlawful Content": "🚫",
    }
    return icons.get(category, "📋")


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: File size in bytes.

    Returns:
        Human-readable size string (e.g., '2.5 MB').
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def format_timestamp(iso_timestamp: str) -> str:
    """
    Format ISO timestamp to a readable string.

    Args:
        iso_timestamp: ISO 8601 timestamp string.

    Returns:
        Formatted date-time string.
    """
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        return dt.strftime("%b %d, %Y %I:%M %p")
    except (ValueError, TypeError):
        return iso_timestamp


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length with ellipsis.

    Args:
        text: Input text.
        max_length: Maximum length before truncation.

    Returns:
        Truncated text.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def count_violations_by_severity(violations: list[dict[str, Any]]) -> dict[str, int]:
    """
    Count violations grouped by severity level.

    Args:
        violations: List of violation dicts.

    Returns:
        Dict mapping severity to count.
    """
    counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for v in violations:
        severity = v.get("severity", "Medium")
        if severity in counts:
            counts[severity] += 1
    return counts


def count_violations_by_category(violations: list[dict[str, Any]]) -> dict[str, int]:
    """
    Count violations grouped by category.

    Args:
        violations: List of violation dicts.

    Returns:
        Dict mapping category to count.
    """
    counts: dict[str, int] = {}
    for v in violations:
        category = v.get("category", "Unknown")
        counts[category] = counts.get(category, 0) + 1
    return counts
