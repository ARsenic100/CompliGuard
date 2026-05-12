"""
Rules Management Page
========================
CRUD interface for managing compliance rules.
"""

from __future__ import annotations

import streamlit as st

from app.models.schemas import SeverityLevel, ViolationCategory
from app.storage.rules_store import RulesStore
from app.ui.components import render_gradient_divider, render_page_header, render_severity_badge
from app.utils.helpers import get_category_icon


def render_rules_management_page() -> None:
    """Render the Rules Management page."""
    render_page_header(
        "⚙️ Rules Management",
        "Add, edit, enable/disable, and delete compliance rules. Changes affect future scans.",
    )

    rules_store = RulesStore()
    rules = rules_store.get_all_rules()

    # === Add New Rule Section ===
    with st.expander("➕ Add New Rule", expanded=False):
        _render_add_rule_form(rules_store)

    render_gradient_divider()

    # === Existing Rules ===
    st.markdown(f"### 📋 Active Rules ({len(rules)})")

    if not rules:
        st.info("No rules configured. Add a rule above to get started.")
        return

    # Group rules by category
    categories: dict[str, list[dict]] = {}
    for rule in rules:
        cat = rule.get("category", "Unknown")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(rule)

    for category, cat_rules in categories.items():
        icon = get_category_icon(category)
        st.markdown(f"#### {icon} {category} ({len(cat_rules)} rules)")

        for rule in cat_rules:
            _render_rule_card(rule, rules_store)

        st.markdown("---")


def _render_add_rule_form(rules_store: RulesStore) -> None:
    """Render the add new rule form."""
    with st.form("add_rule_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            rule_name = st.text_input("Rule Name *", placeholder="e.g., Detect API Keys")
            category = st.selectbox(
                "Category *",
                [vc.value for vc in ViolationCategory],
            )
        with col2:
            severity = st.selectbox(
                "Severity *",
                [sl.value for sl in SeverityLevel],
                index=1,
            )
            enabled = st.checkbox("Enabled", value=True)

        description = st.text_area("Description", placeholder="What does this rule detect?")
        pattern = st.text_input("Regex Pattern (optional)", placeholder=r"e.g., sk-[a-zA-Z0-9]{20,}")
        keywords = st.text_input("Keywords (comma-separated, optional)", placeholder="e.g., secret, api_key, token")

        submitted = st.form_submit_button("➕ Add Rule", type="primary", use_container_width=True)

        if submitted:
            if not rule_name:
                st.error("Rule name is required.")
            else:
                keyword_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else []
                new_rule = {
                    "rule_name": rule_name,
                    "category": category,
                    "severity": severity,
                    "enabled": enabled,
                    "description": description,
                    "pattern": pattern if pattern else None,
                    "keywords": keyword_list,
                }
                rules_store.add_rule(new_rule)
                st.success(f"✅ Rule '{rule_name}' added successfully!")
                st.rerun()


def _render_rule_card(rule: dict, rules_store: RulesStore) -> None:
    """Render an individual rule card with toggle and delete options."""
    rule_id = rule.get("id", "")
    rule_name = rule.get("rule_name", "Unnamed Rule")
    severity = rule.get("severity", "Medium")
    enabled = rule.get("enabled", True)
    description = rule.get("description", "")
    pattern = rule.get("pattern", "")
    keywords = rule.get("keywords", [])

    col_info, col_toggle, col_delete = st.columns([4, 1, 1])

    with col_info:
        status_icon = "✅" if enabled else "⏸️"
        st.markdown(f"""
            **{status_icon} {rule_name}** {render_severity_badge(severity)}

            {f'*{description}*' if description else ''}
            {f'`Pattern: {pattern}`' if pattern else ''}
            {f'Keywords: {", ".join(keywords)}' if keywords else ''}
        """, unsafe_allow_html=True)

    with col_toggle:
        new_enabled = st.checkbox(
            "On",
            value=enabled,
            key=f"toggle_{rule_id}",
            label_visibility="collapsed",
        )
        if new_enabled != enabled:
            rules_store.toggle_rule(rule_id, new_enabled)
            st.rerun()

    with col_delete:
        if st.button("🗑️", key=f"delete_{rule_id}", help="Delete this rule"):
            rules_store.delete_rule(rule_id)
            st.success(f"Rule '{rule_name}' deleted.")
            st.rerun()
