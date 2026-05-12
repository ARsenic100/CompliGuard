"""
LangGraph State Definition
===========================
Defines the TypedDict state that flows through the LangGraph workflow.
Each node in the graph reads from and writes to this shared state.

List fields that receive updates from parallel nodes use Annotated
with operator.add as a reducer, so LangGraph concatenates values
from concurrent branches instead of raising a conflict error.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


class ScanState(TypedDict, total=False):
    """
    Shared state for the LangGraph compliance scanning workflow.

    Fields using Annotated[..., operator.add] are safe for parallel
    writes — LangGraph will merge them by concatenating lists.
    """
    # --- Input ---
    file_bytes: bytes
    file_name: str
    file_size: int

    # --- PDF Metadata ---
    file_metadata: dict[str, Any]
    page_count: int

    # --- Extracted Content ---
    extracted_pages: dict[int, str]

    # --- Rule Configuration ---
    rule_config: list[dict[str, Any]]

    # --- Per-Check Results (written by parallel agents) ---
    pii_results: Annotated[list[dict[str, Any]], operator.add]
    confidential_results: Annotated[list[dict[str, Any]], operator.add]
    encoding_results: Annotated[list[dict[str, Any]], operator.add]
    toxicity_results: Annotated[list[dict[str, Any]], operator.add]

    # --- Aggregated Results ---
    all_violations: list[dict[str, Any]]
    page_results: list[dict[str, Any]]
    compliance_summary: dict[str, Any]
    compliance_score: float
    compliance_status: str

    # --- Reports ---
    report_json_path: str
    report_pdf_path: str

    # --- Scan Metadata ---
    scan_id: str
    started_at: str
    completed_at: str
    processing_time: float

    # --- Error Handling (may be written by parallel nodes) ---
    errors: Annotated[list[str], operator.add]

    # --- UI Progress ---
    current_step: str
    progress: float
    logs: Annotated[list[str], operator.add]
