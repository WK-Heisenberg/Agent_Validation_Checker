import pytest
from httpx import Response
from pytest_httpx import HTTPXMock

from src.validation.a2a_checks import run_a2a_checks
from src.validation.owasp_checks import run_owasp_checks

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

API_URL = "http://fake-agent-endpoint.test/api"
BEARER_TOKEN = "valid-super-secret-token"

# Helper function to find a specific result from the list
def find_result(results: list[dict], name: str) -> dict | None:
    """Finds a result dictionary by its 'name' key."""
    for result in results:
        if result.get("name") == name:
            return result
    return None

async def test_a2a_missing_credentials(httpx_mock: HTTPXMock):
    """Tests the 'Missing Credentials' check."""
    # PASS case: Endpoint correctly returns 401 Unauthorized
    httpx_mock.add_response(method="POST", url=API_URL, status_code=401)
    results, _ = await run_a2a_checks(API_URL, None)
    result = find_result(results, "Missing Credentials")
    assert result is not None
    assert result["status"] == "PASS"

    # FAIL case: Endpoint incorrectly returns 200 OK
    httpx_mock.add_response(method="POST", url=API_URL, status_code=200)
    results, _ = await run_a2a_checks(API_URL, None)
    result = find_result(results, "Missing Credentials")
    assert result is not None
    assert result["status"] == "FAIL"

async def test_a2a_malformed_header(httpx_mock: HTTPXMock):
    """Tests the 'Malformed Authorization Header' check."""
    # PASS case: Endpoint correctly returns 400 Bad Request
    httpx_mock.add_response(method="POST", url=API_URL, status_code=400)
    results, _ = await run_a2a_checks(API_URL, BEARER_TOKEN)
    result = find_result(results, "Malformed Authorization Header")
    assert result is not None
    assert result["status"] == "PASS"

    # FAIL case: Endpoint incorrectly accepts the request
    httpx_mock.add_response(method="POST", url=API_URL, status_code=200)
    results, _ = await run_a2a_checks(API_URL, BEARER_TOKEN)
    result = find_result(results, "Malformed Authorization Header")
    assert result is not None
    assert result["status"] == "FAIL"

async def test_a2a_invalid_credentials(httpx_mock: HTTPXMock):
    """Tests the 'Invalid Credentials' check."""
    # PASS case: Endpoint correctly returns 403 Forbidden
    httpx_mock.add_response(method="POST", url=API_URL, status_code=403)
    results, _ = await run_a2a_checks(API_URL, BEARER_TOKEN)
    result = find_result(results, "Invalid Credentials")
    assert result is not None
    assert result["status"] == "PASS"

async def test_a2a_malformed_json(httpx_mock: HTTPXMock):
    """Tests the 'Malformed JSON Syntax' check."""
    # Mock responses for all other checks to isolate this test
    httpx_mock.add_response(method="POST", url=API_URL, status_code=400, match_content=b'{"message_id": "123",,}')
    
    results, _ = await run_a2a_checks(API_URL, BEARER_TOKEN)
    result = find_result(results, "Malformed JSON Syntax")
    assert result is not None
    assert result["status"] == "PASS"

async def test_a2a_missing_required_fields(httpx_mock: HTTPXMock):
    """Tests the 'Missing Required Fields' check."""
    httpx_mock.add_response(method="POST", url=API_URL, status_code=422)
    results, _ = await run_a2a_checks(API_URL, BEARER_TOKEN)
    result = find_result(results, "Missing Required Fields")
    assert result is not None
    assert result["status"] == "PASS"

async def test_a2a_method_not_allowed(httpx_mock: HTTPXMock):
    """Tests the 'Method Not Allowed' check."""
    httpx_mock.add_response(method="GET", url=API_URL, status_code=405)
    results, _ = await run_a2a_checks(API_URL, BEARER_TOKEN)
    result = find_result(results, "Method Not Allowed")
    assert result is not None
    assert result["status"] == "PASS"

async def test_a2a_response_schema_validation(httpx_mock: HTTPXMock):
    """Tests the 'Response Schema Validation' check."""
    # PASS case: Valid request gets a 200 OK with a valid response body
    valid_response_body = {"status": "success", "message": "Received"}
    httpx_mock.add_response(method="POST", url=API_URL, status_code=200, json=valid_response_body)
    results, _ = await run_a2a_checks(API_URL, BEARER_TOKEN)
    result = find_result(results, "Response Schema Validation")
    assert result is not None
    assert result["status"] == "PASS"

    # FAIL case: Valid request gets a 200 OK but with a malformed response body
    invalid_response_body = {"error": "something went wrong"}
    httpx_mock.add_response(method="POST", url=API_URL, status_code=200, json=invalid_response_body)
    results, _ = await run_a2a_checks(API_URL, BEARER_TOKEN)
    result = find_result(results, "Response Schema Validation")
    assert result is not None
    assert result["status"] == "FAIL"
    # --- START OF CORRECTION ---
    # Update assertion to match the new, more specific error message
    assert "Response missing required field: 'status'" in result["details"]
    # --- END OF CORRECTION ---

async def test_owasp_prompt_injection(httpx_mock: HTTPXMock):
    """Tests the 'Prompt Injection' check."""
    # PASS case: Agent response does not indicate a successful injection
    httpx_mock.add_response(method="POST", url=API_URL, status_code=200, text="I cannot fulfill that request.")
    results, _ = await run_owasp_checks(API_URL, BEARER_TOKEN)
    result = find_result(results, "Prompt Injection (LLM01)")
    assert result is not None
    assert result["status"] == "PASS"

    # FAIL case: Agent response contains signs of a successful joke-telling injection
    httpx_mock.add_response(method="POST", url=API_URL, status_code=200, text="Of course, here is a joke about a computer.")
    results, _ = await run_owasp_checks(API_URL, BEARER_TOKEN)
    result = find_result(results, "Prompt Injection (LLM01)")
    assert result is not None
    assert result["status"] == "FAIL"

async def test_owasp_insecure_output_handling(httpx_mock: HTTPXMock):
    """Tests the 'Insecure Output Handling' check."""
    # PASS case: Response is clean
    httpx_mock.add_response(method="POST", url=API_URL, status_code=200, text="My name is Agent Smith.")
    results, _ = await run_owasp_checks(API_URL, BEARER_TOKEN)
    result = find_result(results, "Insecure Output Handling (LLM04)")
    assert result is not None
    assert result["status"] == "PASS"

    # FAIL case: Response contains a <script> tag
    httpx_mock.add_response(method="POST", url=API_URL, status_code=200, text="My name is <script>alert('XSS')</script>")
    results, _ = await run_owasp_checks(API_URL, BEARER_TOKEN)
    result = find_result(results, "Insecure Output Handling (LLM04)")
    assert result is not None
    assert result["status"] == "FAIL"