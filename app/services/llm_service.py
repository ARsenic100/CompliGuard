"""
LLM Service Module
====================
Wrapper around GROQ's ChatGroq for structured LLM interactions.
Provides retry logic, JSON parsing, and error handling.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Optional

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app.config.settings import GROQ_API_KEY, LLM_MAX_RETRIES, LLM_TIMEOUT, MODEL_NAME, MODEL_TEMPERATURE
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    """
    Service for interacting with the GROQ LLM API.

    Provides methods for:
        - Sending structured prompts
        - Parsing JSON responses
        - Retry logic for transient failures
        - Error handling and fallbacks
    """

    def __init__(self) -> None:
        """Initialize the LLM service with GROQ configuration."""
        if not GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set. LLM features will be unavailable.")
            self._llm = None
            return

        self._llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=MODEL_NAME,
            temperature=MODEL_TEMPERATURE,
            max_retries=2,
            request_timeout=LLM_TIMEOUT,
        )
        logger.info(f"LLM Service initialized with model: {MODEL_NAME}")

    @property
    def is_available(self) -> bool:
        """Check if the LLM service is properly configured and available."""
        return self._llm is not None

    def analyze(
        self,
        system_prompt: str,
        user_prompt: str,
        expect_json: bool = True,
    ) -> dict[str, Any] | str:
        """
        Send a prompt to the LLM and get a response.

        Args:
            system_prompt: System-level instructions for the LLM.
            user_prompt: The user/analysis prompt with content to analyze.
            expect_json: If True, attempt to parse the response as JSON.

        Returns:
            Parsed JSON dict if expect_json=True, otherwise raw string response.

        Raises:
            LLMServiceError: If all retries are exhausted.
        """
        if not self.is_available:
            raise LLMServiceError("LLM service is not available. Check GROQ_API_KEY.")

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        last_error: Optional[Exception] = None

        for attempt in range(1, LLM_MAX_RETRIES + 1):
            try:
                logger.debug(f"LLM request attempt {attempt}/{LLM_MAX_RETRIES}")
                response = self._llm.invoke(messages)
                content = response.content.strip()

                if expect_json:
                    return self._parse_json_response(content)
                return content

            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error on attempt {attempt}: {e}")
                last_error = e
                # Don't retry JSON parse errors—they'll likely recur
                # Instead, try to extract JSON from the response
                try:
                    return self._extract_json_from_text(content)
                except Exception:
                    if attempt == LLM_MAX_RETRIES:
                        raise LLMServiceError(
                            f"Failed to parse LLM response as JSON after {LLM_MAX_RETRIES} attempts: {e}"
                        ) from e

            except Exception as e:
                logger.warning(f"LLM request failed on attempt {attempt}: {e}")
                last_error = e
                if attempt < LLM_MAX_RETRIES:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)

        raise LLMServiceError(
            f"LLM request failed after {LLM_MAX_RETRIES} attempts: {last_error}"
        )

    def analyze_batch(
        self,
        system_prompt: str,
        user_prompts: list[str],
        expect_json: bool = True,
    ) -> list[dict[str, Any] | str]:
        """
        Send multiple prompts sequentially and collect responses.

        Args:
            system_prompt: Shared system prompt for all requests.
            user_prompts: List of user prompts to process.
            expect_json: Whether to parse responses as JSON.

        Returns:
            List of responses (dicts or strings).
        """
        results = []
        for prompt in user_prompts:
            try:
                result = self.analyze(system_prompt, prompt, expect_json)
                results.append(result)
            except LLMServiceError as e:
                logger.error(f"Batch analysis failed for prompt: {e}")
                results.append({"error": str(e)})
        return results

    @staticmethod
    def _parse_json_response(content: str) -> dict[str, Any]:
        """
        Parse a JSON response from the LLM.

        Handles cases where the LLM wraps JSON in markdown code blocks.

        Args:
            content: Raw LLM response string.

        Returns:
            Parsed JSON dict.
        """
        # Try direct JSON parse first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code blocks
        return LLMService._extract_json_from_text(content)

    @staticmethod
    def _extract_json_from_text(text: str) -> dict[str, Any]:
        """
        Extract JSON from text that may contain markdown formatting.

        Args:
            text: Text potentially containing JSON within code blocks.

        Returns:
            Parsed JSON dict.

        Raises:
            json.JSONDecodeError: If no valid JSON found.
        """
        # Try to find JSON in code blocks
        patterns = [
            r'```json\s*\n(.*?)\n\s*```',  # ```json ... ```
            r'```\s*\n(.*?)\n\s*```',       # ``` ... ```
            r'\{[\s\S]*\}',                   # Bare JSON object
            r'\[[\s\S]*\]',                   # Bare JSON array
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue

        raise json.JSONDecodeError("No valid JSON found in response", text, 0)


class LLMServiceError(Exception):
    """Raised when an LLM service operation fails."""
    pass


# Singleton instance for use across the application
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """
    Get or create the singleton LLM service instance.

    Returns:
        LLMService instance.
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
