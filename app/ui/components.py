"""
Reusable UI Components
========================
Streamlit-based UI components for metric cards, badges, score displays, etc.
"""

from __future__ import annotations

import streamlit as st


def render_metric_card(label: str, value: str | int | float, variant: str = "") -> None:
    """Render a styled metric card."""
    css_class = f"metric-card {variant}" if variant else "metric-card"
    st.markdown(f"""
        <div class="{css_class}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)


def render_status_badge(status: str) -> str:
    """Return HTML for a compliance status badge."""
    css_class = status.lower().replace("-", "-").replace(" ", "-")
    if css_class == "non-compliant":
        css_class = "non-compliant"
    return f'<span class="status-badge {css_class}">{status}</span>'


def render_severity_badge(severity: str) -> str:
    """Return HTML for a severity level badge."""
    css_class = severity.lower()
    return f'<span class="severity-badge {css_class}">{severity}</span>'


def render_score_display(score: float, status: str) -> None:
    """Render a large compliance score display."""
    if score >= 90:
        color = "#00C853"
    elif score >= 70:
        color = "#FFD600"
    else:
        color = "#FF1744"

    st.markdown(f"""
        <div class="score-display">
            <div class="score-value" style="color: {color};">{score:.1f}%</div>
            <div class="score-label">Compliance Score</div>
            <div style="margin-top: 12px;">{render_status_badge(status)}</div>
        </div>
    """, unsafe_allow_html=True)


def render_gradient_divider() -> None:
    """Render a gradient divider line."""
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str = "") -> None:
    """Render a styled page header."""
    sub_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
        <div class="app-header">
            <h1>{title}</h1>
            {sub_html}
        </div>
    """, unsafe_allow_html=True)


def render_violation_card(violation: dict) -> None:
    """Render a styled violation card."""
    severity = violation.get("severity", "Medium").lower()
    category = violation.get("category", "Unknown")
    v_type = violation.get("violation_type", "Unknown")
    page = violation.get("page_number", "?")
    confidence = violation.get("confidence", 0)
    matched = violation.get("matched_text", "")
    reason = violation.get("reason", "")
    remediation = violation.get("remediation", "")

    matched_display = matched[:150] + "..." if len(matched) > 150 else matched

    st.markdown(f"""
        <div class="violation-card {severity}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong>{v_type}</strong>
                {render_severity_badge(violation.get("severity", "Medium"))}
            </div>
            <div style="font-size: 0.85rem; color: #666;">
                📂 {category} &nbsp;|&nbsp; 📄 Page {page} &nbsp;|&nbsp; 🎯 {confidence:.0%} confidence
            </div>
            <div style="margin-top: 8px; font-size: 0.9rem;">
                <strong>Match:</strong> <code>{matched_display}</code>
            </div>
            <div style="margin-top: 4px; font-size: 0.85rem; color: #555;">
                <strong>Reason:</strong> {reason}
            </div>
            {f'<div style="margin-top: 4px; font-size: 0.85rem; color: #1565C0;"><strong>Remediation:</strong> {remediation}</div>' if remediation else ''}
        </div>
    """, unsafe_allow_html=True)
