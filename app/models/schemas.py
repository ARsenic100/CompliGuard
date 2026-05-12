"""
Pydantic Data Models / Schemas
===============================
Defines all data structures used throughout the application.
These models ensure type safety and data validation across
the compliance scanning pipeline.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================================
# ENUMS
# ============================================================================

class SeverityLevel(str, Enum):
    """Severity levels for compliance violations."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ViolationCategory(str, Enum):
    """Categories of compliance violations."""
    PII = "PII / Personal Information"
    CONFIDENTIAL = "Confidential Information"
    ENCODING = "Encoding Issue"
    TOXICITY = "Abusive / Unlawful Content"


class ComplianceStatus(str, Enum):
    """Overall compliance status."""
    COMPLIANT = "Compliant"
    WARNING = "Warning"
    NON_COMPLIANT = "Non-Compliant"


class ScanStatus(str, Enum):
    """Status of a compliance scan."""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"


# ============================================================================
# VIOLATION MODELS
# ============================================================================

class Violation(BaseModel):
    """Represents a single compliance violation detected in the PDF."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    category: ViolationCategory
    violation_type: str = Field(description="Specific type of violation (e.g., 'Email Address', 'API Key')")
    severity: SeverityLevel
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    page_number: int = Field(ge=1, description="Page number where violation was found")
    matched_text: str = Field(default="", description="The text that triggered the violation")
    reason: str = Field(default="", description="Explanation of why this is a violation")
    remediation: str = Field(default="", description="Suggested remediation action")
    detected_by: str = Field(default="", description="Detection method: 'regex', 'llm', or 'hybrid'")


class PageResult(BaseModel):
    """Compliance analysis results for a single page."""
    page_number: int
    text_length: int = 0
    violations: list[Violation] = Field(default_factory=list)
    encoding_valid: bool = True
    encoding_issues: list[str] = Field(default_factory=list)

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    @property
    def has_violations(self) -> bool:
        return len(self.violations) > 0


# ============================================================================
# SCAN RESULT MODELS
# ============================================================================

class FileMetadata(BaseModel):
    """Metadata about the uploaded PDF file."""
    filename: str
    file_size_bytes: int
    page_count: int = 0
    upload_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    file_hash: str = ""
    pdf_metadata: dict[str, Any] = Field(default_factory=dict)


class ComplianceSummary(BaseModel):
    """Summary of the compliance scan results."""
    total_violations: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    compliance_score: float = 100.0
    compliance_status: ComplianceStatus = ComplianceStatus.COMPLIANT
    pages_with_violations: int = 0
    total_pages_scanned: int = 0
    categories_detected: list[str] = Field(default_factory=list)


class ScanResult(BaseModel):
    """Complete scan result for a PDF document."""
    scan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_metadata: FileMetadata
    page_results: list[PageResult] = Field(default_factory=list)
    compliance_summary: ComplianceSummary = Field(default_factory=ComplianceSummary)
    scan_status: ScanStatus = ScanStatus.PENDING
    started_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    errors: list[str] = Field(default_factory=list)
    report_path: Optional[str] = None
    processing_time_seconds: float = 0.0

    def get_all_violations(self) -> list[Violation]:
        """Get all violations across all pages."""
        violations = []
        for page in self.page_results:
            violations.extend(page.violations)
        return violations

    def get_violations_by_category(self) -> dict[str, list[Violation]]:
        """Group violations by category."""
        grouped: dict[str, list[Violation]] = {}
        for violation in self.get_all_violations():
            category = violation.category.value
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(violation)
        return grouped

    def get_violations_by_severity(self) -> dict[str, list[Violation]]:
        """Group violations by severity."""
        grouped: dict[str, list[Violation]] = {}
        for violation in self.get_all_violations():
            severity = violation.severity.value
            if severity not in grouped:
                grouped[severity] = []
            grouped[severity].append(violation)
        return grouped


# ============================================================================
# RULE MODELS
# ============================================================================

class ComplianceRule(BaseModel):
    """A compliance rule that can be dynamically managed."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    rule_name: str
    category: ViolationCategory
    enabled: bool = True
    severity: SeverityLevel = SeverityLevel.MEDIUM
    description: str = ""
    pattern: Optional[str] = None  # Regex pattern (for regex-based rules)
    keywords: list[str] = Field(default_factory=list)  # Keywords for LLM-based detection
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# SCAN HISTORY MODEL
# ============================================================================

class ScanHistoryEntry(BaseModel):
    """Entry in the scan history database."""
    scan_id: str
    filename: str
    file_size_bytes: int
    page_count: int
    total_violations: int
    compliance_score: float
    compliance_status: str
    scan_timestamp: str
    processing_time_seconds: float
    report_path: Optional[str] = None
