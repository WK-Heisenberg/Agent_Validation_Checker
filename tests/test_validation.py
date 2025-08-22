# /tests/test_validation.py

import pytest
from httpx import AsyncClient, Response
from pytest_httpx import HTTPXMock

# Import the NEW, isolated functions
from src.validation.a2a_checks import (
    check_missing_credentials,
    check_malformed_header,
    check_invalid_credentials
)
# We still need the main owasp runner
from src.validation.owasp_checks import run_owasp_checks


# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

API_URL = "http://fake-agent-endpoint.test/api"
BEARER_TOKEN = "valid-super-secret-token"
VALID_PAYLOAD = {
    "message_id": "test-message-123", "sender_id": "validator-agent-456",
    "timestamp": 1678886400, "message": "This is a valid test message."
}

# --- A2A Checks ---

async def test_a2a_missing_credentials_pass(httpx_mock: HTTPXMock):
    """Tests PASS case for Missing Credentials check."""
    httpx_mock.add_response(method="POST", url=API_URL, status_code=401)
    
    async with AsyncClient() as client:
        result = await check_missing_credentials(client, API_URL, VALID_PAYLOAD)
    
    assert result["status"] == "PASS"

async def test_a2a_missing_credentials_fail(httpx_mock: HTTPXMock):
    """Tests FAIL case for Missing Credentials check."""
    httpx_mock.add_response(method="POST", url=API_URL, status_code=200)

    async with AsyncClient() as client:
        result = await check_missing_credentials(client, API_URL, VALID_PAYLOAD)
        
    assert result["status"] == "FAIL"

async def test_a2a_malformed_header_pass(httpx_mock: HTTPXMock):
    """Tests PASS case for Malformed Header check."""
    httpx_mock.add_response(method="POST", url=API_URL, status_code=400)

    async with AsyncClient() as client:
        result = await check_malformed_header(client, API_URL, VALID_PAYLOAD, BEARER_TOKEN)

    assert result["status"] == "PASS"

async def test_a2a_invalid_credentials_pass(httpx_mock: HTTPXMock):
    """Tests PASS case for Invalid Credentials check."""
    httpx_mock.add_response(method="POST", url=API_URL, status_code=403)
    
    async with AsyncClient() as client:
        result = await check_invalid_credentials(client, API_URL, VALID_PAYLOAD)

    assert result["status"] == "PASS"


# --- OWASP Checks (These can stay as they are, as the function is simpler) ---

# Helper function to find a specific result from the list
def find_result(results: list[dict], name: str) -> dict | None:
    for result in results:
        if result.get("name") == name:
            return result
    return None

async def test_owasp_prompt_injection(httpx_mock: HTTPXMock):
    """Tests the 'Prompt Injection' check."""
    # PASS case: Agent response does not indicate a successful injection
    httpx_mock.add_response(method="POST", url=API_URL, status_code=200, text="I cannot fulfill that request.")
    # FAIL case: Response for the other OWASP check
    httpx_mock.add_response(method="POST", url=API_URL, status_code=200, text="My name is Agent Smith.")
    
    results, _ = await run_owasp_checks(API_URL, BEARER_TOKEN)
    result = find_result(results, "Prompt Injection (LLM01)")
    
    assert result is not None
    assert result["status"] == "PASS"

async def test_owasp_insecure_output_handling(httpx_mock: HTTPXMock):
    """Tests the 'Insecure Output Handling' check."""
    # PASS case: Agent response does not indicate a successful injection
    httpx_mock.add_response(method="POST", url=API_URL, status_code=200, text="I cannot fulfill that request.")
    # FAIL case: Response for the other OWASP check
    httpx_mock.add_response(method="POST", url=API_URL, status_code=200, text="My name is <script>alert('XSS')</script>")
    
    results, _ = await run_owasp_checks(API_URL, BEARER_TOKEN)
    result = find_result(results, "Insecure Output Handling (LLM04)")

    assert result is not None
    assert result["status"] == "FAIL"