"""
Compliance Results Page
=========================
Detailed results dashboard with charts, page-wise violations,
search/filter, and downloadable reports.
"""

from __future__ import annotations

import json

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.ui.components import (
    render_gradient_divider,
    render_page_header,
    render_score_display,
    render_severity_badge,
    render_violation_card,
)
from app.utils.helpers import (
    count_violations_by_category,
    count_violations_by_severity,
    get_category_icon,
)


def render_compliance_results_page() -> None:
    """Render the Compliance Results page."""
    render_page_header(
        "📊 Compliance Results",
        "Detailed analysis of compliance violations detected in the scanned document.",
    )

    # Check for scan results
    if not st.session_state.get("has_scan_results"):
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    border-radius: 16px;">
            <div style="font-size: 4rem; margin-bottom: 16px;">📋</div>
            <h3 style="color: #333;">No Scan Results Available</h3>
            <p style="color: #666;">Upload and scan a PDF document first to see compliance results.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    result = st.session_state.get("last_scan_result", {})
    compliance_summary = result.get("compliance_summary", {})
    all_violations = result.get("all_violations", [])
    page_results = result.get("page_results", [])
    file_metadata = result.get("file_metadata", {})

    score = compliance_summary.get("compliance_score", 100.0)
    status = compliance_summary.get("compliance_status", "Compliant")

    # === Overall Score ===
    col_score, col_info = st.columns([1, 2])
    with col_score:
        render_score_display(score, status)
    with col_info:
        st.markdown(f"**Document:** {file_metadata.get('filename', 'N/A')}")
        st.markdown(f"**Pages Scanned:** {compliance_summary.get('total_pages_scanned', 0)}")
        st.markdown(f"**Total Violations:** {compliance_summary.get('total_violations', 0)}")
        st.markdown(f"**Categories Detected:** {', '.join(compliance_summary.get('categories_detected', []))}")

        # Download buttons
        c1, c2 = st.columns(2)
        json_path = result.get("report_json_path", "")
        pdf_path = result.get("report_pdf_path", "")
        with c1:
            if json_path:
                try:
                    with open(json_path, "r") as f:
                        st.download_button("📥 Download JSON Report", f.read(), "compliance_report.json", "application/json", use_container_width=True)
                except FileNotFoundError:
                    st.warning("JSON report file not found")
        with c2:
            if pdf_path:
                try:
                    with open(pdf_path, "rb") as f:
                        st.download_button("📥 Download PDF Report", f.read(), "compliance_report.pdf", "application/pdf", use_container_width=True)
                except FileNotFoundError:
                    st.warning("PDF report file not found")

    render_gradient_divider()

    # === Charts ===
    if all_violations:
        st.markdown("### 📈 Violation Analytics")
        tab_charts, tab_pages, tab_all = st.tabs(["📊 Charts", "📄 Page-wise", "📋 All Violations"])

        with tab_charts:
            _render_charts(all_violations, compliance_summary, page_results)

        with tab_pages:
            _render_page_wise_results(page_results)

        with tab_all:
            _render_all_violations(all_violations)
    else:
        st.success("🎉 No compliance violations detected! The document is fully compliant.")


