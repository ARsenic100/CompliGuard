# 🛡️ CompliGuard

> 🔍 An enterprise-grade AI compliance scanning platform that uses **Generative AI** (GROQ/Llama-3.1-8b), **RAG** (ChromaDB), and **rule-based validation** to scan uploaded PDFs for compliance violations, PII, toxicity, encoding issues, and corporate policy alignment.

[![Python 3.11](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38%2B-FF4B4B.svg)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2%2B-green.svg)](https://github.com/langchain-ai/langgraph)
[![GROQ](https://img.shields.io/badge/GROQ-API-orange.svg)](https://console.groq.com)

---

## 🌟 Features

- **📤 PDF Upload & Scan** — Drag-and-drop PDF upload with real-time scanning progress
- **🔐 PII Detection** — Hybrid regex + LLM detection of emails, phones, Aadhaar, PAN, SSN, passport numbers
- **🔒 Confidential Info Detection** — AI-powered semantic analysis for API keys, passwords, financial data, trade secrets
- **⚠️ Encoding Validation** — UTF-8 consistency checks for malformed characters, mojibake, and garbled text
- **🚫 Toxicity Detection** — LLM-based moderation for hate speech, threats, harassment, illegal content
- **📊 Interactive Dashboard** — Plotly charts, severity distribution, page-wise heatmap, compliance gauge
- **💬 Chat with Document** — RAG-based chat interface to query the scanned document against corporate policies
- **🏢 Corporate Policies** — Manage and embed corporate policies for context-aware compliance checking
- **⚙️ Dynamic Rule Engine** — Add, edit, delete, enable/disable rules through the UI
- **📜 Scan History** — Persistent scan history with downloadable reports
- **📥 Report Generation** — JSON and PDF compliance reports with executive summaries
- **🎯 Confidence Scoring** — Each violation includes confidence, severity, explanation, and remediation

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Streamlit UI                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ Upload & │ │ Results  │ │ Chat w/  │ │ Corporate│     │
│  │  Scan    │ │Dashboard │ │ Document │ │ Policies │     │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘     │
│  ┌────┴─────┐ ┌────┴─────┐                               │
│  │  Rules   │ │  Scan    │                               │
│  │ Manager  │ │ History  │                               │
│  └──────────┘ └──────────┘                               │
└───────┬────────────┬────────────┬────────────┬───────────┘
        │            │            │            │
┌───────▼────────────▼────────────▼────────────▼───────────┐
│                  LangGraph Workflow                      │
│  validate → extract → embed → rules → context →          │
│  ┌──────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │ PII  │ │Confident.│ │Encoding  │ │Toxicity  │         │
│  └──┬───┘ └────┬─────┘ └────┬─────┘ └────┬─────┘         │
│     └──────────┴────────────┴────────────┘               │
│                  ↓ aggregate → report → store → END      │
└──────────────────────────────────────────────────────────┘
        │            │            │            │
┌───────▼────┐ ┌─────▼─────┐ ┌────▼───────┐ ┌──▼────────┐
│  GROQ LLM  │ │ ReportLab │ │ SQLite DB  │ │ ChromaDB  │
│Llama 3.1 8B│ │PDF Reports│ │Scan History│ │Vector DB  │
└────────────┘ └───────────┘ └────────────┘ └───────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11
- GROQ API key ([Get one here](https://console.groq.com/keys))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/ARsenic100/CompliGuard.git
cd CompliGuard

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 5. Generate sample PDFs & Presentation (optional)
python generate_5page_doc.py
python generate_mock_pdfs.py
python -m sample_pdfs.generate_samples

# 6. Run the application
streamlit run main.py
```

### Environment Setup

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.1-8b-instant
MODEL_TEMPERATURE=0
MAX_FILE_SIZE_MB=50
LOG_LEVEL=INFO
```

## 📁 Project Structure

```
pdf-compliance-scanner/
├── app/
│   ├── ui/                    # Streamlit pages and components
│   │   ├── pages/             # 6 main pages
│   │   ├── components.py      # Reusable UI widgets
│   │   └── theme.py           # CSS styling
│   ├── graph/                 # LangGraph workflow
│   │   ├── state.py           # TypedDict state
│   │   ├── nodes.py           # Node functions
│   │   └── workflow.py        # Graph builder
│   ├── agents/                # 4 compliance detectors
│   │   ├── pii_detector.py
│   │   ├── confidential_detector.py
│   │   ├── encoding_validator.py
│   │   └── toxicity_detector.py
│   ├── services/              # Core services
│   │   ├── llm_service.py     # GROQ wrapper
│   │   ├── pdf_service.py     # PyMuPDF
│   │   └── report_service.py  # Report generation
│   ├── storage/               # Database & rules
│   ├── prompts/               # LLM prompt templates
│   ├── config/                # Settings
│   ├── models/                # Pydantic schemas
│   └── utils/                 # Logger, helpers, security
├── tests/                     # Unit tests
├── docs/                      # Documentation
├── sample_pdfs/               # Test PDFs
├── data/                      # Runtime data (uploads, reports, logs)
├── main.py                    # App entrypoint
├── requirements.txt
└── .env.example
```

## 🔄 How LangGraph Works

The scanning workflow is orchestrated by a **LangGraph StateGraph**:

1. **validate_pdf** — Validates file format, size, and PDF structure
2. **extract_text** — Extracts page-wise text using PyMuPDF
3. **embed_document** — Creates document embeddings using ChromaDB
4. **load_rules** — Loads enabled compliance rules from database
5. **retrieve_context** — Retrieves relevant policy chunks and historical remediations for RAG
6. **Parallel Fan-out** — 4 detection agents run simultaneously:
   - `pii_detection` (regex + LLM hybrid)
   - `confidential_detection` (keyword + LLM semantic)
   - `encoding_validation` (pure Python)
   - `toxicity_detection` (LLM moderation)
7. **aggregate_results** — Merges all results, calculates compliance score
8. **generate_report** — Creates JSON and PDF reports
9. **store_results** — Saves to SQLite database

### Compliance Scoring

```
Score = max(0, 100 - sum(severity_weights))

Severity Weights:
  Critical = 10 points
  High     = 7 points
  Medium   = 4 points
  Low      = 1 point

Status:
  90-100 → Compliant ✅
  70-89  → Warning ⚠️
  0-69   → Non-Compliant ❌
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## 🎮 Demo Instructions

1. Start the application: `streamlit run main.py`
2. Navigate to **📤 Upload & Scan**
3. Upload `sample_pdfs/sample_mixed_violations.pdf` or `5_Page_Violating_Document.pdf`
4. Click **🚀 Start Scan** and watch the AI analysis
5. Navigate to **📊 Compliance Results** for detailed charts
6. Go to **🏢 Corporate Policies** and add new policies using the uploaded `Mock_Corporate_Policy.pdf`
7. Navigate to **💬 Chat with Document** to ask questions about the violations and corporate policies
8. Try **⚙️ Rules Management** to add/edit rules
9. Check **📜 Scan History** for past scans

## 🔮 Future Enhancements

- OCR support for scanned PDFs (Tesseract integration)
- Multi-language compliance checking
- Custom LLM model support (OpenAI, Anthropic, local models)
- Batch PDF scanning
- REST API endpoint
- User authentication and role-based access
- Webhook notifications for compliance alerts
- Integration with document management systems

## 📄 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push and open a Pull Request
