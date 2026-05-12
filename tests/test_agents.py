"""
Tests for Compliance Agents
==============================
Unit tests for PII, confidential, encoding, and toxicity detection agents.
"""

import pytest


class TestPIIDetector:
    """Tests for PII detection agent."""

    def test_detect_email(self):
        """Test email address detection."""
        from app.agents.pii_detector import PIIDetector
        detector = PIIDetector()
        text = "Contact us at john.doe@example.com for more info."
        violations = detector._detect_with_regex(text, 1)
        email_violations = [v for v in violations if v["violation_type"] == "Email Address"]
        assert len(email_violations) >= 1
        assert "john.doe@example.com" in email_violations[0]["matched_text"]

    def test_detect_phone(self):
        """Test phone number detection."""
        from app.agents.pii_detector import PIIDetector
        detector = PIIDetector()
        text = "Call us at +1-555-123-4567 today."
        violations = detector._detect_with_regex(text, 1)
        phone_violations = [v for v in violations if v["violation_type"] == "Phone Number"]
        assert len(phone_violations) >= 1

    def test_detect_pan(self):
        """Test PAN number detection."""
        from app.agents.pii_detector import PIIDetector
        detector = PIIDetector()
        text = "PAN Number: ABCDE1234F is required."
        violations = detector._detect_with_regex(text, 1)
        pan_violations = [v for v in violations if v["violation_type"] == "PAN Number"]
        assert len(pan_violations) >= 1

    def test_detect_ssn(self):
        """Test SSN detection."""
        from app.agents.pii_detector import PIIDetector
        detector = PIIDetector()
        text = "SSN: 123-45-6789"
        violations = detector._detect_with_regex(text, 1)
        ssn_violations = [v for v in violations if v["violation_type"] == "SSN"]
        assert len(ssn_violations) >= 1

    def test_no_pii_in_clean_text(self):
        """Test that clean text produces no regex violations."""
        from app.agents.pii_detector import PIIDetector
        detector = PIIDetector()
        text = "This is a clean document with no personal information."
        violations = detector._detect_with_regex(text, 1)
        assert len(violations) == 0

    def test_deduplication(self):
        """Test violation deduplication."""
        from app.agents.pii_detector import PIIDetector
        violations = [
            {"matched_text": "test@test.com", "violation_type": "Email", "confidence": 0.9},
            {"matched_text": "test@test.com", "violation_type": "Email", "confidence": 0.95},
        ]
        deduped = PIIDetector._deduplicate(violations)
        assert len(deduped) == 1
        assert deduped[0]["confidence"] == 0.95


class TestConfidentialDetector:
    """Tests for confidential information detection."""

    def test_detect_api_key(self):
        """Test API key detection."""
        from app.agents.confidential_detector import ConfidentialDetector
        detector = ConfidentialDetector()
        text = "api_key = sk-live-abcdefghijklmnopqrstuvwxyz"
        violations = detector._detect_with_keywords(text, 1)
        assert len(violations) >= 1

    def test_detect_confidential_marking(self):
        """Test confidential marking detection."""
        from app.agents.confidential_detector import ConfidentialDetector
        detector = ConfidentialDetector()
        text = "This document is STRICTLY CONFIDENTIAL"
        violations = detector._detect_with_keywords(text, 1)
        assert len(violations) >= 1

    def test_detect_password(self):
        """Test password detection."""
        from app.agents.confidential_detector import ConfidentialDetector
        detector = ConfidentialDetector()
        text = 'password = MySecret123!'
        violations = detector._detect_with_keywords(text, 1)
        assert len(violations) >= 1


class TestEncodingValidator:
    """Tests for encoding validation."""

    def test_valid_encoding(self):
        """Test that valid UTF-8 text passes."""
        from app.agents.encoding_validator import EncodingValidator
        validator = EncodingValidator()
        result = validator.validate("Hello, this is valid text.", 1)
        assert result["encoding_valid"] is True
        assert len(result["violations"]) == 0

    def test_replacement_character(self):
        """Test detection of replacement characters."""
        from app.agents.encoding_validator import EncodingValidator
        validator = EncodingValidator()
        result = validator.validate("Text with \ufffd replacement chars", 1)
        assert result["encoding_valid"] is False
        assert len(result["violations"]) >= 1

    def test_empty_text(self):
        """Test handling of empty text."""
        from app.agents.encoding_validator import EncodingValidator
        validator = EncodingValidator()
        result = validator.validate("", 1)
        assert result["encoding_valid"] is True


class TestToxicityDetector:
    """Tests for toxicity detection."""

    def test_pre_screen_positive(self):
        """Test that pre-screening flags potentially toxic text."""
        from app.agents.toxicity_detector import ToxicityDetector
        detector = ToxicityDetector()
        assert detector._pre_screen("I will kill you") is True

    def test_pre_screen_negative(self):
        """Test that pre-screening passes clean text."""
        from app.agents.toxicity_detector import ToxicityDetector
        detector = ToxicityDetector()
        assert detector._pre_screen("This is a nice day for a walk") is False
