"""
Application Configuration Module
=================================
Centralized configuration management with environment variable support.
All settings are loaded from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# PATH CONFIGURATION
# ============================================================================
# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
REPORTS_DIR = DATA_DIR / "reports"
RULES_DIR = DATA_DIR / "rules"
LOGS_DIR = DATA_DIR / "logs"

# Ensure all data directories exist
for directory in [UPLOADS_DIR, REPORTS_DIR, RULES_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# GROQ / LLM CONFIGURATION
# ============================================================================
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
MODEL_NAME: str = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
MODEL_TEMPERATURE: float = float(os.getenv("MODEL_TEMPERATURE", "0"))
LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "3"))
LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60"))

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================
MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_PAGES: int = int(os.getenv("MAX_PAGES", "500"))
ALLOWED_EXTENSIONS: list[str] = [".pdf"]

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DB_PATH: str = os.getenv("DB_PATH", str(DATA_DIR / "compliance_scanner.db"))

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE: str = str(LOGS_DIR / "compliance_scanner.log")

# ============================================================================
# COMPLIANCE SCORING CONFIGURATION
# ============================================================================
SEVERITY_WEIGHTS: dict[str, int] = {
    "Critical": 10,
    "High": 7,
    "Medium": 4,
    "Low": 1,
}

COMPLIANCE_THRESHOLDS: dict[str, tuple[int, int]] = {
    "Compliant": (90, 100),
    "Warning": (70, 89),
    "Non-Compliant": (0, 69),
}

# ============================================================================
# UI CONFIGURATION
# ============================================================================
APP_TITLE: str = "AI-Powered PDF Compliance Scanner"
APP_ICON: str = "🔍"
APP_LAYOUT: str = "wide"

# ============================================================================
# REPORT CONFIGURATION
# ============================================================================
REPORT_OUTPUT_DIR: str = os.getenv("REPORT_OUTPUT_DIR", str(REPORTS_DIR))

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================
MAX_FILENAME_LENGTH: int = 255
TEMP_FILE_CLEANUP_HOURS: int = 24
