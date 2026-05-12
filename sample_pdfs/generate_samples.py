"""
Sample PDF Generator
=======================
Generates test PDF files containing various compliance violation types
for demo and testing purposes.

Usage:
    python -m sample_pdfs.generate_samples
"""

from pathlib import Path

from fpdf import FPDF


OUTPUT_DIR = Path(__file__).parent


def create_sample_pii_pdf() -> str:
    """Create a PDF containing PII examples."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Page 1: Email and Phone PII
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Employee Directory - CONFIDENTIAL", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 11)

    employees = [
        ("John Smith", "john.smith@acmecorp.com", "+1-555-123-4567", "123 Main Street, Springfield, IL 62704"),
        ("Jane Doe", "jane.doe@techstartup.io", "(408) 555-0199", "456 Oak Avenue, San Jose, CA 95101"),
        ("Raj Patel", "raj.patel@globalinc.com", "+91-98765-43210", "789 MG Road, Bangalore, Karnataka 560001"),
    ]

    for name, email, phone, address in employees:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, f"Name: {name}", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, f"Email: {email}", ln=True)
        pdf.cell(0, 7, f"Phone: {phone}", ln=True)
        pdf.cell(0, 7, f"Address: {address}", ln=True)
        pdf.ln(8)

    # Page 2: ID Numbers
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Identity Verification Records", ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 11)

    pdf.cell(0, 7, "Aadhaar Number: 1234 5678 9012", ln=True)
    pdf.cell(0, 7, "PAN Number: ABCDE1234F", ln=True)
    pdf.cell(0, 7, "SSN: 123-45-6789", ln=True)
    pdf.cell(0, 7, "Passport: J12345678", ln=True)
    pdf.cell(0, 7, "Date of Birth: DOB: 15/03/1990", ln=True)
    pdf.ln(10)
    pdf.cell(0, 7, "Credit Card: 4532 1234 5678 9012", ln=True)
    pdf.cell(0, 7, "IP Address: 192.168.1.100", ln=True)

    filepath = str(OUTPUT_DIR / "sample_pii_document.pdf")
    pdf.output(filepath)
    return filepath


def create_sample_confidential_pdf() -> str:
    """Create a PDF with confidential business information."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Page 1: Financial Projections
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "STRICTLY CONFIDENTIAL", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Q4 2026 Financial Projections", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 11)

    pdf.cell(0, 7, "Revenue Forecast: $45.2M (up 23% YoY)", ln=True)
    pdf.cell(0, 7, "EBITDA Projection: $12.8M (28.3% margin)", ln=True)
    pdf.cell(0, 7, "Q4 2026 earnings forecast: $3.50 per share", ln=True)
    pdf.cell(0, 7, "FY 2026 revenue projection: $165M", ln=True)
    pdf.ln(10)
    pdf.cell(0, 7, "This document contains proprietary trade secret information.", ln=True)
    pdf.cell(0, 7, "Distribution restricted under NDA agreement #2024-0847.", ln=True)

    # Page 2: API Keys and Credentials
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Development Environment Configuration", ln=True)
    pdf.ln(5)
    pdf.set_font("Courier", "", 10)

    pdf.cell(0, 7, "# Production API Configuration", ln=True)
    pdf.cell(0, 7, "api_key = sk-prod-a1b2c3d4e5f6g7h8i9j0k1l2m3n4", ln=True)
    pdf.cell(0, 7, "secret_key = super_secret_password_12345", ln=True)
    pdf.cell(0, 7, "password = MyDBP@ssw0rd!2024", ln=True)
    pdf.cell(0, 7, "access_token = ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijkl", ln=True)
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, "Internal strategy: Plan to acquire CompetitorX by Q2 2027.", ln=True)
    pdf.cell(0, 7, "Board has approved the acquisition budget of $500M.", ln=True)

    filepath = str(OUTPUT_DIR / "sample_confidential_document.pdf")
    pdf.output(filepath)
    return filepath