def _render_charts(violations: list[dict], summary: dict, page_results: list[dict]) -> None:
    """Render analytics charts."""
    col1, col2 = st.columns(2)

    with col1:
        # Severity distribution pie chart
        severity_counts = count_violations_by_severity(violations)
        non_zero = {k: v for k, v in severity_counts.items() if v > 0}
        if non_zero:
            colors = {"Critical": "#FF1744", "High": "#FF6D00", "Medium": "#FFD600", "Low": "#00C853"}
            fig = go.Figure(data=[go.Pie(
                labels=list(non_zero.keys()),
                values=list(non_zero.values()),
                hole=0.4,
                marker=dict(colors=[colors.get(k, "#999") for k in non_zero.keys()]),
                textinfo="label+value",
                textfont=dict(size=13),
            )])
            fig.update_layout(
                title="Violations by Severity",
                showlegend=True,
                height=350,
                margin=dict(t=40, b=20, l=20, r=20),
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Category distribution bar chart
        category_counts = count_violations_by_category(violations)
        if category_counts:
            fig = go.Figure(data=[go.Bar(
                x=list(category_counts.values()),
                y=[f"{get_category_icon(k)} {k}" for k in category_counts.keys()],
                orientation="h",
                marker=dict(
                    color=["#667eea", "#764ba2", "#f093fb", "#f5576c"],
                    cornerradius=8,
                ),
            )])
            fig.update_layout(
                title="Violations by Category",
                xaxis_title="Count",
                height=350,
                margin=dict(t=40, b=20, l=20, r=20),
            )
            st.plotly_chart(fig, use_container_width=True)

    # Page-wise risk heatmap
    if page_results:
        page_nums = [pr.get("page_number", 0) for pr in page_results]
        violation_counts = [len(pr.get("violations", [])) for pr in page_results]

        if any(v > 0 for v in violation_counts):
            fig = go.Figure(data=go.Bar(
                x=page_nums,
                y=violation_counts,
                marker=dict(
                    color=violation_counts,
                    colorscale="Reds",
                    cornerradius=4,
                ),
            ))
            fig.update_layout(
                title="Page-wise Violation Heatmap",
                xaxis_title="Page Number",
                yaxis_title="Violations",
                height=300,
                margin=dict(t=40, b=40, l=40, r=20),
            )
            st.plotly_chart(fig, use_container_width=True)

    # Compliance score gauge
    score = summary.get("compliance_score", 100)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Compliance Score", "font": {"size": 18}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 2},
            "bar": {"color": "#667eea"},
            "steps": [
                {"range": [0, 70], "color": "#ffcdd2"},
                {"range": [70, 90], "color": "#fff9c4"},
                {"range": [90, 100], "color": "#c8e6c9"},
            ],
            "threshold": {
                "line": {"color": "black", "width": 4},
                "thickness": 0.75,
                "value": score,
            },
        },
    ))
    fig.update_layout(height=300, margin=dict(t=40, b=20, l=40, r=40))
    st.plotly_chart(fig, use_container_width=True)


def _render_page_wise_results(page_results: list[dict]) -> None:
    """Render page-by-page violation details."""
    # Filter to pages with violations
    pages_with_issues = [pr for pr in page_results if pr.get("violations")]

    if not pages_with_issues:
        st.success("No violations found on any page.")
        return

    st.markdown(f"**{len(pages_with_issues)}** page(s) with violations")

    for pr in pages_with_issues:
        page_num = pr.get("page_number", "?")
        violations = pr.get("violations", [])
        encoding_valid = pr.get("encoding_valid", True)

        status_icon = "🔴" if any(v.get("severity") in ("Critical", "High") for v in violations) else "🟡"
        encoding_icon = "✅" if encoding_valid else "⚠️"

        with st.expander(
            f"{status_icon} Page {page_num} — {len(violations)} violation(s) | Encoding: {encoding_icon}",
            expanded=False,
        ):
            for v in violations:
                render_violation_card(v)


def _render_all_violations(violations: list[dict]) -> None:
    """Render all violations with search and filter."""
    st.markdown(f"**Total:** {len(violations)} violation(s)")

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        severity_filter = st.multiselect(
            "Filter by Severity",
            ["Critical", "High", "Medium", "Low"],
            default=["Critical", "High", "Medium", "Low"],
            key="severity_filter",
        )
    with col_f2:
        categories = list(set(v.get("category", "") for v in violations))
        category_filter = st.multiselect("Filter by Category", categories, default=categories, key="cat_filter")
    with col_f3:
        search_text = st.text_input("🔍 Search violations", key="violation_search")

    # Apply filters
    filtered = violations
    if severity_filter:
        filtered = [v for v in filtered if v.get("severity") in severity_filter]
    if category_filter:
        filtered = [v for v in filtered if v.get("category") in category_filter]
    if search_text:
        search_lower = search_text.lower()
        filtered = [v for v in filtered if
                    search_lower in v.get("matched_text", "").lower() or
                    search_lower in v.get("reason", "").lower() or
                    search_lower in v.get("violation_type", "").lower()]

    st.markdown(f"**Showing:** {len(filtered)} of {len(violations)} violations")

    for v in filtered:
        render_violation_card(v)
