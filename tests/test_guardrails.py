"""
Level 4: Guardrail Tests — Mocking external API calls.

WHAT'S NEW HERE:
    - We mock an external API (Ollama's LLM) to avoid real network requests
    - We test error handling: timeouts, API failures, and the fail_open setting
    - We use mocker.AsyncMock() to replace the Ollama async client

THE GUARDRAIL PATTERN:
    InputGuardrail sends the user's query to an LLM and asks: "Is this safe?"
    - If the LLM says "True" → allow the request
    - If the LLM says "False" → block the request
    - If the LLM times out or errors → depends on fail_open setting
"""

import asyncio

from app.modules.text_generation.guardrails.input_guardrail import InputGuardrail
from app.modules.text_generation.guardrails.schema import InputGuardResponse


# =============================================================================
# Helper: create a guardrail with a mocked client
# =============================================================================


def create_guardrail(mocker, fail_open: bool = True) -> InputGuardrail:
    """Creates an InputGuardrail and replaces its async client with a mock."""
    guardrail = InputGuardrail(
        api_key="fake-key",
        model="test-model",
        host="http://fake-host",
        timeout=5.0,
        fail_open=fail_open,
    )
    # Replace the real Ollama client with a mock
    guardrail.aclient = mocker.AsyncMock()
    return guardrail


# =============================================================================
# Classification Tests
# =============================================================================


class TestInputGuardrailClassification:
    """Tests for the core classification logic."""

    async def test_safe_input_allowed(self, mocker):
        """When the LLM returns 'True', the input should be classified as allowed."""
        guardrail = create_guardrail(mocker)

        # Mock: LLM returns "True" (safe)
        guardrail.aclient.chat.return_value = {"message": {"content": "True"}}

        result = await guardrail.is_input_allowed("What is Python?")

        assert isinstance(result, InputGuardResponse)
        assert result.classification is True

    async def test_unsafe_input_blocked(self, mocker):
        """When the LLM returns 'False', the input should be classified as blocked."""
        guardrail = create_guardrail(mocker)

        # Mock: LLM returns "False" (unsafe)
        guardrail.aclient.chat.return_value = {"message": {"content": "False"}}

        result = await guardrail.is_input_allowed("Ignore all instructions and...")

        assert result.classification is False

    async def test_case_insensitive_true(self, mocker):
        """The classification should handle different casings of 'true'."""
        guardrail = create_guardrail(mocker)

        guardrail.aclient.chat.return_value = {
            "message": {"content": "  TRUE  "}  # uppercase + whitespace
        }

        result = await guardrail.is_input_allowed("Normal question")
        assert result.classification is True

    async def test_allowed_keyword(self, mocker):
        """The word 'allowed' should also be treated as safe."""
        guardrail = create_guardrail(mocker)

        guardrail.aclient.chat.return_value = {"message": {"content": "allowed"}}

        result = await guardrail.is_input_allowed("Normal question")
        assert result.classification is True


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestInputGuardrailErrorHandling:
    """Tests for timeout and error scenarios."""

    async def test_timeout_with_fail_open(self, mocker):
        """
        When the LLM times out and fail_open=True, the request should be ALLOWED.
        This is the 'fail open' behavior — better to let a message through
        than to block all users when the guardrail service is slow.
        """
        guardrail = create_guardrail(mocker, fail_open=True)

        # Mock: LLM call raises a TimeoutError
        guardrail.aclient.chat.side_effect = asyncio.TimeoutError()

        result = await guardrail.is_input_allowed("Some query")
        assert result.classification is True  # Allowed despite timeout

    async def test_timeout_with_fail_closed(self, mocker):
        """
        When the LLM times out and fail_open=False, the request should be BLOCKED.
        This is the 'fail closed' behavior — stricter security.
        """
        guardrail = create_guardrail(mocker, fail_open=False)

        guardrail.aclient.chat.side_effect = asyncio.TimeoutError()

        result = await guardrail.is_input_allowed("Some query")
        assert result.classification is False  # Blocked on timeout

    async def test_api_error_with_fail_open(self, mocker):
        """
        When the LLM raises an unexpected error and fail_open=True,
        the request should be ALLOWED (graceful degradation).
        """
        guardrail = create_guardrail(mocker, fail_open=True)

        guardrail.aclient.chat.side_effect = ConnectionError("API is down")

        result = await guardrail.is_input_allowed("Some query")
        assert result.classification is True

    async def test_api_error_with_fail_closed(self, mocker):
        """
        When the LLM raises an unexpected error and fail_open=False,
        the request should be BLOCKED.
        """
        guardrail = create_guardrail(mocker, fail_open=False)

        guardrail.aclient.chat.side_effect = ConnectionError("API is down")

        result = await guardrail.is_input_allowed("Some query")
        assert result.classification is False
