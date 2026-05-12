"""
PDF Processing Service
========================
Uses PyMuPDF (fitz) for PDF text extraction, metadata retrieval,
and page-wise content splitting. Handles corrupt, scanned, and empty PDFs.
"""

from __future__ import annotations

import io
from typing import Any

import fitz  # PyMuPDF

from app.config.settings import MAX_PAGES
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PDFServiceError(Exception):
    """Raised when PDF processing fails."""
    pass


class PDFService:
    """
    Service for processing PDF files using PyMuPDF.

    Provides:
        - Text extraction (page-wise)
        - Metadata retrieval
        - PDF validation
        - Handling of edge cases (corrupt, empty, scanned PDFs)
    """

    @staticmethod
    def validate_pdf(file_bytes: bytes) -> dict[str, Any]:
        """
        Validate that the file is a valid, readable PDF.

        Args:
            file_bytes: Raw PDF file bytes.

        Returns:
            Dict with validation results including page_count and metadata.

        Raises:
            PDFServiceError: If the PDF cannot be opened or is invalid.
        """
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            raise PDFServiceError(f"Cannot open PDF file: {e}") from e

        page_count = len(doc)

        if page_count == 0:
            doc.close()
            raise PDFServiceError("PDF has no pages.")

        if page_count > MAX_PAGES:
            doc.close()
            raise PDFServiceError(
                f"PDF has {page_count} pages, exceeding the maximum of {MAX_PAGES}."
            )

        # Extract metadata
        metadata = doc.metadata or {}
        clean_metadata = {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
        }

        doc.close()

        logger.info(f"PDF validated: {page_count} pages")

        return {
            "valid": True,
            "page_count": page_count,
            "metadata": clean_metadata,
        }

    @staticmethod
    def extract_text(file_bytes: bytes) -> dict[int, str]:
        """
        Extract text from all pages of a PDF.

        Args:
            file_bytes: Raw PDF file bytes.

        Returns:
            Dict mapping page numbers (1-indexed) to extracted text.

        Raises:
            PDFServiceError: If text extraction fails.
        """
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            raise PDFServiceError(f"Cannot open PDF for extraction: {e}") from e

        pages: dict[int, str] = {}
        empty_pages: list[int] = []

        for page_num in range(len(doc)):
            try:
                page = doc[page_num]
                text = page.get_text("text")  # Extract as plain text

                # Clean the extracted text
                text = text.strip()

                page_index = page_num + 1  # 1-indexed
                pages[page_index] = text

                if not text:
                    empty_pages.append(page_index)

            except Exception as e:
                logger.warning(f"Error extracting page {page_num + 1}: {e}")
                pages[page_num + 1] = ""
                empty_pages.append(page_num + 1)

        doc.close()

        if empty_pages:
            logger.warning(
                f"Empty pages detected (possibly scanned/image-only): {empty_pages}"
            )

        total_chars = sum(len(text) for text in pages.values())
        logger.info(
            f"Extracted text from {len(pages)} pages "
            f"({total_chars} total characters, {len(empty_pages)} empty pages)"
        )

        return pages

    @staticmethod
    def get_page_count(file_bytes: bytes) -> int:
        """
        Get the number of pages in a PDF.

        Args:
            file_bytes: Raw PDF file bytes.

        Returns:
            Number of pages.
        """
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            count = len(doc)
            doc.close()
            return count
        except Exception as e:
            raise PDFServiceError(f"Cannot read PDF: {e}") from e
