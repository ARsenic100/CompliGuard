"""
Chat with Document UI Page
===========================
Interactive RAG chatbot to ask questions about scanned documents.
"""

import streamlit as st
from app.services.rag_service import get_rag_service
from app.storage.database import Database
from app.services.llm_service import get_llm_service
from app.prompts.templates import CONFIDENTIAL_SYSTEM_PROMPT

def render_chat_document_page() -> None:
    st.header("💬 Chat with Document (RAG)")
    
    st.markdown("""
    Use this interactive assistant to query uploaded documents for specific details 
    or ask for clarification regarding compliance violations.
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
        # Add user message to state and display
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching document..."):
                # Retrieve context from RAG
                docs = rag_service.query_document(scan_id, prompt, k=4)
                context = "\n\n".join([d.page_content for d in docs])
                
                if not context:
                    response = "I couldn't find relevant information in this document to answer your question."
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    return
                
                # Ask LLM
                system_prompt = (
                    "You are a helpful compliance assistant. Answer the user's question "
                    "using ONLY the provided document context. If the answer is not in the context, "
                    "say so clearly. Do not make up answers.\n\n"
                    f"CONTEXT FROM DOCUMENT:\n{context}"
                )
                
                try:
                    # Using expect_json=False because we want conversational text
                    response = llm_service.analyze(system_prompt, prompt, expect_json=False)
                    if isinstance(response, dict):
                        response = str(response)
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error communicating with LLM: {e}")
