import collections
import collections.abc
from pptx import Presentation
from pptx.util import Inches, Pt, Cm
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# Fix for pptx collections issue in newer python versions
collections.Mapping = collections.abc.Mapping
collections.Sequence = collections.abc.Sequence

def add_red_accent(slide):
    # Add the signature red line accent on the left
    left = Cm(1.5)
    top = Cm(1.5)
    width = Cm(0.15)
    height = Cm(2.0)
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(228, 32, 45)
    shape.line.color.rgb = RGBColor(228, 32, 45)
    return left + width + Cm(0.3), top

def add_horizontal_red_accent(slide, left, top, width=Cm(2.0)):
    height = Cm(0.15)
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(228, 32, 45)
    shape.line.color.rgb = RGBColor(228, 32, 45)

def format_title(title_shape, text, font_size=Pt(32), color=RGBColor(25, 55, 109)):
    title_shape.text = text
    for paragraph in title_shape.text_frame.paragraphs:
        for run in paragraph.runs:
            run.font.name = 'Arial'
            run.font.size = font_size
            run.font.bold = True
            run.font.color.rgb = color

def format_subtitle(shape, text, font_size=Pt(16), color=RGBColor(80, 80, 80)):
    shape.text = text
    for paragraph in shape.text_frame.paragraphs:
        for run in paragraph.runs:
            run.font.name = 'Arial'
            run.font.size = font_size
            run.font.color.rgb = color

