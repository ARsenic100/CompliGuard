"""
SQLite Database Module
========================
Manages scan history and persistent storage using SQLite.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Optional

from app.config.settings import DB_PATH
from app.utils.logger import get_logger

logger = get_logger(__name__)


class Database:
    """SQLite database manager for scan history and metadata."""

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Create tables if they don't exist."""
        conn = self._get_conn()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scan_history (
                    scan_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_size_bytes INTEGER,
                    page_count INTEGER,
                    total_violations INTEGER DEFAULT 0,
                    compliance_score REAL DEFAULT 100.0,
                    compliance_status TEXT DEFAULT 'Compliant',
                    scan_timestamp TEXT NOT NULL,
                    processing_time_seconds REAL DEFAULT 0.0,
                    report_json_path TEXT,
                    report_pdf_path TEXT,
                    scan_data TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rules (
                    id TEXT PRIMARY KEY,
                    rule_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    enabled INTEGER DEFAULT 1,
                    severity TEXT DEFAULT 'Medium',
                    description TEXT DEFAULT '',
                    pattern TEXT,
                    keywords TEXT DEFAULT '[]',
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS corporate_policies (
                    id TEXT PRIMARY KEY,
                    policy_name TEXT NOT NULL,
                    upload_date TEXT NOT NULL,
                    chunk_count INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS historical_remediations (
                    id TEXT PRIMARY KEY,
                    violation_type TEXT NOT NULL,
                    violation_text TEXT NOT NULL,
                    resolution TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Database init error: {e}")
        finally:
            conn.close()

    def save_scan(self, scan_data: dict[str, Any]) -> None:
        """Save a completed scan to history."""
        conn = self._get_conn()
        try:
            conn.execute("""
                INSERT OR REPLACE INTO scan_history
                (scan_id, filename, file_size_bytes, page_count, total_violations,
                 compliance_score, compliance_status, scan_timestamp,
                 processing_time_seconds, report_json_path, report_pdf_path, scan_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scan_data.get("scan_id", ""),
                scan_data.get("filename", ""),
                scan_data.get("file_size_bytes", 0),
                scan_data.get("page_count", 0),
                scan_data.get("total_violations", 0),
                scan_data.get("compliance_score", 100.0),
                scan_data.get("compliance_status", "Compliant"),
                scan_data.get("scan_timestamp", ""),
                scan_data.get("processing_time_seconds", 0.0),
                scan_data.get("report_json_path", ""),
                scan_data.get("report_pdf_path", ""),
                json.dumps(scan_data, default=str),
            ))
            conn.commit()
            logger.info(f"Scan saved: {scan_data.get('scan_id', '')}")
        except Exception as e:
            logger.error(f"Error saving scan: {e}")
        finally:
            conn.close()

    def get_scan_history(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get scan history ordered by most recent first."""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "SELECT * FROM scan_history ORDER BY scan_timestamp DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching scan history: {e}")
            return []
        finally:
            conn.close()

    def get_scan_by_id(self, scan_id: str) -> Optional[dict[str, Any]]:
        """Get a specific scan by ID."""
        conn = self._get_conn()
        try:
            cursor = conn.execute("SELECT * FROM scan_history WHERE scan_id = ?", (scan_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error fetching scan: {e}")
            return None
        finally:
            conn.close()

    def delete_scan(self, scan_id: str) -> bool:
        """Delete a scan from history."""
        conn = self._get_conn()
        try:
            conn.execute("DELETE FROM scan_history WHERE scan_id = ?", (scan_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting scan: {e}")
            return False
        finally:
            conn.close()

    # --- Rules CRUD ---
    def save_rule(self, rule: dict[str, Any]) -> None:
        """Save or update a compliance rule."""
        conn = self._get_conn()
        try:
            conn.execute("""
                INSERT OR REPLACE INTO rules
                (id, rule_name, category, enabled, severity, description, pattern, keywords, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule.get("id", ""),
                rule.get("rule_name", ""),
                rule.get("category", ""),
                1 if rule.get("enabled", True) else 0,
                rule.get("severity", "Medium"),
                rule.get("description", ""),
                rule.get("pattern", ""),
                json.dumps(rule.get("keywords", [])),
                rule.get("created_at", ""),
                rule.get("updated_at", ""),
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving rule: {e}")
        finally:
            conn.close()

    def get_rules(self) -> list[dict[str, Any]]:
        """Get all compliance rules."""
        conn = self._get_conn()
        try:
            cursor = conn.execute("SELECT * FROM rules ORDER BY category, rule_name")
            rows = cursor.fetchall()
            rules = []
            for row in rows:
                rule = dict(row)
                rule["enabled"] = bool(rule.get("enabled", 1))
                try:
                    rule["keywords"] = json.loads(rule.get("keywords", "[]"))
                except (json.JSONDecodeError, TypeError):
                    rule["keywords"] = []
                rules.append(rule)
            return rules
        except Exception as e:
            logger.error(f"Error fetching rules: {e}")
            return []
        finally:
            conn.close()

    def delete_rule(self, rule_id: str) -> bool:
        """Delete a compliance rule."""
        conn = self._get_conn()
        try:
            conn.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting rule: {e}")
            return False
        finally:
            conn.close()

    # --- RAG Metadata ---
    
    def save_policy_metadata(self, policy_id: str, policy_name: str, chunk_count: int) -> None:
        conn = self._get_conn()
        from datetime import datetime
        try:
            conn.execute(
                "INSERT INTO corporate_policies (id, policy_name, upload_date, chunk_count) VALUES (?, ?, ?, ?)",
                (policy_id, policy_name, datetime.now().isoformat(), chunk_count)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving policy metadata: {e}")
        finally:
            conn.close()

    def get_policies(self) -> list[dict[str, Any]]:
        conn = self._get_conn()
        try:
            cursor = conn.execute("SELECT * FROM corporate_policies ORDER BY upload_date DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching policies: {e}")
            return []
        finally:
            conn.close()

    def save_remediation_metadata(self, remediation_id: str, violation_type: str, violation_text: str, resolution: str) -> None:
        conn = self._get_conn()
        from datetime import datetime
        try:
            conn.execute(
                "INSERT INTO historical_remediations (id, violation_type, violation_text, resolution, created_at) VALUES (?, ?, ?, ?, ?)",
                (remediation_id, violation_type, violation_text, resolution, datetime.now().isoformat())
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving remediation metadata: {e}")
        finally:
            conn.close()

    def get_remediations(self) -> list[dict[str, Any]]:
        conn = self._get_conn()
        try:
            cursor = conn.execute("SELECT * FROM historical_remediations ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching remediations: {e}")
            return []
        finally:
            conn.close()
