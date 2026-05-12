"""
RAG Service Module
====================
Manages vector embeddings and retrieval using ChromaDB and local HuggingFace models.
"""

from __future__ import annotations

import os
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Directory for Chroma persistent storage
CHROMA_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "chroma_db")
os.makedirs(CHROMA_DB_DIR, exist_ok=True)

class RAGService:
    """Service for managing vector database operations."""

    def __init__(self) -> None:
        """Initialize the RAG service with local embeddings."""
        logger.info("Initializing RAG Service (Embeddings and Vector DB)...")
        # Use a lightweight, fast local embedding model
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        # Initialize global collections
        self.policies_store = Chroma(
            collection_name="corporate_policies",
            embedding_function=self.embeddings,
            persist_directory=CHROMA_DB_DIR
        )
        
        self.remediations_store = Chroma(
            collection_name="historical_remediations",
            embedding_function=self.embeddings,
            persist_directory=CHROMA_DB_DIR
        )

    # --- Document RAG (For specific scans) ---

    def embed_document(self, scan_id: str, pages: dict[int, str]) -> str:
        """
        Chunk and embed a specific document for a scan.
        
        Args:
            scan_id: Unique scan ID
            pages: Dictionary of page_number -> page_text
            
        Returns:
            The name of the collection created for this document.
        """
        collection_name = f"scan_{scan_id.replace('-', '_')}"
        
        docs = []
        for page_num, text in pages.items():
            if not text.strip():
                continue
            
            chunks = self.text_splitter.split_text(text)
            for chunk in chunks:
                docs.append(Document(
                    page_content=chunk,
                    metadata={"page_number": page_num, "scan_id": scan_id}
                ))
        
        if not docs:
            logger.warning(f"No text to embed for scan {scan_id}")
            return collection_name
            
        # Create a new collection for this specific scan
        Chroma.from_documents(
            documents=docs,
            embedding=self.embeddings,
            collection_name=collection_name,
            persist_directory=CHROMA_DB_DIR
        )
        
        logger.info(f"Embedded {len(docs)} chunks for scan {scan_id} into {collection_name}")
        return collection_name

    def query_document(self, scan_id: str, query: str, k: int = 5) -> list[Document]:
        """Query a specific document's vector collection."""
        collection_name = f"scan_{scan_id.replace('-', '_')}"
        try:
            store = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=CHROMA_DB_DIR
            )
            return store.similarity_search(query, k=k)
        except Exception as e:
            logger.error(f"Error querying document {scan_id}: {e}")
            return []

    # --- Corporate Policies RAG ---

    def add_corporate_policy(self, policy_name: str, text: str) -> int:
        """Add a corporate policy to the global vector store."""
        chunks = self.text_splitter.split_text(text)
        docs = [
            Document(page_content=chunk, metadata={"policy_name": policy_name})
            for chunk in chunks
        ]
        if docs:
            self.policies_store.add_documents(docs)
            logger.info(f"Added {len(docs)} chunks for policy: {policy_name}")
        return len(docs)

    def query_policies(self, query: str, k: int = 3) -> list[Document]:
        """Search corporate policies for context."""
        return self.policies_store.similarity_search(query, k=k)

    def delete_corporate_policy(self, policy_name: str) -> bool:
        """Remove all vector embeddings for a specific policy."""
        try:
            # Access the underlying ChromaDB collection to delete by metadata filter
            collection = self.policies_store._collection
            # Get IDs of documents matching this policy name
            results = collection.get(where={"policy_name": policy_name})
            if results and results["ids"]:
                collection.delete(ids=results["ids"])
                logger.info(f"Deleted {len(results['ids'])} embeddings for policy: {policy_name}")
                return True
            logger.warning(f"No embeddings found for policy: {policy_name}")
            return True  # Still return True — nothing to delete is fine
        except Exception as e:
            logger.error(f"Error deleting policy embeddings for {policy_name}: {e}")
            return False

    # --- Historical Remediations RAG ---

    def add_remediation(self, violation_type: str, violation_text: str, resolution: str) -> None:
        """Store a historical remediation."""
        content = f"Violation Type: {violation_type}\nIssue: {violation_text}\nResolution: {resolution}"
        doc = Document(
            page_content=content,
            metadata={"type": "remediation", "violation_type": violation_type}
        )
        self.remediations_store.add_documents([doc])
        logger.info(f"Added historical remediation for {violation_type}")

    def query_remediations(self, violation_query: str, k: int = 2, violation_type: str | None = None) -> list[Document]:
        """Find past resolutions, optionally filtered by exact violation type."""
        try:
            if violation_type:
                return self.remediations_store.similarity_search(
                    violation_query,
                    k=k,
                    filter={"violation_type": violation_type},
                )
            return self.remediations_store.similarity_search(violation_query, k=k)
        except Exception:
            return []

# Singleton instance
_rag_service = None

def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
