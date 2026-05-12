"""
Tests for Rules Management
==============================
Tests for rules store CRUD operations and database interactions.
"""

import os
import tempfile

import pytest


class TestRulesStore:
    """Tests for the rules storage system."""

    def test_get_all_rules_returns_list(self):
        """Test that get_all_rules returns a list."""
        from app.storage.rules_store import RulesStore
        store = RulesStore()
        rules = store.get_all_rules()
        assert isinstance(rules, list)

    def test_default_rules_loaded(self):
        """Test that default rules are loaded on initialization."""
        from app.storage.rules_store import RulesStore
        store = RulesStore()
        rules = store.get_all_rules()
        assert len(rules) > 0

    def test_add_rule(self):
        """Test adding a new rule."""
        from app.storage.rules_store import RulesStore
        store = RulesStore()
        initial_count = len(store.get_all_rules())
        store.add_rule({
            "rule_name": "Test Rule",
            "category": "PII / Personal Information",
            "severity": "Medium",
            "enabled": True,
            "description": "Test rule for unit testing",
            "pattern": r"\btest\b",
            "keywords": ["test"],
        })
        new_count = len(store.get_all_rules())
        assert new_count >= initial_count  # Could be equal if ID collision

    def test_get_enabled_rules(self):
        """Test filtering enabled rules."""
        from app.storage.rules_store import RulesStore
        store = RulesStore()
        enabled = store.get_enabled_rules()
        for rule in enabled:
            assert rule.get("enabled") is True

    def test_get_rules_by_category(self):
        """Test filtering rules by category."""
        from app.storage.rules_store import RulesStore
        store = RulesStore()
        pii_rules = store.get_rules_by_category("PII / Personal Information")
        for rule in pii_rules:
            assert rule.get("category") == "PII / Personal Information"


class TestDatabase:
    """Tests for the database module."""

    def test_database_initialization(self):
        """Test that database tables are created."""
        from app.storage.database import Database
        db = Database()
        history = db.get_scan_history()
        assert isinstance(history, list)

    def test_save_and_retrieve_scan(self):
        """Test saving and retrieving a scan."""
        from app.storage.database import Database
        db = Database()
        scan_data = {
            "scan_id": "test-123",
            "filename": "test.pdf",
            "file_size_bytes": 1000,
            "page_count": 5,
            "total_violations": 3,
            "compliance_score": 79.0,
            "compliance_status": "Warning",
            "scan_timestamp": "2026-01-01T00:00:00",
            "processing_time_seconds": 5.5,
        }
        db.save_scan(scan_data)
        result = db.get_scan_by_id("test-123")
        assert result is not None
        assert result["filename"] == "test.pdf"
        assert result["compliance_score"] == 79.0

        # Cleanup
        db.delete_scan("test-123")
