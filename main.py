"""
AI-Powered PDF Compliance Scanner
====================================
Main Streamlit application entrypoint.
Provides sidebar navigation and page routing.

Usage:
    streamlit run main.py
"""

import streamlit as st

from app.config.settings import APP_ICON, APP_LAYOUT, APP_TITLE
from app.ui.pages.compliance_results import render_compliance_results_page
from app.ui.pages.rules_management import render_rules_management_page
from app.ui.pages.scan_history import render_scan_history_page
from app.ui.pages.upload_scan import render_upload_scan_page
from app.ui.theme import get_custom_css


def main() -> None:
    """Main application entrypoint."""

    # --- Page Configuration ---
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout=APP_LAYOUT,
        initial_sidebar_state="expanded",
    )

    # --- Inject Custom CSS ---
    st.markdown(get_custom_css(), unsafe_allow_html=True)

    # --- Initialize Session State ---
    if "has_scan_results" not in st.session_state:
        st.session_state["has_scan_results"] = False
    if "last_scan_result" not in st.session_state:
        st.session_state["last_scan_result"] = {}

    # --- Sidebar Navigation ---
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 25px 0 15px 0;">
                <div style="margin-bottom: 15px; display: flex; justify-content: center; align-items: center;">
                    <svg width="70" height="70" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" style="stop-color:#00F2FE;stop-opacity:1" />
                                <stop offset="100%" style="stop-color:#4FACFE;stop-opacity:1" />
                            </linearGradient>
                            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                                <feGaussianBlur stdDeviation="4" result="blur" />
                                <feComposite in="SourceGraphic" in2="blur" operator="over" />
                            </filter>
                        </defs>
                        <!-- Shield Base -->
                        <path d="M50 5 L90 25 L90 60 C90 80 70 95 50 95 C30 95 10 80 10 60 L10 25 Z" fill="url(#shieldGrad)" filter="url(#glow)"/>
                        <!-- Inner Checkmark -->
                        <path d="M30 50 L45 65 L70 35" stroke="white" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                        <!-- Small decoration -->
                        <circle cx="50" cy="80" r="4" fill="white" opacity="0.8"/>
                    </svg>
                </div>
                <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800; background: -webkit-linear-gradient(45deg, #00F2FE, #4FACFE); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.5px;">CompliGuard</h2>
                <p style="margin: 4px 0 0 0; font-size: 0.8rem; font-weight: 600; letter-spacing: 2px; color: #a0aec0; text-transform: uppercase;">AI Scanner</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Navigation menu
        page = st.radio(
            "Navigation",
            [
                "📤 Upload & Scan",
                "📊 Compliance Results",
                "⚙️ Rules Management",
                "📜 Scan History",
            ],
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Sidebar info
        st.markdown("""
            <div style="padding: 12px; background: rgba(255,255,255,0.1); border-radius: 8px; font-size: 0.8rem;">
                <p style="margin: 0 0 4px 0;"><strong>🤖 Model:</strong> Llama 3.1 8B</p>
                <p style="margin: 0 0 4px 0;"><strong>🔗 Provider:</strong> GROQ</p>
                <p style="margin: 0;"><strong>🔄 Orchestrator:</strong> LangGraph</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Quick status
        if st.session_state.get("has_scan_results"):
            result = st.session_state.get("last_scan_result", {})
            summary = result.get("compliance_summary", {})
            score = summary.get("compliance_score", 100)
            status = summary.get("compliance_status", "N/A")

            if score >= 90:
                color = "#00C853"
            elif score >= 70:
                color = "#FFD600"
            else:
                color = "#FF1744"

            st.markdown(f"""
                <div style="padding: 12px; background: rgba(255,255,255,0.1); border-radius: 8px; text-align: center;">
                    <p style="margin: 0; font-size: 0.75rem; opacity: 0.8;">LAST SCAN</p>
                    <p style="margin: 4px 0; font-size: 1.8rem; font-weight: 700; color: {color};">{score:.0f}%</p>
                    <p style="margin: 0; font-size: 0.8rem;">{status}</p>
                </div>
            """, unsafe_allow_html=True)

    # --- Page Routing ---
    if page == "📤 Upload & Scan":
        render_upload_scan_page()
    elif page == "📊 Compliance Results":
        render_compliance_results_page()
    elif page == "⚙️ Rules Management":
        render_rules_management_page()
    elif page == "📜 Scan History":
        render_scan_history_page()


if __name__ == "__main__":
    main()