def create_sample_toxicity_pdf() -> str:
    """Create a PDF with potentially toxic/abusive content for testing."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Page 1: Content with threats and hate speech (for detection testing)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Content Moderation Test Document", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 11)

    pdf.cell(0, 7, "This document is created for compliance testing purposes.", ln=True)
    pdf.ln(5)
    pdf.cell(0, 7, "Section 1 - Threat Detection Test:", ln=True)
    pdf.cell(0, 7, "The suspect said: 'I will destroy the entire building", ln=True)
    pdf.cell(0, 7, "and kill everyone inside.' This statement was reported.", ln=True)
    pdf.ln(5)
    pdf.cell(0, 7, "Section 2 - Harassment Detection Test:", ln=True)
    pdf.cell(0, 7, "The employee filed a harassment complaint stating", ln=True)
    pdf.cell(0, 7, "continuous abuse and threats from the supervisor.", ln=True)
    pdf.ln(5)
    pdf.cell(0, 7, "Section 3 - Illegal Activity Reference:", ln=True)
    pdf.cell(0, 7, "Instructions for money laundering and fraud schemes", ln=True)
    pdf.cell(0, 7, "were discovered in the seized documents.", ln=True)

    filepath = str(OUTPUT_DIR / "sample_toxicity_document.pdf")
    pdf.output(filepath)
    return filepath


def create_sample_encoding_pdf() -> str:
    """Create a PDF with encoding issues for testing."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Encoding Test Document", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 11)

    pdf.cell(0, 7, "Normal text: This is a properly encoded document.", ln=True)
    pdf.ln(5)
    pdf.cell(0, 7, "The following are encoding test patterns:", ln=True)
    pdf.cell(0, 7, "Text with special chars: price is 100 euros.", ln=True)
    pdf.cell(0, 7, "Company name: Acme Corp (TM) - All rights reserved.", ln=True)

    filepath = str(OUTPUT_DIR / "sample_encoding_document.pdf")
    pdf.output(filepath)
    return filepath


def create_sample_mixed_pdf() -> str:
    """Create a comprehensive PDF with all types of violations."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Page 1: PII
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Comprehensive Test Document", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Page 1: Personal Information", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(5)
    pdf.cell(0, 7, "Contact: john.doe@example.com | Phone: +1-555-867-5309", ln=True)
    pdf.cell(0, 7, "SSN: 078-05-1120 | PAN: BNZAA2318J", ln=True)

    # Page 2: Confidential
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Page 2: Confidential Business Data", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(5)
    pdf.cell(0, 7, "CONFIDENTIAL - Internal Use Only", ln=True)
    pdf.cell(0, 7, "Revenue projection: $82M for FY2026", ln=True)
    pdf.cell(0, 7, "api_key = sk-live-abc123def456ghi789jkl012mno345", ln=True)
    pdf.cell(0, 7, "password = AdminP@ss2024!", ln=True)

    # Page 3: Abusive Content
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Page 3: Content Moderation Test", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(5)
    pdf.cell(0, 7, "Report excerpt: suspect threatened to bomb the facility", ln=True)
    pdf.cell(0, 7, "and made racist remarks against coworkers.", ln=True)

    # Page 4: Clean page
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Page 4: Clean Content", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.ln(5)
    pdf.cell(0, 7, "This page contains only normal, compliant text.", ln=True)
    pdf.cell(0, 7, "No violations should be detected on this page.", ln=True)
    pdf.cell(0, 7, "The company policy on data handling is attached.", ln=True)

    filepath = str(OUTPUT_DIR / "sample_mixed_violations.pdf")
    pdf.output(filepath)
    return filepath


def generate_all_samples() -> list[str]:
    """Generate all sample PDF files."""
    print("Generating sample PDFs...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    files = [
        create_sample_pii_pdf(),
        create_sample_confidential_pdf(),
        create_sample_toxicity_pdf(),
        create_sample_encoding_pdf(),
        create_sample_mixed_pdf(),
    ]

    for f in files:
        print(f"  Created: {f}")

    print(f"\nGenerated {len(files)} sample PDFs in {OUTPUT_DIR}")
    return files


if __name__ == "__main__":
    generate_all_samples()
