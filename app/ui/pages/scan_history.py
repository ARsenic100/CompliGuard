"""
Scan History Page
====================
Displays previous scan results with timestamps, scores, and report downloads.
"""

from __future__ import annotations

import json

import streamlit as st

from app.storage.database import Database
from app.ui.components import (
    render_gradient_divider,
    render_page_header,
    render_severity_badge,
    render_status_badge,
)
from app.utils.helpers import format_file_size, format_timestamp


def render_scan_history_page() -> None:
    """Render the Scan History page."""
    render_page_header(
        "📜 Scan History",
        "View previous compliance scan results, download reports, and track document compliance over time.",
    )

    db = Database()
    history = db.get_scan_history(limit=50)

    if not history:
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    border-radius: 16px;">
            <div style="font-size: 4rem; margin-bottom: 16px;">📜</div>
            <h3 style="color: #333;">No Scan History</h3>
            <p style="color: #666;">Scan results will appear here after you complete your first scan.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"**{len(history)}** scan(s) recorded")
    render_gradient_divider()

    # Display as a table
    for scan in history:
        scan_id = scan.get("scan_id", "")[:8]
        filename = scan.get("filename", "Unknown")
        score = scan.get("compliance_score", 100.0)
        status = scan.get("compliance_status", "Compliant")
        violations = scan.get("total_violations", 0)
        timestamp = scan.get("scan_timestamp", "")
        pages = scan.get("page_count", 0)
        proc_time = scan.get("processing_time_seconds", 0)

        # Score-based color
        if score >= 90:
            score_color = "#00C853"
        elif score >= 70:
            score_color = "#FFD600"
        else:
            score_color = "#FF1744"

        col1, col2, col3, col4 = st.columns([3, 1, 1, 2])

        with col1:
            st.markdown(f"""
                **📄 {filename}**
                <br><small style="color: #888;">ID: {scan_id} | 📅 {format_timestamp(timestamp)} | ⏱️ {proc_time:.1f}s</small>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: {score_color};">{score:.0f}%</div>
                    <small>{status}</small>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 1.2rem; font-weight: 600;">{violations}</div>
                    <small>Violations</small>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            btn_col1, btn_col2 = st.columns(2)
            json_path = scan.get("report_json_path", "")
            pdf_path = scan.get("report_pdf_path", "")

            with btn_col1:
                if json_path:
                    try:
                        with open(json_path, "r") as f:
                            st.download_button(
                                "📥 JSON",
                                f.read(),
                                f"report_{scan_id}.json",
                                "application/json",
                                key=f"dl_json_{scan_id}",
                                use_container_width=True,
                            )
                    except FileNotFoundError:
                        st.button("⚠️", disabled=True, key=f"na_json_{scan_id}")

            with btn_col2:
                if pdf_path:
                    try:
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                "📥 PDF",
                                f.read(),
                                f"report_{scan_id}.pdf",
                                "application/pdf",
                                key=f"dl_pdf_{scan_id}",
                                use_container_width=True,
                            )
                    except FileNotFoundError:
                        st.button("⚠️", disabled=True, key=f"na_pdf_{scan_id}")

        st.markdown("---")
