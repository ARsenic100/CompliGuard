"""
Report Generation Service
===========================
Generates compliance reports in JSON and PDF formats.
Includes executive summaries, violation tables, charts, and AI explanations.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config.settings import REPORT_OUTPUT_DIR
from app.utils.helpers import (
    count_violations_by_category,
    count_violations_by_severity,
    format_file_size,
    get_compliance_status,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ReportService:
    """
    Service for generating compliance scan reports.

    Supports:
        - JSON reports (machine-readable, full detail)
        - PDF reports (human-readable with tables and summaries)
    """

    def __init__(self) -> None:
        """Initialize report service and ensure output directory exists."""
        self.output_dir = Path(REPORT_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_json_report(
        self,
        scan_id: str,
        file_metadata: dict[str, Any],
        page_results: list[dict[str, Any]],
        compliance_summary: dict[str, Any],
        all_violations: list[dict[str, Any]],
    ) -> str:
        """
        Generate a JSON compliance report.

        Args:
            scan_id: Unique scan identifier.
            file_metadata: PDF file metadata dict.
            page_results: List of per-page result dicts.
            compliance_summary: Summary with scores and counts.
            all_violations: List of all violations.

        Returns:
            Path to the generated JSON report file.
        """
        report = {
            "report_metadata": {
                "report_id": scan_id,
                "generated_at": datetime.now().isoformat(),
                "generator": "AI-Powered PDF Compliance Scanner",
                "version": "1.0.0",
            },
            "file_metadata": file_metadata,
            "compliance_summary": compliance_summary,
            "violations": all_violations,
            "page_summaries": [
                {
                    "page_number": pr.get("page_number"),
                    "text_length": pr.get("text_length", 0),
                    "violation_count": len(pr.get("violations", [])),
                    "encoding_valid": pr.get("encoding_valid", True),
                    "violations": pr.get("violations", []),
                }
                for pr in page_results
            ],
            "statistics": {
                "violations_by_severity": count_violations_by_severity(all_violations),
                "violations_by_category": count_violations_by_category(all_violations),
            },
        }

        filename = f"compliance_report_{scan_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"JSON report generated: {filepath}")
        return str(filepath)

    def generate_pdf_report(
        self,
        scan_id: str,
        file_metadata: dict[str, Any],
        page_results: list[dict[str, Any]],
        compliance_summary: dict[str, Any],
        all_violations: list[dict[str, Any]],
    ) -> str:
        """
        Generate a PDF compliance report with executive summary and violation tables.

        Args:
            scan_id: Unique scan identifier.
            file_metadata: PDF file metadata dict.
            page_results: List of per-page result dicts.
            compliance_summary: Summary with scores and counts.
            all_violations: List of all violations.

        Returns:
            Path to the generated PDF report file.
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
            from reportlab.lib.units import inch
            from reportlab.platypus import (
                Paragraph,
                SimpleDocTemplate,
                Spacer,
                Table,
                TableStyle,
            )
        except ImportError:
            logger.warning("ReportLab not installed. Generating JSON report only.")
            return self.generate_json_report(
                scan_id, file_metadata, page_results, compliance_summary, all_violations
            )

        filename = f"compliance_report_{scan_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = self.output_dir / filename

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50,
        )

        styles = getSampleStyleSheet()
        elements = []

        # --- Title ---
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Title"],
            fontSize=22,
            spaceAfter=20,
            textColor=colors.HexColor("#1a237e"),
        )
        elements.append(Paragraph("PDF Compliance Scan Report", title_style))
        elements.append(Spacer(1, 12))

        # --- Executive Summary ---
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#283593"),
            spaceAfter=10,
        )
        elements.append(Paragraph("Executive Summary", heading_style))

        score = compliance_summary.get("compliance_score", 100)
        status = compliance_summary.get("compliance_status", "Compliant")
        total_violations = compliance_summary.get("total_violations", 0)

        summary_data = [
            ["Metric", "Value"],
            ["Document", file_metadata.get("filename", "N/A")],
            ["File Size", format_file_size(file_metadata.get("file_size_bytes", 0))],
            ["Pages Scanned", str(compliance_summary.get("total_pages_scanned", 0))],
            ["Compliance Score", f"{score:.1f}%"],
            ["Status", status],
            ["Total Violations", str(total_violations)],
            ["Critical", str(compliance_summary.get("critical_count", 0))],
            ["High", str(compliance_summary.get("high_count", 0))],
            ["Medium", str(compliance_summary.get("medium_count", 0))],
            ["Low", str(compliance_summary.get("low_count", 0))],
            ["Scan Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ]

        summary_table = Table(summary_data, colWidths=[2.5 * inch, 4 * inch])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 11),
            ("FONTSIZE", (0, 1), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f5f5f5")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        # --- Violations Table ---
        if all_violations:
            elements.append(Paragraph("Violation Details", heading_style))

            violation_header = ["#", "Page", "Category", "Type", "Severity", "Confidence"]
            violation_rows = [violation_header]

            for i, v in enumerate(all_violations[:50], 1):  # Limit to 50 for PDF readability
                violation_rows.append([
                    str(i),
                    str(v.get("page_number", "N/A")),
                    str(v.get("category", "N/A"))[:25],
                    str(v.get("violation_type", "N/A"))[:25],
                    str(v.get("severity", "N/A")),
                    f"{v.get('confidence', 0):.0%}",
                ])

            v_table = Table(
                violation_rows,
                colWidths=[0.4 * inch, 0.5 * inch, 1.8 * inch, 1.8 * inch, 0.8 * inch, 0.8 * inch],
            )

            # Color-code severity
            severity_colors = {
                "Critical": colors.HexColor("#ffcdd2"),
                "High": colors.HexColor("#ffe0b2"),
                "Medium": colors.HexColor("#fff9c4"),
                "Low": colors.HexColor("#c8e6c9"),
            }

            style_commands = [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ]

            # Apply severity-based row coloring
            for row_idx, row in enumerate(violation_rows[1:], 1):
                severity = row[4]
                bg_color = severity_colors.get(severity, colors.white)
                style_commands.append(("BACKGROUND", (0, row_idx), (-1, row_idx), bg_color))

            v_table.setStyle(TableStyle(style_commands))
            elements.append(v_table)
            elements.append(Spacer(1, 20))

            if len(all_violations) > 50:
                elements.append(
                    Paragraph(
                        f"<i>Showing 50 of {len(all_violations)} violations. "
                        f"See JSON report for complete details.</i>",
                        styles["Normal"],
                    )
                )

        # --- Recommendations ---
        elements.append(Paragraph("Recommendations", heading_style))
        recommendations = self._generate_recommendations(compliance_summary, all_violations)
        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", styles["Normal"]))
            elements.append(Spacer(1, 4))

        # Build the PDF
        doc.build(elements)
        logger.info(f"PDF report generated: {filepath}")
        return str(filepath)

    @staticmethod
    def _generate_recommendations(
        summary: dict[str, Any],
        violations: list[dict[str, Any]],
    ) -> list[str]:
        """
        Generate actionable recommendations based on scan results.

        Args:
            summary: Compliance summary dict.
            violations: List of all violations.

        Returns:
            List of recommendation strings.
        """
        recommendations = []

        categories = count_violations_by_category(violations)

        if categories.get("PII / Personal Information", 0) > 0:
            recommendations.append(
                "Review and redact all personal identifiable information (PII) "
                "before distribution. Consider using automated PII redaction tools."
            )

        if categories.get("Confidential Information", 0) > 0:
            recommendations.append(
                "Mark the document as CONFIDENTIAL and restrict access. "
                "Remove or redact sensitive business information, API keys, and credentials."
            )

        if categories.get("Encoding Issue", 0) > 0:
            recommendations.append(
                "Re-export the PDF with proper UTF-8 encoding. "
                "Check the source document for corrupted characters."
            )

        if categories.get("Abusive / Unlawful Content", 0) > 0:
            recommendations.append(
                "Immediately review flagged content for abusive or unlawful material. "
                "Escalate to legal/compliance team if confirmed."
            )

        score = summary.get("compliance_score", 100)
        if score < 70:
            recommendations.append(
                "URGENT: This document is NON-COMPLIANT. Do not distribute "
                "until all critical and high-severity issues are resolved."
            )
        elif score < 90:
            recommendations.append(
                "Address medium and high-severity violations before final review."
            )

        if not recommendations:
            recommendations.append(
                "No significant compliance issues detected. Document is ready for review."
            )

        return recommendations
