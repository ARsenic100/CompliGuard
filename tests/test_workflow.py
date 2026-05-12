"""
Tests for LangGraph Workflow
===============================
Tests for state, node functions, and workflow execution.
"""

import pytest


class TestScanState:
    """Tests for the scan state definition."""

    def test_state_can_be_created(self):
        """Test that ScanState can be instantiated."""
        from app.graph.state import ScanState
        state: ScanState = {
            "file_bytes": b"test",
            "file_name": "test.pdf",
            "file_size": 100,
            "errors": [],
            "logs": [],
        }
        assert state["file_name"] == "test.pdf"
        assert state["file_size"] == 100


class TestHelpers:
    """Tests for helper utilities."""

    def test_compliance_score_no_violations(self):
        """Test that no violations gives 100% score."""
        from app.utils.helpers import calculate_compliance_score
        assert calculate_compliance_score([]) == 100.0

    def test_compliance_score_with_violations(self):
        """Test score calculation with violations."""
        from app.utils.helpers import calculate_compliance_score
        violations = [
            {"severity": "Critical"},  # -10
            {"severity": "High"},      # -7
            {"severity": "Medium"},    # -4
        ]
        score = calculate_compliance_score(violations)
        assert score == 79.0

    def test_compliance_score_floor_zero(self):
        """Test that score doesn't go below 0."""
        from app.utils.helpers import calculate_compliance_score
        violations = [{"severity": "Critical"}] * 20
        score = calculate_compliance_score(violations)
        assert score == 0.0

    def test_get_compliance_status(self):
        """Test compliance status determination."""
        from app.utils.helpers import get_compliance_status
        from app.models.schemas import ComplianceStatus
        assert get_compliance_status(95.0) == ComplianceStatus.COMPLIANT
        assert get_compliance_status(80.0) == ComplianceStatus.WARNING
        assert get_compliance_status(50.0) == ComplianceStatus.NON_COMPLIANT

    def test_format_file_size(self):
        """Test file size formatting."""
        from app.utils.helpers import format_file_size
        assert format_file_size(500) == "500 B"
        assert "KB" in format_file_size(2048)
        assert "MB" in format_file_size(2 * 1024 * 1024)

    def test_count_violations_by_severity(self):
        """Test severity counting."""
        from app.utils.helpers import count_violations_by_severity
        violations = [
            {"severity": "Critical"},
            {"severity": "Critical"},
            {"severity": "High"},
            {"severity": "Low"},
        ]
        counts = count_violations_by_severity(violations)
        assert counts["Critical"] == 2
        assert counts["High"] == 1
        assert counts["Low"] == 1
        assert counts["Medium"] == 0
