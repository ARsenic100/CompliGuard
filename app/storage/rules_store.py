"""
Rules Store Module
====================
Manages compliance rules loading, saving, and default initialization.
Rules are stored in both SQLite and a JSON fallback file.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config.settings import RULES_DIR
from app.storage.database import Database
from app.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_RULES_FILE = RULES_DIR / "default_rules.json"


class RulesStore:
    """Manages compliance rules with database and JSON file storage."""

    def __init__(self) -> None:
        self.db = Database()
        self._ensure_defaults_loaded()

    def _ensure_defaults_loaded(self) -> None:
        """Load default rules into DB if none exist."""
        existing = self.db.get_rules()
        if not existing:
            self._load_defaults()

    def _load_defaults(self) -> None:
        """Load default rules from JSON file into the database."""
        if not DEFAULT_RULES_FILE.exists():
            logger.warning("Default rules file not found, creating defaults")
            self._create_default_rules_file()

        try:
            with open(DEFAULT_RULES_FILE, "r", encoding="utf-8") as f:
                rules = json.load(f)
            for rule in rules:
                self.db.save_rule(rule)
            logger.info(f"Loaded {len(rules)} default rules")
        except Exception as e:
            logger.error(f"Error loading default rules: {e}")

    def _create_default_rules_file(self) -> None:
        """Create the default rules JSON file."""
        from app.models.schemas import SeverityLevel, ViolationCategory
        default_rules = [
            {"id": "pii_001", "rule_name": "Email Address Detection", "category": ViolationCategory.PII.value,
             "enabled": True, "severity": SeverityLevel.HIGH.value,
             "description": "Detect email addresses in document text",
             "pattern": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}", "keywords": [],
             "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()},
            {"id": "pii_002", "rule_name": "Phone Number Detection", "category": ViolationCategory.PII.value,
             "enabled": True, "severity": SeverityLevel.HIGH.value,
             "description": "Detect phone numbers in various formats",
             "pattern": r"(?:\+?\d{1,3}[\s-]?)?\(?\d{2,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}",
             "keywords": [], "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()},
            {"id": "pii_003", "rule_name": "Aadhaar Number Detection", "category": ViolationCategory.PII.value,
             "enabled": True, "severity": SeverityLevel.CRITICAL.value,
             "description": "Detect 12-digit Aadhaar-like numbers",
             "pattern": r"\d{4}[\s-]?\d{4}[\s-]?\d{4}", "keywords": [],
             "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()},
            {"id": "conf_001", "rule_name": "Detect API Keys", "category": ViolationCategory.CONFIDENTIAL.value,
             "enabled": True, "severity": SeverityLevel.CRITICAL.value,
             "description": "Detect API keys and access tokens",
             "pattern": r"(?:api[_\-]?key|access[_\-]?token)\s*[=:]\s*[\w\-]{20,}",
             "keywords": ["api_key", "secret_key", "access_token"],
             "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()},
            {"id": "conf_002", "rule_name": "Confidential Markings", "category": ViolationCategory.CONFIDENTIAL.value,
             "enabled": True, "severity": SeverityLevel.HIGH.value,
             "description": "Detect confidential document markings",
             "pattern": r"\b(?:CONFIDENTIAL|STRICTLY CONFIDENTIAL|TOP SECRET|PROPRIETARY)\b",
             "keywords": ["confidential", "proprietary", "trade secret"],
             "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()},
            {"id": "conf_003", "rule_name": "Password Detection", "category": ViolationCategory.CONFIDENTIAL.value,
             "enabled": True, "severity": SeverityLevel.CRITICAL.value,
             "description": "Detect passwords and secrets in plain text",
             "pattern": r"(?:password|passwd|pwd|secret)\s*[=:]\s*[^\s]{4,}",
             "keywords": ["password", "secret", "credential"],
             "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()},
            {"id": "tox_001", "rule_name": "Hate Speech Detection", "category": ViolationCategory.TOXICITY.value,
             "enabled": True, "severity": SeverityLevel.CRITICAL.value,
             "description": "Detect hate speech and discriminatory language",
             "pattern": None, "keywords": ["hate", "racist", "discrimination"],
             "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()},
            {"id": "enc_001", "rule_name": "Encoding Validation", "category": ViolationCategory.ENCODING.value,
             "enabled": True, "severity": SeverityLevel.MEDIUM.value,
             "description": "Validate UTF-8 encoding consistency",
             "pattern": None, "keywords": [],
             "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()},
        ]
        RULES_DIR.mkdir(parents=True, exist_ok=True)
        with open(DEFAULT_RULES_FILE, "w", encoding="utf-8") as f:
            json.dump(default_rules, f, indent=2, ensure_ascii=False)
        logger.info("Created default rules file")

    def get_all_rules(self) -> list[dict[str, Any]]:
        """Get all rules from the database."""
        return self.db.get_rules()

    def get_enabled_rules(self) -> list[dict[str, Any]]:
        """Get only enabled rules."""
        return [r for r in self.db.get_rules() if r.get("enabled", True)]

    def get_rules_by_category(self, category: str) -> list[dict[str, Any]]:
        """Get enabled rules filtered by category."""
        return [r for r in self.get_enabled_rules() if r.get("category") == category]

    def add_rule(self, rule: dict[str, Any]) -> None:
        """Add a new rule."""
        import uuid
        if "id" not in rule:
            rule["id"] = str(uuid.uuid4())[:8]
        rule["created_at"] = datetime.now().isoformat()
        rule["updated_at"] = datetime.now().isoformat()
        self.db.save_rule(rule)
        logger.info(f"Rule added: {rule.get('rule_name')}")

    def update_rule(self, rule: dict[str, Any]) -> None:
        """Update an existing rule."""
        rule["updated_at"] = datetime.now().isoformat()
        self.db.save_rule(rule)
        logger.info(f"Rule updated: {rule.get('rule_name')}")

    def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule by ID."""
        result = self.db.delete_rule(rule_id)
        if result:
            logger.info(f"Rule deleted: {rule_id}")
        return result

    def toggle_rule(self, rule_id: str, enabled: bool) -> None:
        """Enable or disable a rule."""
        rules = self.db.get_rules()
        for rule in rules:
            if rule.get("id") == rule_id:
                rule["enabled"] = enabled
                rule["updated_at"] = datetime.now().isoformat()
                self.db.save_rule(rule)
                logger.info(f"Rule {rule_id} {'enabled' if enabled else 'disabled'}")
                return
