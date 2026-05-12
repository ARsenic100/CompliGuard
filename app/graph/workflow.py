"""
LangGraph Workflow Builder
============================
Builds and compiles the compliance scanning StateGraph.
The graph orchestrates the full scanning pipeline from
PDF validation through report generation.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from langgraph.graph import END, StateGraph

from app.graph.nodes import (
    aggregate_results_node,
    confidential_detection_node,
    encoding_validation_node,
    extract_text_node,
    generate_report_node,
    load_rules_node,
    pii_detection_node,
    should_continue_after_validation,
    store_results_node,
    toxicity_detection_node,
    validate_pdf_node,
)
from app.graph.state import ScanState
from app.utils.logger import get_logger

logger = get_logger(__name__)


def build_compliance_graph() -> StateGraph:
    """
    Build the LangGraph compliance scanning workflow.

    Workflow:
        validate_pdf → extract_text → load_rules →
        [parallel: pii, confidential, encoding, toxicity] →
        aggregate_results → generate_report → store_results → END

    Returns:
        Compiled StateGraph ready for invocation.
    """
    # Create the state graph
    graph = StateGraph(ScanState)

    # --- Add Nodes ---
    graph.add_node("validate_pdf", validate_pdf_node)
    graph.add_node("extract_text", extract_text_node)
    graph.add_node("load_rules", load_rules_node)
    graph.add_node("pii_detection", pii_detection_node)
    graph.add_node("confidential_detection", confidential_detection_node)
    graph.add_node("encoding_validation", encoding_validation_node)
    graph.add_node("toxicity_detection", toxicity_detection_node)
    graph.add_node("aggregate_results", aggregate_results_node)
    graph.add_node("generate_report", generate_report_node)
    graph.add_node("store_results", store_results_node)

    # --- Set Entry Point ---
    graph.set_entry_point("validate_pdf")

    # --- Add Edges ---
    # Conditional edge after validation: continue or stop on error
    graph.add_conditional_edges(
        "validate_pdf",
        should_continue_after_validation,
        {
            "continue": "extract_text",
            "error": END,
        },
    )

    # Sequential flow: extract → load rules
    graph.add_edge("extract_text", "load_rules")

    # Fan-out: rules → all 4 detection agents
    graph.add_edge("load_rules", "pii_detection")
    graph.add_edge("load_rules", "confidential_detection")
    graph.add_edge("load_rules", "encoding_validation")
    graph.add_edge("load_rules", "toxicity_detection")

    # Fan-in: all 4 agents → aggregate
    graph.add_edge("pii_detection", "aggregate_results")
    graph.add_edge("confidential_detection", "aggregate_results")
    graph.add_edge("encoding_validation", "aggregate_results")
    graph.add_edge("toxicity_detection", "aggregate_results")

    # Sequential flow: aggregate → report → store → END
    graph.add_edge("aggregate_results", "generate_report")
    graph.add_edge("generate_report", "store_results")
    graph.add_edge("store_results", END)

    logger.info("Compliance scanning graph built successfully")
    return graph


# Compile the graph once for reuse
_compiled_graph = None


def get_compiled_graph():
    """Get or create the compiled workflow graph."""
    global _compiled_graph
    if _compiled_graph is None:
        graph = build_compliance_graph()
        _compiled_graph = graph.compile()
        logger.info("Compliance graph compiled")
    return _compiled_graph


def run_compliance_scan(file_bytes: bytes, file_name: str) -> dict[str, Any]:
    """
    Execute the full compliance scanning workflow.

    Args:
        file_bytes: Raw PDF file content.
        file_name: Original filename.

    Returns:
        Final state dict with all scan results.
    """
    scan_id = str(uuid.uuid4())
    started_at = datetime.now().isoformat()

    logger.info(f"Starting compliance scan: {scan_id} for {file_name}")

    initial_state: ScanState = {
        "file_bytes": file_bytes,
        "file_name": file_name,
        "file_size": len(file_bytes),
        "scan_id": scan_id,
        "started_at": started_at,
        "errors": [],
        "logs": [f"🚀 Starting compliance scan: {file_name}"],
        "current_step": "initializing",
        "progress": 0.0,
        # Initialize empty results
        "file_metadata": {},
        "page_count": 0,
        "extracted_pages": {},
        "rule_config": [],
        "pii_results": [],
        "confidential_results": [],
        "encoding_results": [],
        "toxicity_results": [],
        "all_violations": [],
        "page_results": [],
        "compliance_summary": {},
        "compliance_score": 100.0,
        "compliance_status": "Compliant",
        "report_json_path": "",
        "report_pdf_path": "",
        "completed_at": "",
        "processing_time": 0.0,
    }

    compiled_graph = get_compiled_graph()

    try:
        # Run the graph
        final_state = compiled_graph.invoke(initial_state)
        logger.info(f"Scan completed: {scan_id}")
        return final_state
    except Exception as e:
        logger.error(f"Scan workflow failed: {e}")
        initial_state["errors"] = [f"Workflow execution failed: {e}"]
        initial_state["logs"].append(f"❌ Scan failed: {e}")
        initial_state["current_step"] = "error"
        return initial_state
