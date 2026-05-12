"""
Tests for PDF Service
========================
Unit tests for PDF validation, text extraction, and edge case handling.
"""

import pytest
from fpdf import FPDF


def _create_test_pdf(text: str = "Hello World", pages: int = 1) -> bytes:
    """Create a simple test PDF in memory."""
    pdf = FPDF()
    for i in range(pages):
        pdf.add_page()
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, f"{text} - Page {i + 1}", ln=True)
    return pdf.output()


class TestPDFService:
    """Tests for the PDF processing service."""

    def test_validate_valid_pdf(self):
        """Test that a valid PDF passes validation."""
        from app.services.pdf_service import PDFService
        pdf_bytes = _create_test_pdf()
        result = PDFService.validate_pdf(pdf_bytes)
        assert result["valid"] is True
        assert result["page_count"] == 1
        assert "metadata" in result

    def test_validate_multi_page_pdf(self):
        """Test validation of a multi-page PDF."""
        from app.services.pdf_service import PDFService
        pdf_bytes = _create_test_pdf(pages=5)
        result = PDFService.validate_pdf(pdf_bytes)
        assert result["page_count"] == 5

    def test_validate_invalid_pdf(self):
        """Test that an invalid file raises an error."""
        from app.services.pdf_service import PDFService, PDFServiceError
        with pytest.raises(PDFServiceError):
            PDFService.validate_pdf(b"Not a PDF file")

    def test_extract_text(self):
        """Test text extraction from a PDF."""
        from app.services.pdf_service import PDFService
        pdf_bytes = _create_test_pdf("Test Content", pages=3)
        pages = PDFService.extract_text(pdf_bytes)
        assert len(pages) == 3
        assert 1 in pages
        assert "Test Content" in pages[1]

    def test_extract_text_empty_pdf(self):
        """Test extraction from a PDF with empty pages."""
        from app.services.pdf_service import PDFService
        pdf = FPDF()
        pdf.add_page()  # Empty page
        pdf_bytes = pdf.output()
        pages = PDFService.extract_text(pdf_bytes)
        assert len(pages) == 1

    def test_get_page_count(self):
        """Test page count retrieval."""
        from app.services.pdf_service import PDFService
        pdf_bytes = _create_test_pdf(pages=7)
        count = PDFService.get_page_count(pdf_bytes)
        assert count == 7
