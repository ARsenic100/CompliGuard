# Live Demo Script

## Pre-Demo Setup

```bash
# 1. Ensure environment is ready
cd pdf-compliance-scanner
source venv/bin/activate

# 2. Verify .env file has GROQ_API_KEY
cat .env

# 3. Generate sample PDFs
python -m sample_pdfs.generate_samples

# 4. Start the application
streamlit run main.py
```

## Demo Flow (10-12 minutes)

### Step 1: Introduction (1 min)

**Talking Point:**
"This is the AI-Powered PDF Compliance Scanner. It uses GROQ's Llama 3.1 model orchestrated by LangGraph to automatically detect compliance violations in PDF documents."

**Action:**
- Show the main UI with sidebar navigation
- Point out the dark gradient sidebar, model info, and navigation options

---

### Step 2: Rules Management (2 min)

**Talking Point:**
"Before we scan, let's look at our dynamic rule engine. Rules drive the compliance checks and can be modified without code changes."

**Action:**
1. Navigate to **⚙️ Rules Management**
2. Show the pre-loaded default rules grouped by category
3. Demonstrate adding a new custom rule:
   - Rule Name: "Detect AWS Keys"
   - Category: Confidential Information
   - Severity: Critical
   - Pattern: `AKIA[0-9A-Z]{16}`
   - Click "Add Rule"
4. Toggle a rule off/on to show dynamic control

---

### Step 3: Upload & Scan (3 min)

**Talking Point:**
"Now let's scan a document. I'll upload our test PDF that contains PII, confidential data, and problematic content."

**Action:**
1. Navigate to **📤 Upload & Scan**
2. Upload `sample_pdfs/sample_mixed_violations.pdf`
3. Point out the file metadata cards (name, size, type)
4. Click **🚀 Start Scan**
5. Watch the progress bar and processing logs:
   - "🔍 Validating PDF file..."
   - "📄 Extracting text from PDF pages..."
   - "🔐 Running PII detection..."
   - "🔒 Running confidential information detection..."
   - "⚠️ Running encoding validation..."
   - "🚫 Running toxicity detection..."
   - "📝 Generating compliance reports..."
6. Review the results summary showing compliance score and violation counts

**Expected Output:**
- Compliance Score: ~50-70% (Non-Compliant or Warning)
- Multiple PII violations (emails, phone numbers, SSN, PAN)
- Confidential info violations (API keys, passwords, financial data)
- Toxicity violations (threats, harassment references)

---

### Step 4: Compliance Results Dashboard (3 min)

**Talking Point:**
"Let's dive into the detailed results. The dashboard provides interactive charts and page-by-page analysis."

**Action:**
1. Navigate to **📊 Compliance Results**
2. Show the compliance score gauge meter
3. Point out the download buttons (JSON and PDF reports)
4. Switch to the **📊 Charts** tab:
   - Severity distribution pie chart
   - Category distribution bar chart
   - Page-wise violation heatmap
   - Compliance score gauge
5. Switch to **📄 Page-wise** tab:
   - Expand Page 1 to show PII violations
   - Expand Page 2 to show confidential info violations
   - Expand Page 3 to show toxicity violations
   - Note that Page 4 has no violations (clean page)
6. Switch to **📋 All Violations** tab:
   - Use severity filter to show only Critical violations
   - Use search to find specific violation types

---

### Step 5: Report Download (1 min)

**Talking Point:**
"Reports can be downloaded for compliance records and audit trails."

**Action:**
1. Download the JSON report — show the structure
2. Download the PDF report — show executive summary and violation tables

---

### Step 6: Scan History (1 min)

**Talking Point:**
"Every scan is automatically saved to history for audit trails."

**Action:**
1. Navigate to **📜 Scan History**
2. Show the scan record with timestamp, score, and violation count
3. Show report download buttons

---

### Step 7: Architecture Walkthrough (1 min)

**Talking Point:**
"Under the hood, LangGraph orchestrates the entire pipeline. The four detection agents run in parallel for performance."

**Action:**
- Show the architecture diagram from the README or docs
- Highlight: parallel execution, hybrid detection, state management

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "GROQ_API_KEY not set" | Add key to `.env` file |
| Slow scanning | GROQ has rate limits — wait and retry |
| No violations found | Use sample PDFs with known violations |
| Import errors | Run `pip install -r requirements.txt` |

## Key Demo Takeaways

1. **AI understands context** — Not just pattern matching
2. **Page-wise analysis** — Know exactly where violations are
3. **Dynamic rules** — Customize without code changes
4. **Production-ready** — Error handling, logging, reports
5. **Extensible architecture** — Easy to add new checks
