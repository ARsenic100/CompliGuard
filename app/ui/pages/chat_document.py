"""
Chat with Document UI Page
===========================
Interactive RAG chatbot with full context: document chunks, scan violations,
corporate policies, compliance rules, and historical remediations.
"""

import json
import os

import streamlit as st

from app.services.llm_service import get_llm_service
from app.services.rag_service import get_rag_service
from app.storage.database import Database


def _build_rules_context() -> str:
    """Load all active compliance rules as context."""
    rules_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "rules", "default_rules.json",
    )
    try:
        with open(rules_path, "r") as f:
            rules = json.load(f)
        lines = []
        for r in rules:
            if r.get("enabled"):
                severity = r.get("severity", "Medium")
                lines.append(
                    f"- [{severity}] {r['rule_name']}: {r.get('description', '')} "
                    f"(Category: {r.get('category', 'N/A')})"
                )
        return "\n".join(lines) if lines else "No active rules configured."
    except Exception:
        return "Rules file unavailable."


def _build_violations_context(scan_id: str) -> str:
    """Get all violations from the last scan result stored in session state."""
    result = st.session_state.get("last_scan_result", {})
    if result.get("scan_id") != scan_id:
        return "No violation data available for this scan in the current session."

    violations = result.get("all_violations", [])
    if not violations:
        return "No violations were found in this document. It is fully compliant."

    summary = result.get("compliance_summary", {})
    score = summary.get("compliance_score", 100)
    status = summary.get("compliance_status", "Compliant")

    lines = [
        f"COMPLIANCE SCORE: {score:.1f}% — Status: {status}",
        f"TOTAL VIOLATIONS: {len(violations)}",
        "",
    ]
    for i, v in enumerate(violations, 1):
        lines.append(
            f"{i}. [{v.get('severity', 'Medium')}] {v.get('violation_type', 'Unknown')} "
            f"(Page {v.get('page_number', '?')}) — "
            f"Match: \"{v.get('matched_text', '')[:120]}\" — "
            f"Reason: {v.get('reason', 'N/A')}"
        )
        if v.get("remediation"):
            lines.append(f"   Suggested Fix: {v['remediation']}")
    return "\n".join(lines)


def _build_policy_context(rag_service) -> str:
    """Fetch corporate policy context from ChromaDB."""
    try:
        docs = rag_service.query_policies("compliance rules policies requirements", k=5)
        if docs:
            return "\n\n".join([d.page_content for d in docs])
        return "No corporate policies have been uploaded yet."
    except Exception:
        return "Corporate policy retrieval unavailable."


def _build_remediation_context(rag_service) -> str:
    """Fetch historical remediation context."""
    try:
        docs = rag_service.query_remediations("compliance violation resolution", k=3)
        if docs:
            return "\n\n".join([d.page_content for d in docs])
        return "No historical remediations recorded yet."
    except Exception:
        return "Remediation history unavailable."


def render_chat_document_page() -> None:
    st.header("💬 Chat with Document (RAG)")

    st.markdown("""
    Use this interactive assistant to query uploaded documents for specific details
    or ask for clarification regarding compliance violations. The AI has access to:
    **document content**, **scan violations**, **corporate policies**, **compliance rules**,
    and **historical remediations**.
    """)

    db = Database()
    scans = db.get_scan_history(limit=20)

    if not scans:
        st.info("No documents have been scanned yet. Please upload and scan a document first.")
        return

    scan_options = {f"{s['filename']} ({s['scan_id'][:8]})": s['scan_id'] for s in scans}
    selected_name = st.selectbox("Select a Document to Chat With:", list(scan_options.keys()))
    scan_id = scan_options[selected_name]

    rag_service = get_rag_service()
    llm_service = get_llm_service()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_scan_id" not in st.session_state or st.session_state.current_scan_id != scan_id:
        st.session_state.chat_history = []
        st.session_state.current_scan_id = scan_id

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about this document..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching document & gathering context..."):
                # 1. Document chunks (RAG retrieval)
                docs = rag_service.query_document(scan_id, prompt, k=5)
                doc_context = "\n\n".join([d.page_content for d in docs]) if docs else "No matching content found."

                # 2. Violations context
                violations_context = _build_violations_context(scan_id)

                # 3. Active rules
                rules_context = _build_rules_context()

                # 4. Corporate policies
                policy_context = _build_policy_context(rag_service)

                # 5. Historical remediations
                remediation_context = _build_remediation_context(rag_service)

                # Build the comprehensive system prompt
                system_prompt = f"""You are CompliGuard AI — an expert compliance assistant with deep knowledge of document analysis, data privacy regulations, and corporate policy enforcement.

You have access to the following context about the scanned document. Use ALL of it to give detailed, accurate, and actionable answers.

═══════════════════════════════════════
📄 DOCUMENT CONTENT (Retrieved Chunks):
═══════════════════════════════════════
{doc_context}

═══════════════════════════════════════
🚨 SCAN VIOLATIONS FOUND:
═══════════════════════════════════════
{violations_context}

═══════════════════════════════════════
📋 ACTIVE COMPLIANCE RULES:
═══════════════════════════════════════
{rules_context}

═══════════════════════════════════════
🏢 CORPORATE POLICIES:
═══════════════════════════════════════
{policy_context}

═══════════════════════════════════════
📚 HISTORICAL REMEDIATIONS:
═══════════════════════════════════════
{remediation_context}

═══════════════════════════════════════
INSTRUCTIONS (FOLLOW STRICTLY):
1. ALWAYS answer from the CURRENT DOCUMENT first. The "Document Content" section above is your PRIMARY source of truth.
2. When the user asks about data in their document (names, phones, emails, etc.), answer ONLY from "Document Content" — never cite historical remediations as the answer.
3. Historical Remediations are ONLY for reference on how similar issues were fixed in the PAST. Never confuse them with the current document.
4. When the user asks "should I remove X" or "what to do", check the ACTIVE COMPLIANCE RULES above. If a rule matches (e.g., Phone Number Detection = High severity), be DECISIVE: state clearly that it violates the rule and recommend removal. Do NOT say "there is no specific rule" if a matching rule exists.
5. Cross-reference violations, rules, and policies to give specific, actionable advice.
6. Be concise, clear, and professional. Use markdown formatting."""

                try:
                    response = llm_service.analyze(system_prompt, prompt, expect_json=False)
                    if isinstance(response, dict):
                        response = str(response)
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error communicating with LLM: {e}")