def create_presentation():
    prs = Presentation()
    
    # Use blank layout for custom designs
    blank_layout = prs.slide_layouts[6]

    # Colors
    dark_blue = RGBColor(25, 55, 109)
    red_accent = RGBColor(228, 32, 45)
    gray_text = RGBColor(80, 80, 80)
    light_bg = RGBColor(245, 245, 245)

    # -----------------------------------------
    # Slide 1: Title Slide
    # -----------------------------------------
    slide = prs.slides.add_slide(blank_layout)
    left, top = add_red_accent(slide)
    
    title_box = slide.shapes.add_textbox(left, top - Cm(0.3), Inches(8), Inches(1.5))
    format_title(title_box, "CompliGuard\nClient Presentation", Pt(40))
    
    subtitle_box = slide.shapes.add_textbox(left, top + Cm(3.0), Inches(8), Inches(1))
    format_subtitle(subtitle_box, "Enterprise-Grade AI Compliance Scanning Platform\n\nMay 2026", Pt(18))
    
    # Add a stylish background shape on the right (like the image)
    right_shape = slide.shapes.add_shape(MSO_SHAPE.RIGHT_TRIANGLE, Inches(5), Inches(0), Inches(5), Inches(7.5))
    right_shape.fill.solid()
    right_shape.fill.fore_color.rgb = light_bg
    right_shape.line.fill.background()
    right_shape.rotation = 180

    # -----------------------------------------
    # Slide 2: Agenda
    # -----------------------------------------
    slide = prs.slides.add_slide(blank_layout)
    title_box = slide.shapes.add_textbox(Cm(1.5), Cm(1.0), Inches(8), Inches(1))
    format_title(title_box, "Agenda", Pt(28))
    add_horizontal_red_accent(slide, Cm(1.6), Cm(2.2), width=Cm(3.0))

    agenda_items = [
        "01    Executive Summary",
        "02    Key Features",
        "03    System Architecture",
        "04    LangGraph Workflow",
        "05    Core Detection Engines"
    ]
    
    agenda_items_2 = [
        "06    Compliance Rules & Scoring",
        "07    Technology Stack",
        "08    Use Cases & Impact",
        "09    Demonstration Flow",
        "10    Future Roadmap"
    ]

    for i, item in enumerate(agenda_items):
        tb = slide.shapes.add_textbox(Cm(1.5), Cm(3.5 + i*1.2), Inches(4), Inches(0.8))
        format_subtitle(tb, item, Pt(18), dark_blue)
        tb.text_frame.paragraphs[0].runs[0].font.bold = True

    for i, item in enumerate(agenda_items_2):
        tb = slide.shapes.add_textbox(Cm(12.0), Cm(3.5 + i*1.2), Inches(4), Inches(0.8))
        format_subtitle(tb, item, Pt(18), dark_blue)
        tb.text_frame.paragraphs[0].runs[0].font.bold = True

    # -----------------------------------------
    # Slide 3: Executive Summary
    # -----------------------------------------
    slide = prs.slides.add_slide(blank_layout)
    title_box = slide.shapes.add_textbox(Cm(1.5), Cm(1.0), Inches(8), Inches(1))
    format_title(title_box, "What is CompliGuard?", Pt(28))
    add_horizontal_red_accent(slide, Cm(1.6), Cm(2.2), width=Cm(3.0))

    content = (
        "CompliGuard is an enterprise-grade AI compliance scanning platform designed to "
        "automate and enhance the review of PDF documents.\n\n"
        "It leverages the power of Generative AI (GROQ/Llama-3.1-8b) alongside "
        "deterministic rule-based validation to ensure absolute accuracy and safety.\n\n"
        "Key Capabilities:\n"
        "• Deep inspection of PDFs for compliance violations\n"
        "• Detection of PII, Toxicity, and Confidential Information\n"
        "• Real-time interactive dashboard with drill-down analytics\n"
        "• Granular dynamic rule management\n"
    )
    
    tb = slide.shapes.add_textbox(Cm(1.5), Cm(3.5), Inches(8), Inches(3.5))
    tb.text = content
    for paragraph in tb.text_frame.paragraphs:
        paragraph.font.size = Pt(16)
        paragraph.font.name = 'Arial'
        paragraph.font.color.rgb = gray_text
        paragraph.space_after = Pt(12)

    # -----------------------------------------
    # Slide 4: Key Features (Cards Layout)
    # -----------------------------------------
    slide = prs.slides.add_slide(blank_layout)
    title_box = slide.shapes.add_textbox(Cm(1.5), Cm(1.0), Inches(8), Inches(1))
    format_title(title_box, "Comprehensive Features", Pt(28))
    add_horizontal_red_accent(slide, Cm(1.6), Cm(2.2), width=Cm(3.0))

    features = [
        ("AI-Powered Scanning", "Hybrid regex and LLM-based detection of PII, Toxicity, and Confidential Info."),
        ("Interactive Dashboard", "Plotly charts, severity distribution, page-wise heatmap, and compliance gauge."),
        ("Dynamic Rule Engine", "Add, edit, delete, and toggle compliance rules instantly through the UI."),
        ("Comprehensive Reporting", "Downloadable JSON and PDF compliance reports with executive summaries.")
    ]

    for i, (title, desc) in enumerate(features):
        row = i // 2
        col = i % 2
        left = Cm(1.5 + col*12.0)
        top = Cm(3.5 + row*5.0)
        
        # Card Background
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Cm(11.0), Cm(4.0))
        shape.fill.solid()
        shape.fill.fore_color.rgb = light_bg
        shape.line.color.rgb = dark_blue
        
        # Card Title
        tb = slide.shapes.add_textbox(left + Cm(0.5), top + Cm(0.5), Cm(10.0), Cm(1.0))
        format_subtitle(tb, title, Pt(16), dark_blue)
        tb.text_frame.paragraphs[0].runs[0].font.bold = True
        
        # Card Desc
        tb2 = slide.shapes.add_textbox(left + Cm(0.5), top + Cm(1.5), Cm(10.0), Cm(2.0))
        format_subtitle(tb2, desc, Pt(14), gray_text)
        tb2.text_frame.word_wrap = True

    # -----------------------------------------
    # Slide 5: System Architecture
    # -----------------------------------------
    slide = prs.slides.add_slide(blank_layout)
    title_box = slide.shapes.add_textbox(Cm(1.5), Cm(1.0), Inches(8), Inches(1))
    format_title(title_box, "System Architecture", Pt(28))
    add_horizontal_red_accent(slide, Cm(1.6), Cm(2.2), width=Cm(3.0))

    boxes = [
        ("Streamlit UI", Cm(1.5), Cm(4.0), dark_blue, RGBColor(255,255,255)),
        ("LangGraph Workflow", Cm(9.5), Cm(4.0), red_accent, RGBColor(255,255,255)),
        ("GROQ LLM", Cm(17.5), Cm(4.0), dark_blue, RGBColor(255,255,255)),
        ("SQLite / ReportLab", Cm(9.5), Cm(9.0), dark_blue, RGBColor(255,255,255))
    ]

    for text, left, top, bg_color, fg_color in boxes:
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Cm(6.0), Cm(3.0))
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.fill.background()
        
        tb = shape.text_frame
        tb.text = text
        tb.paragraphs[0].alignment = PP_ALIGN.CENTER
        tb.paragraphs[0].font.bold = True
        tb.paragraphs[0].font.size = Pt(16)
        tb.paragraphs[0].font.color.rgb = fg_color

    # Add arrows
    slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Cm(7.7), Cm(5.0), Cm(1.5), Cm(1.0))
    slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Cm(15.7), Cm(5.0), Cm(1.5), Cm(1.0))
    slide.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Cm(12.0), Cm(7.2), Cm(1.0), Cm(1.5))

    # -----------------------------------------
    # Slide 6: LangGraph Workflow
    # -----------------------------------------
    slide = prs.slides.add_slide(blank_layout)
    title_box = slide.shapes.add_textbox(Cm(1.5), Cm(1.0), Inches(8), Inches(1))
    format_title(title_box, "Orchestration with LangGraph", Pt(28))
    add_horizontal_red_accent(slide, Cm(1.6), Cm(2.2), width=Cm(3.0))

    workflow = [
        "1. validate_pdf & extract_text (PyMuPDF)",
        "2. load_rules (SQLite DB)",
        "3. Parallel Fan-out Detection Agents:",
        "    - PII Detection",
        "    - Confidential Info",
        "    - Encoding Validation",
        "    - Toxicity Detection",
        "4. aggregate_results (Score Calculation)",
        "5. generate_report (ReportLab PDF / JSON)",
        "6. store_results"
    ]

    tb = slide.shapes.add_textbox(Cm(1.5), Cm(3.5), Inches(8), Inches(4))
    tb.text = "\n".join(workflow)
    for i, paragraph in enumerate(tb.text_frame.paragraphs):
        paragraph.font.size = Pt(16)
        paragraph.font.name = 'Arial'
        paragraph.font.color.rgb = dark_blue if i in [2, 7] else gray_text
        paragraph.font.bold = (i in [2, 7])
        paragraph.space_after = Pt(8)

    # -----------------------------------------
    # Slide 7: Core Detection Engines
    # -----------------------------------------
    slide = prs.slides.add_slide(blank_layout)
    title_box = slide.shapes.add_textbox(Cm(1.5), Cm(1.0), Inches(8), Inches(1))
    format_title(title_box, "Multi-Layered Detection Engines", Pt(28))
    add_horizontal_red_accent(slide, Cm(1.6), Cm(2.2), width=Cm(3.0))

    engines = [
        ("PII Detection", "Hybrid Regex + LLM\nIdentifies Emails, Phone numbers, Aadhaar, PAN, SSN.", Cm(1.5), Cm(3.5)),
        ("Confidential Data", "Semantic LLM Analysis\nDetects API keys, passwords, financial data, trade secrets.", Cm(13.0), Cm(3.5)),
        ("Encoding Validation", "Pure Python Rules\nChecks UTF-8 consistency, mojibake, and garbled text.", Cm(1.5), Cm(9.0)),
        ("Toxicity Detection", "LLM Moderation\nFlags hate speech, threats, harassment, illegal content.", Cm(13.0), Cm(9.0))
    ]

    for title, desc, left, top in engines:
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, Cm(10.5), Cm(4.0))
        shape.fill.solid()
        shape.fill.fore_color.rgb = dark_blue
        shape.line.fill.background()
        
        tb = shape.text_frame
        tb.text = title + "\n" + desc
        tb.paragraphs[0].font.bold = True
        tb.paragraphs[0].font.size = Pt(16)
        tb.paragraphs[0].font.color.rgb = RGBColor(255,255,255)
        tb.paragraphs[1].font.size = Pt(12)
        tb.paragraphs[1].font.color.rgb = RGBColor(200,200,200)

    # -----------------------------------------
    # Slide 8: Rules & Compliance Scoring
    # -----------------------------------------
    slide = prs.slides.add_slide(blank_layout)
    title_box = slide.shapes.add_textbox(Cm(1.5), Cm(1.0), Inches(8), Inches(1))
    format_title(title_box, "Dynamic Rules & Scoring Mechanism", Pt(28))
    add_horizontal_red_accent(slide, Cm(1.6), Cm(2.2), width=Cm(3.0))

    score_text = (
        "Compliance Score Calculation:\n"
        "Score = max(0, 100 - sum(severity_weights))\n\n"
        "Severity Weights:\n"
        "• Critical: 10 points\n"
        "• High: 7 points\n"
        "• Medium: 4 points\n"
        "• Low: 1 point\n\n"
        "Status Thresholds:\n"
        "✅ 90-100: Compliant\n"
        "⚠️ 70-89: Warning\n"
        "❌ 0-69: Non-Compliant"
    )

    tb = slide.shapes.add_textbox(Cm(1.5), Cm(3.5), Inches(8), Inches(4))
    tb.text = score_text
    for p in tb.text_frame.paragraphs:
        p.font.size = Pt(16)
        p.font.name = 'Arial'
        p.font.color.rgb = gray_text
        p.space_after = Pt(6)

    # -----------------------------------------
    # Slide 9: Technology Stack
    # -----------------------------------------
    slide = prs.slides.add_slide(blank_layout)
    title_box = slide.shapes.add_textbox(Cm(1.5), Cm(1.0), Inches(8), Inches(1))
    format_title(title_box, "Technology Stack", Pt(28))
    add_horizontal_red_accent(slide, Cm(1.6), Cm(2.2), width=Cm(3.0))

    stack_cats = [
        ("Frontend", "Streamlit 1.38+, Plotly"),
        ("Orchestration", "LangGraph 0.2+, LangChain"),
        ("AI / Model", "GROQ API, Llama-3.1-8b"),
        ("Data Layer", "SQLite, PyMuPDF, ReportLab")
    ]

    for i, (cat, tools) in enumerate(stack_cats):
        left = Cm(1.5)
        top = Cm(4.0 + i*2.5)
        
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, Cm(6.0), Cm(1.5))
        shape.fill.solid()
        shape.fill.fore_color.rgb = dark_blue
        shape.line.fill.background()
        
        tb = shape.text_frame
        tb.text = cat
        tb.paragraphs[0].alignment = PP_ALIGN.CENTER
        tb.paragraphs[0].font.bold = True
        tb.paragraphs[0].font.color.rgb = RGBColor(255,255,255)

        shape_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left + Cm(6.2), top, Cm(12.0), Cm(1.5))
        shape_bg.fill.solid()
        shape_bg.fill.fore_color.rgb = light_bg
        shape_bg.line.color.rgb = light_bg
        
        tb_bg = shape_bg.text_frame
        tb_bg.text = tools
        tb_bg.paragraphs[0].alignment = PP_ALIGN.LEFT
        tb_bg.paragraphs[0].font.color.rgb = gray_text
        tb_bg.paragraphs[0].font.size = Pt(14)

    # -----------------------------------------
    # Slide 10: Future Roadmap
    # -----------------------------------------
    slide = prs.slides.add_slide(blank_layout)
    title_box = slide.shapes.add_textbox(Cm(1.5), Cm(1.0), Inches(8), Inches(1))
    format_title(title_box, "Future Enhancements & Roadmap", Pt(28))
    add_horizontal_red_accent(slide, Cm(1.6), Cm(2.2), width=Cm(3.0))

    roadmap = [
        ("OCR Support", "Tesseract integration for scanning image-based PDFs."),
        ("Multi-Language", "Global compliance checking support for multiple languages."),
        ("Model Flexibility", "Support for OpenAI, Anthropic, and local LLMs."),
        ("Enterprise Integrations", "Batch PDF scanning, REST API endpoint, Webhook alerts.")
    ]

    for i, (title, desc) in enumerate(roadmap):
        tb = slide.shapes.add_textbox(Cm(1.5), Cm(3.5 + i*2.0), Inches(8), Inches(1))
        format_subtitle(tb, f"• {title}: {desc}", Pt(16), gray_text)
        tb.text_frame.paragraphs[0].runs[0].font.bold = True
        tb.text_frame.paragraphs[0].runs[0].font.color.rgb = dark_blue

    prs.save("CompliGuard_Presentation.pptx")

if __name__ == "__main__":
    create_presentation()
