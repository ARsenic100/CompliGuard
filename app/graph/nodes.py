"""
LangGraph Workflow Node Functions
===================================
Each function is a node in the LangGraph StateGraph.
Nodes read from and write to the shared ScanState.

IMPORTANT: For Annotated reducer fields (logs, errors, pii_results, etc.),
each node must return only NEW items — LangGraph auto-concatenates them
via operator.add. Do NOT copy the existing list and append.
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime
from typing import Any

from app.agents.confidential_detector import ConfidentialDetector
from app.agents.encoding_validator import EncodingValidator
from app.agents.pii_detector import PIIDetector
from app.agents.toxicity_detector import ToxicityDetector
from app.graph.state import ScanState
from app.models.schemas import ViolationCategory
from app.services.pdf_service import PDFService, PDFServiceError
from app.services.report_service import ReportService
from app.storage.database import Database
from app.storage.rules_store import RulesStore
from app.utils.helpers import calculate_compliance_score, get_compliance_status
from app.utils.logger import get_logger
from app.utils.security import FileValidationError, validate_uploaded_file

logger = get_logger(__name__)


def validate_pdf_node(state: ScanState) -> dict[str, Any]:
    """Node: Validate the uploaded PDF file."""
    logger.info("▶ Node: validate_pdf")

    try:
        file_bytes = state["file_bytes"]
        file_name = state["file_name"]

        # Security validation
        validation = validate_uploaded_file(file_bytes, file_name)

        # PDF structure validation
        pdf_validation = PDFService.validate_pdf(file_bytes)

        file_metadata = {
            "filename": validation["filename"],
            "file_size_bytes": validation["file_size"],
            "file_hash": validation["file_hash"],
            "page_count": pdf_validation["page_count"],
            "pdf_metadata": pdf_validation["metadata"],
        }

        return {
            "file_metadata": file_metadata,
            "page_count": pdf_validation["page_count"],
            "errors": [],
            "logs": [
                "🔍 Validating PDF file...",
                f"✅ PDF validated: {pdf_validation['page_count']} pages, {validation['file_size']} bytes",
            ],
            "current_step": "validate_pdf",
            "progress": 10.0,
        }

    except (FileValidationError, PDFServiceError) as e:
        error_msg = f"PDF validation failed: {e}"
        logger.error(error_msg)
        return {
            "errors": [error_msg],
            "logs": ["🔍 Validating PDF file...", f"❌ {error_msg}"],
            "current_step": "validate_pdf_error",
            "progress": 10.0,
        }


def extract_text_node(state: ScanState) -> dict[str, Any]:
    """Node: Extract text from all PDF pages using PyMuPDF."""
    logger.info("▶ Node: extract_text")

    try:
        extracted_pages = PDFService.extract_text(state["file_bytes"])
        total_chars = sum(len(t) for t in extracted_pages.values())
        empty_pages = sum(1 for t in extracted_pages.values() if not t.strip())

        new_logs = [
            "📄 Extracting text from PDF pages...",
            f"✅ Extracted text from {len(extracted_pages)} pages ({total_chars:,} characters)",
        ]
        if empty_pages:
            new_logs.append(f"⚠️ {empty_pages} empty page(s) detected (possibly scanned/image-only)")

        return {
            "extracted_pages": extracted_pages,
            "errors": [],
            "logs": new_logs,
            "current_step": "extract_text",
            "progress": 25.0,
        }

    except PDFServiceError as e:
        error_msg = f"Text extraction failed: {e}"
        logger.error(error_msg)
        return {
            "errors": [error_msg],
            "logs": ["📄 Extracting text from PDF pages...", f"❌ {error_msg}"],
            "current_step": "extract_text_error",
            "progress": 25.0,
        }


def load_rules_node(state: ScanState) -> dict[str, Any]:
    """Node: Load active compliance rules."""
    logger.info("▶ Node: load_rules")

    try:
        rules_store = RulesStore()
        rules = rules_store.get_enabled_rules()
        rule_dicts = [r for r in rules]
        return {
            "rule_config": rule_dicts,
            "logs": ["📋 Loading compliance rules...", f"✅ Loaded {len(rule_dicts)} active rules"],
            "errors": [],
            "current_step": "load_rules",
            "progress": 30.0,
        }
    except Exception as e:
        logger.error(f"Error loading rules: {e}")
        return {
            "rule_config": [],
            "logs": ["📋 Loading compliance rules...", f"⚠️ Error loading rules, using defaults: {e}"],
            "errors": [],
            "current_step": "load_rules",
            "progress": 30.0,
        }


def pii_detection_node(state: ScanState) -> dict[str, Any]:
    """Node: Run PII detection on all pages."""
    logger.info("▶ Node: pii_detection")

    detector = PIIDetector()
    extracted_pages = state.get("extracted_pages", {})
    rules = [r for r in state.get("rule_config", []) if r.get("category") == ViolationCategory.PII.value]

    all_violations: list[dict[str, Any]] = []
    for page_num, text in extracted_pages.items():
        if text.strip():
            violations = detector.detect(text, page_num, rules)
            all_violations.extend(violations)

    return {
        "pii_results": all_violations,
        "logs": [
            "🔐 Running PII detection...",
            f"✅ PII detection complete: {len(all_violations)} violation(s) found",
        ],
        "errors": [],
    }


def confidential_detection_node(state: ScanState) -> dict[str, Any]:
    """Node: Run confidential information detection on all pages."""
    logger.info("▶ Node: confidential_detection")

    detector = ConfidentialDetector()
    extracted_pages = state.get("extracted_pages", {})
    rules = [r for r in state.get("rule_config", []) if r.get("category") == ViolationCategory.CONFIDENTIAL.value]

    all_violations: list[dict[str, Any]] = []
    for page_num, text in extracted_pages.items():
        if text.strip():
            violations = detector.detect(text, page_num, rules)
            all_violations.extend(violations)

    return {
        "confidential_results": all_violations,
        "logs": [
            "🔒 Running confidential information detection...",
            f"✅ Confidential detection complete: {len(all_violations)} violation(s) found",
        ],
        "errors": [],
    }


def encoding_validation_node(state: ScanState) -> dict[str, Any]:
    """Node: Validate UTF-8 encoding consistency on all pages."""
    logger.info("▶ Node: encoding_validation")

    validator = EncodingValidator()
    extracted_pages = state.get("extracted_pages", {})

    all_violations: list[dict[str, Any]] = []
    for page_num, text in extracted_pages.items():
        result = validator.validate(text, page_num)
        all_violations.extend(result.get("violations", []))

    return {
        "encoding_results": all_violations,
        "logs": [
            "⚠️ Running encoding validation...",
            f"✅ Encoding validation complete: {len(all_violations)} issue(s) found",
        ],
        "errors": [],
    }


def toxicity_detection_node(state: ScanState) -> dict[str, Any]:
    """Node: Run toxic/abusive content detection on all pages."""
    logger.info("▶ Node: toxicity_detection")

    detector = ToxicityDetector()
    extracted_pages = state.get("extracted_pages", {})

    all_violations: list[dict[str, Any]] = []
    for page_num, text in extracted_pages.items():
        if text.strip():
            violations = detector.detect(text, page_num)
            all_violations.extend(violations)

    return {
        "toxicity_results": all_violations,
        "logs": [
            "🚫 Running toxicity detection...",
            f"✅ Toxicity detection complete: {len(all_violations)} violation(s) found",
        ],
        "errors": [],
    }


def aggregate_results_node(state: ScanState) -> dict[str, Any]:
    """Node: Aggregate all check results into unified page results and summary."""
    logger.info("▶ Node: aggregate_results")

    # Collect all violations from all checks
    all_violations: list[dict[str, Any]] = []
    all_violations.extend(state.get("pii_results", []))
    all_violations.extend(state.get("confidential_results", []))
    all_violations.extend(state.get("encoding_results", []))
    all_violations.extend(state.get("toxicity_results", []))

    # Build page results
    extracted_pages = state.get("extracted_pages", {})
    page_results: list[dict[str, Any]] = []

    for page_num in sorted(extracted_pages.keys()):
        page_violations = [v for v in all_violations if v.get("page_number") == page_num]
        encoding_violations = [v for v in page_violations if v.get("category") == ViolationCategory.ENCODING.value]

        page_results.append({
            "page_number": page_num,
            "text_length": len(extracted_pages.get(page_num, "")),
            "violations": page_violations,
            "encoding_valid": len(encoding_violations) == 0,
            "encoding_issues": [v.get("matched_text", "") for v in encoding_violations],
        })

    # Calculate compliance score and summary
    score = calculate_compliance_score(all_violations)
    status = get_compliance_status(score)

    severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    categories_detected: set[str] = set()
    for v in all_violations:
        sev = v.get("severity", "Medium")
        if sev in severity_counts:
            severity_counts[sev] += 1
        categories_detected.add(v.get("category", "Unknown"))

    pages_with_violations = sum(1 for pr in page_results if pr.get("violations"))

    compliance_summary = {
        "total_violations": len(all_violations),
        "critical_count": severity_counts["Critical"],
        "high_count": severity_counts["High"],
        "medium_count": severity_counts["Medium"],
        "low_count": severity_counts["Low"],
        "compliance_score": score,
        "compliance_status": status.value,
        "pages_with_violations": pages_with_violations,
        "total_pages_scanned": len(extracted_pages),
        "categories_detected": list(categories_detected),
    }

    return {
        "all_violations": all_violations,
        "page_results": page_results,
        "compliance_summary": compliance_summary,
        "compliance_score": score,
        "compliance_status": status.value,
        "logs": [
            "📊 Aggregating results...",
            f"✅ Aggregation complete: Score {score:.1f}% ({status.value})",
            f"   Total violations: {len(all_violations)} across {pages_with_violations} page(s)",
        ],
        "errors": [],
        "current_step": "aggregate_results",
        "progress": 85.0,
    }


def generate_report_node(state: ScanState) -> dict[str, Any]:
    """Node: Generate JSON and PDF compliance reports."""
    logger.info("▶ Node: generate_report")

    report_service = ReportService()
    scan_id = state.get("scan_id", str(uuid.uuid4()))
    file_metadata = state.get("file_metadata", {})
    page_results = state.get("page_results", [])
    compliance_summary = state.get("compliance_summary", {})
    all_violations = state.get("all_violations", [])

    json_path = ""
    pdf_path = ""
    new_logs = ["📝 Generating compliance reports..."]

    try:
        json_path = report_service.generate_json_report(
            scan_id, file_metadata, page_results, compliance_summary, all_violations
        )
        new_logs.append("✅ JSON report generated")
    except Exception as e:
        logger.error(f"JSON report generation failed: {e}")
        new_logs.append(f"⚠️ JSON report generation failed: {e}")

    try:
        pdf_path = report_service.generate_pdf_report(
            scan_id, file_metadata, page_results, compliance_summary, all_violations
        )
        new_logs.append("✅ PDF report generated")
    except Exception as e:
        logger.error(f"PDF report generation failed: {e}")
        new_logs.append(f"⚠️ PDF report generation failed: {e}")

    return {
        "report_json_path": json_path,
        "report_pdf_path": pdf_path,
        "logs": new_logs,
        "errors": [],
        "current_step": "generate_report",
        "progress": 92.0,
    }


def store_results_node(state: ScanState) -> dict[str, Any]:
    """Node: Save scan results to database."""
    logger.info("▶ Node: store_results")

    completed_at = datetime.now().isoformat()
    started_at = state.get("started_at", completed_at)

    try:
        start_dt = datetime.fromisoformat(started_at)
        end_dt = datetime.fromisoformat(completed_at)
        processing_time = (end_dt - start_dt).total_seconds()
    except (ValueError, TypeError):
        processing_time = 0.0

    file_metadata = state.get("file_metadata", {})
    compliance_summary = state.get("compliance_summary", {})

    scan_data = {
        "scan_id": state.get("scan_id", ""),
        "filename": file_metadata.get("filename", ""),
        "file_size_bytes": file_metadata.get("file_size_bytes", 0),
        "page_count": state.get("page_count", 0),
        "total_violations": compliance_summary.get("total_violations", 0),
        "compliance_score": compliance_summary.get("compliance_score", 100.0),
        "compliance_status": compliance_summary.get("compliance_status", "Compliant"),
        "scan_timestamp": started_at,
        "processing_time_seconds": processing_time,
        "report_json_path": state.get("report_json_path", ""),
        "report_pdf_path": state.get("report_pdf_path", ""),
    }

    new_logs = ["💾 Saving scan results..."]

    try:
        db = Database()
        db.save_scan(scan_data)
        new_logs.append("✅ Results saved to database")
    except Exception as e:
        logger.error(f"Error saving results: {e}")
        new_logs.append(f"⚠️ Error saving results: {e}")

    return {
        "completed_at": completed_at,
        "processing_time": processing_time,
        "logs": new_logs,
        "errors": [],
        "current_step": "store_results",
        "progress": 100.0,
    }


def should_continue_after_validation(state: ScanState) -> str:
    """Conditional edge: check if validation passed."""
    errors = state.get("errors", [])
    if errors:
        return "error"
    return "continue"
