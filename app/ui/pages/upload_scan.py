"""
Upload & Scan Page
=====================
PDF upload, validation, scan execution, and real-time progress display.
"""

from __future__ import annotations

import streamlit as st

from app.config.settings import MAX_FILE_SIZE_MB
from app.graph.workflow import run_compliance_scan
from app.ui.components import (
    render_gradient_divider,
    render_metric_card,
    render_page_header,
    render_score_display,
    render_status_badge,
)
from app.utils.helpers import format_file_size


def render_upload_scan_page() -> None:
    """Render the Upload & Scan page."""
    render_page_header(
        "📤 Upload & Scan",
        "Upload a PDF document to scan for compliance violations using AI-powered analysis.",
    )

    # --- File Upload Section ---
    st.markdown("### 📁 Upload PDF Document")
    uploaded_file = st.file_uploader(
        "Drag and drop or click to upload a PDF file",
        type=["pdf"],
        help=f"Maximum file size: {MAX_FILE_SIZE_MB} MB",
        key="pdf_uploader",
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_name = uploaded_file.name

        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric_card("📄 File Name", file_name)
        with col2:
            render_metric_card("📦 File Size", format_file_size(len(file_bytes)))
        with col3:
            render_metric_card("📋 Type", "PDF Document")

        render_gradient_divider()

        # --- Scan Button ---
        st.markdown("### 🔍 Start Compliance Scan")
        col_btn, col_info = st.columns([1, 3])

        with col_btn:
            scan_clicked = st.button(
                "🚀 Start Scan",
                type="primary",
                use_container_width=True,
                key="start_scan_btn",
            )

        with col_info:
            st.info(
                "The scan will check for: **PII**, **Confidential Information**, "
                "**Encoding Issues**, and **Abusive Content**."
            )

        if scan_clicked:
            _run_scan(file_bytes, file_name)

    else:
        # Show instructions when no file uploaded
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    border-radius: 16px; margin-top: 20px;">
            <div style="font-size: 4rem; margin-bottom: 16px;">📄</div>
            <h3 style="color: #333; margin-bottom: 12px;">No PDF Uploaded</h3>
            <p style="color: #666; max-width: 400px; margin: 0 auto;">
                Upload a PDF document to begin compliance scanning.
                The AI will analyze each page for potential violations.
            </p>
        </div>
        """, unsafe_allow_html=True)


def _run_scan(file_bytes: bytes, file_name: str) -> None:
    """Execute the compliance scan with progress display."""

    # Progress container
    progress_container = st.container()
    with progress_container:
        st.markdown('<div class="scanning-indicator">⏳ Scanning in progress...</div>', unsafe_allow_html=True)
        progress_bar = st.progress(0, text="Initializing scan...")
        log_expander = st.expander("📋 Processing Logs", expanded=True)

    # Run the scan
    with st.spinner("Running AI-powered compliance analysis..."):
        try:
            progress_bar.progress(5, text="Starting compliance scan...")

            # Execute the LangGraph workflow
            result = run_compliance_scan(file_bytes, file_name)

            # Store results in session state
            st.session_state["last_scan_result"] = result
            st.session_state["has_scan_results"] = True

            progress_bar.progress(100, text="Scan complete!")

        except Exception as e:
            st.error(f"❌ Scan failed: {e}")
            return

    # Display logs
    with log_expander:
        logs = result.get("logs", [])
        for log_entry in logs:
            st.text(log_entry)

    render_gradient_divider()

    # --- Display Results Summary ---
    errors = result.get("errors", [])
    if errors:
        st.error("⚠️ Scan completed with errors:")
        for error in errors:
            st.error(error)
        return

    compliance_summary = result.get("compliance_summary", {})
    score = compliance_summary.get("compliance_score", 100.0)
    status = compliance_summary.get("compliance_status", "Compliant")
    total = compliance_summary.get("total_violations", 0)

    st.markdown("### 📊 Scan Results Summary")

    # Score display
    col_score, col_metrics = st.columns([1, 2])
    with col_score:
        render_score_display(score, status)

    with col_metrics:
        m1, m2 = st.columns(2)
        with m1:
            render_metric_card("Total Violations", total, "critical" if total > 0 else "low")
        with m2:
            render_metric_card(
                "Pages Scanned",
                compliance_summary.get("total_pages_scanned", 0),
            )

        m3, m4 = st.columns(2)
        with m3:
            render_metric_card("🔴 Critical", compliance_summary.get("critical_count", 0), "critical")
        with m4:
            render_metric_card("🟠 High", compliance_summary.get("high_count", 0), "high")

    render_gradient_divider()

    # Processing info
    processing_time = result.get("processing_time", 0)
    st.info(
        f"⏱️ Scan completed in **{processing_time:.1f} seconds** | "
        f"📄 **{compliance_summary.get('total_pages_scanned', 0)}** pages scanned | "
        f"🔍 **{total}** violations found"
    )

    # Navigation hint
    st.success("✅ Scan complete! Navigate to **📊 Compliance Results** in the sidebar for detailed analysis.")
