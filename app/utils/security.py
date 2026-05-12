"""
Security Utilities
===================
File validation, upload security, and input sanitization
to protect against malicious uploads and injection attacks.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from app.config.settings import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES, MAX_FILENAME_LENGTH
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FileValidationError(Exception):
    """Raised when a file fails security validation."""
    pass


def validate_uploaded_file(
    file_bytes: bytes,
    filename: str,
) -> dict[str, str | int | bool]:
    """
    Validate an uploaded file for security and format compliance.

    Checks:
        - File size within limits
        - Allowed file extension
        - PDF magic bytes (header validation)
        - Filename sanitization
        - Filename length

    Args:
        file_bytes: Raw file content bytes.
        filename: Original filename.

    Returns:
        Dict with validation results including sanitized filename and file hash.

    Raises:
        FileValidationError: If any validation check fails.
    """
    # 1. Check file size
    file_size = len(file_bytes)
    if file_size == 0:
        raise FileValidationError("Uploaded file is empty.")
    if file_size > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        raise FileValidationError(
            f"File size ({file_size / (1024 * 1024):.1f} MB) exceeds "
            f"maximum allowed size ({max_mb:.0f} MB)."
        )

    # 2. Check file extension
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"File type '{ext}' is not allowed. Allowed types: {ALLOWED_EXTENSIONS}"
        )

    # 3. Validate PDF magic bytes (PDF files start with %PDF-)
    if not file_bytes[:5] == b"%PDF-":
        raise FileValidationError(
            "File does not appear to be a valid PDF (invalid header)."
        )

    # 4. Sanitize filename
    safe_filename = sanitize_filename(filename)

    # 5. Check filename length
    if len(safe_filename) > MAX_FILENAME_LENGTH:
        raise FileValidationError(
            f"Filename exceeds maximum length of {MAX_FILENAME_LENGTH} characters."
        )

    # 6. Calculate file hash for deduplication
    file_hash = hashlib.sha256(file_bytes).hexdigest()

    logger.info(f"File validated: {safe_filename} ({file_size} bytes, hash: {file_hash[:12]}...)")

    return {
        "valid": True,
        "filename": safe_filename,
        "file_size": file_size,
        "file_hash": file_hash,
        "extension": ext,
    }


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal and other attacks.

    Args:
        filename: Original filename.

    Returns:
        Sanitized filename safe for filesystem use.
    """
    # Remove path separators and get just the filename
    filename = Path(filename).name

    # Remove or replace potentially dangerous characters
    # Allow only alphanumeric, dots, hyphens, underscores, and spaces
    filename = re.sub(r'[^\w\s\-.]', '_', filename)

    # Remove leading/trailing whitespace and dots
    filename = filename.strip().strip('.')

    # Collapse multiple underscores/spaces
    filename = re.sub(r'[_\s]+', '_', filename)

    # Ensure the filename is not empty after sanitization
    if not filename:
        filename = "uploaded_document.pdf"

    return filename


def sanitize_text_input(text: str) -> str:
    """
    Sanitize text input to prevent injection attacks.

    Args:
        text: Raw text input.

    Returns:
        Sanitized text.
    """
    # Remove null bytes
    text = text.replace('\x00', '')

    # Limit length for safety
    max_input_length = 10000
    if len(text) > max_input_length:
        text = text[:max_input_length]

    return text
