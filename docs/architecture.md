# System Architecture

## Architecture Diagram

```mermaid
graph TD
    subgraph UI["🖥️ Streamlit UI"]
        A1["📤 Upload & Scan"]
        A2["📊 Compliance Results"]
        A3["⚙️ Rules Management"]
        A4["📜 Scan History"]
    end

    subgraph LG["🔄 LangGraph Workflow Engine"]
        B1["validate_pdf"]
        B2["extract_text"]
        B3["load_rules"]

        subgraph Parallel["⚡ Parallel Detection"]
            C1["🔐 PII Detector<br/>Regex + LLM Hybrid"]
            C2["🔒 Confidential Detector<br/>Keyword + LLM Semantic"]
            C3["⚠️ Encoding Validator<br/>Pure Python"]
            C4["🚫 Toxicity Detector<br/>LLM Moderation"]
        end

        B4["aggregate_results"]
        B5["generate_report"]
        B6["store_results"]
    end

    subgraph Services["🔧 Services"]
        S1["GROQ LLM<br/>Llama 3.1 8B"]
        S2["PyMuPDF<br/>PDF Extraction"]
        S3["ReportLab<br/>PDF Reports"]
    end

    subgraph Storage["💾 Storage"]
        D1["SQLite DB<br/>Scan History"]
        D2["Rules Store<br/>JSON + SQLite"]
        D3["File Storage<br/>Reports & Uploads"]
    end

    A1 -->|"Upload PDF"| B1
    B1 -->|"Valid"| B2
    B1 -->|"Invalid"| END1["❌ Error"]
    B2 --> B3
    B3 --> C1 & C2 & C3 & C4
    C1 & C2 & C3 & C4 --> B4
    B4 --> B5
    B5 --> B6
    B6 -->|"Results"| A2

    C1 & C2 & C4 -.->|"API Calls"| S1
    B2 -.-> S2
    B5 -.-> S3

    B6 -.-> D1
    A3 -.-> D2
    B5 -.-> D3
    A4 -.-> D1
```

## State Flow

```mermaid
stateDiagram-v2
    [*] --> ValidatePDF: Upload PDF
    ValidatePDF --> ExtractText: Valid
    ValidatePDF --> Error: Invalid
    ExtractText --> LoadRules
    LoadRules --> ParallelChecks

    state ParallelChecks {
        [*] --> PIIDetection
        [*] --> ConfidentialDetection
        [*] --> EncodingValidation
        [*] --> ToxicityDetection
    }

    ParallelChecks --> AggregateResults
    AggregateResults --> GenerateReport
    GenerateReport --> StoreResults
    StoreResults --> [*]: Complete

    Error --> [*]: Return Error
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit | Web UI with interactive widgets |
| Orchestration | LangGraph | Stateful workflow management |
| AI/LLM | GROQ (Llama 3.1 8B) | Contextual compliance analysis |
| PDF Processing | PyMuPDF (fitz) | Text extraction and metadata |
| Data Models | Pydantic | Type-safe data validation |
| Database | SQLite | Scan history and rules storage |
| Reports | ReportLab | PDF report generation |
| Charts | Plotly | Interactive data visualization |
| Logging | Python logging | Structured application logging |

## Data Flow

1. **Input**: User uploads PDF via Streamlit UI
2. **Validation**: File size, type, PDF structure checked
3. **Extraction**: PyMuPDF extracts page-wise text
4. **Analysis**: 4 agents analyze text in parallel
5. **Aggregation**: Results merged, score calculated
6. **Reporting**: JSON + PDF reports generated
7. **Storage**: Results saved to SQLite
8. **Output**: Results displayed in dashboard
