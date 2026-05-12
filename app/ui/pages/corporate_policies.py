"""
Corporate Policies Management Page
====================================
Upload custom corporate rules to be used as RAG context for compliance scanning.
"""

import uuid
import streamlit as st
from app.services.rag_service import get_rag_service
from app.storage.database import Database
from app.services.pdf_service import PDFService
from app.utils.logger import get_logger

logger = get_logger(__name__)

def render_corporate_policies_page() -> None:
    st.header("🏢 Corporate Policies (RAG)")
    
    st.markdown("""
    Upload internal company manuals, employee handbooks, or security standards as PDFs.
    The system will embed these policies and use them to check future uploaded documents 
    for custom compliance violations.
    """)
    
    # Upload section
    uploaded_file = st.file_uploader("Upload Corporate Policy PDF", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("Add Policy to Knowledge Base"):
            with st.spinner("Processing and embedding policy..."):
                try:
                    file_bytes = uploaded_file.getvalue()
                    extracted_pages = PDFService.extract_text(file_bytes)
                    full_text = "\n".join(extracted_pages.values())
                    
                    if not full_text.strip():
                        st.error("Could not extract any text from the PDF.")
                    else:
                        rag_service = get_rag_service()
                        policy_name = uploaded_file.name
                        chunk_count = rag_service.add_corporate_policy(policy_name, full_text)
                        
                        # Save metadata
                        db = Database()
                        db.save_policy_metadata(str(uuid.uuid4()), policy_name, chunk_count)
                        
                        st.success(f"Successfully embedded '{policy_name}' ({chunk_count} chunks).")
                        st.balloons()
                except Exception as e:
                    st.error(f"Error processing policy: {e}")
                    logger.error(f"Error embedding policy {uploaded_file.name}: {e}")
    
    st.divider()
    
    st.subheader("Active Policies in Knowledge Base")
    db = Database()
    policies = db.get_policies()
    
    if not policies:
        st.info("No corporate policies have been added yet.")
    else:
        for p in policies:
            with st.container(border=True):
                cols = st.columns([3, 1, 1, 1])
                cols[0].markdown(f"**{p['policy_name']}**")
                cols[1].markdown(f"Chunks: `{p['chunk_count']}`")
                cols[2].caption(p['upload_date'][:10])
                policy_name = p['policy_name']
                if cols[3].button("🗑️ Delete", key=f"del_{p['id']}", type="primary"):
                    with st.spinner(f"Deleting '{policy_name}'..."):
                        rag_service = get_rag_service()
                        rag_service.delete_corporate_policy(policy_name)
                        db.delete_policy(policy_name)
                        st.success(f"Deleted '{policy_name}' and its embeddings.")
                        st.rerun()
