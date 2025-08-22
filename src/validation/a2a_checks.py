import httpx
import json

async def run_a2a_checks(api_url: str, bearer_token: str | None) -> tuple[list[dict], list[dict]]:
    """
    Runs the A2A protocol validation checks with robust network error handling.
    Returns a tuple containing a list of results and a list of request/response logs.
    """
    results = []
    logs = []
    token_provided = bearer_token and bearer_token.strip()
    auth_headers = {"Authorization": f"Bearer {bearer_token}"} if token_provided else {}
    valid_payload = {
        "message_id": "test-message-123",
        "sender_id": "validator-agent-456",
        "timestamp": 1678886400,
        "message": "This is a valid test message."
    }

    async def run_test(test_name: str, method: str, **kwargs):
        """Helper function to log requests/responses and handle network errors."""
        log_entry = {"test": test_name, "request": {"method": method, **kwargs}}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(method, **kwargs)
                # --- START OF CORRECTION ---
                # Capture the response details and add them to the log entry
                log_entry["response"] = {
                    "status_code": response.status_code,
                    "text": response.text
                }
                # --- END OF CORRECTION ---
                logs.append(log_entry)
                return response
        except httpx.RequestError as exc:
            log_entry["response"] = {"error": f"Network error: {exc}"}
            logs.append(log_entry)
            results.append({
                "name": test_name, "status": "FAIL", "details": str(exc),
                "explanation": "Could not connect to the target URL. Please verify the URL and that the server is running."
            })
            return None

    # ... (The rest of the file follows the same pattern, no other changes needed) ...

    # Test Case 1.1: Missing Credentials
    test_name = "Missing Credentials"
    response = await run_test(test_name, "POST", url=api_url, json=valid_payload, headers={})
    if response is not None:
        results.append({
            "name": test_name, "status": "PASS" if response.status_code == 401 else "FAIL",
            "details": f"Expected 401, got {response.status_code}",
            "explanation": "An agent must reject any request that lacks an 'Authorization' header."
        })

    # Test Case 1.2: Malformed Authorization Header
    test_name = "Malformed Authorization Header"
    if token_provided:
        response = await run_test(test_name, "POST", url=api_url, json=valid_payload, headers={"Authorization": f"Token {bearer_token}"})
        if response is not None:
            results.append({
                "name": test_name, "status": "PASS" if response.status_code in [400, 401] else "FAIL",
                "details": f"Expected 400 or 401, got {response.status_code}",
                "explanation": "The A2A protocol strictly requires the 'Bearer <token>' format."
            })
    else:
        logs.append({"test": test_name, "request": {"note": "Request skipped, no token provided."}})
        results.append({
            "name": test_name, "status": "SKIPPED",
            "details": "Test skipped because no Bearer Token was provided.",
            "explanation": "This test was skipped because no token was provided."
        })

    # Test Case 1.3: Invalid Credentials
    test_name = "Invalid Credentials"
    response = await run_test(test_name, "POST", url=api_url, json=valid_payload, headers={"Authorization": "Bearer invalid-token-string"})
    if response is not None:
        results.append({
            "name": test_name, "status": "PASS" if response.status_code in [401, 403] else "FAIL",
            "details": f"Expected 401 or 403, got {response.status_code}",
            "explanation": "The agent must validate the token and reject invalid ones."
        })

    # Test Case 2.1: Malformed JSON Syntax
    test_name = "Malformed JSON Syntax"
    response = await run_test(test_name, "POST", url=api_url, content='{"message_id": "123",,}', headers=auth_headers)
    if response is not None:
        results.append({
            "name": test_name, "status": "PASS" if response.status_code == 400 else "FAIL",
            "details": f"Expected 400, got {response.status_code}",
            "explanation": "An agent must robustly handle syntactically invalid JSON."
        })

    # Test Case 2.2: Missing Required Fields
    test_name = "Missing Required Fields"
    response = await run_test(test_name, "POST", url=api_url, json={"message": "test"}, headers=auth_headers)
    if response is not None:
        results.append({
            "name": test_name, "status": "PASS" if response.status_code in [400, 422] else "FAIL",
            "details": f"Expected 400 or 422, got {response.status_code}",
            "explanation": "The agent must reject semantically incorrect JSON that is missing required fields."
        })

    # Test Case 2.3: Incorrect Data Types
    test_name = "Incorrect Data Types"
    response = await run_test(test_name, "POST", url=api_url, json={"message_id": 123}, headers=auth_headers)
    if response is not None:
        results.append({
            "name": test_name, "status": "PASS" if response.status_code in [400, 422] else "FAIL",
            "details": f"Expected 400 or 422, got {response.status_code}",
            "explanation": "Schema validation includes enforcing correct data types."
        })

    # Test Case 2.4: Response Schema Validation
    test_name = "Response Schema Validation"
    response = await run_test(test_name, "POST", url=api_url, json=valid_payload, headers=auth_headers)
    if response is not None:
        if response.status_code in [200, 202]:
            try:
                if "status" in response.json():
                     results.append({"name": test_name, "status": "PASS", "details": "Response conforms to schema.", "explanation": "A compliant agent must produce valid, well-structured responses."})
                else:
                     results.append({"name": test_name, "status": "FAIL", "details": "Response missing required fields.", "explanation": "Agent response was missing required fields from the schema."})
            except Exception:
                results.append({"name": test_name, "status": "FAIL", "details": "Failed to parse response JSON.", "explanation": "The agent's response was not valid JSON."})
        else:
            results.append({"name": test_name, "status": "FAIL", "details": f"Expected 200 or 202, got {response.status_code}", "explanation": "The agent failed to process a fully valid request."})

    # Test Case 3.1: Method Not Allowed
    test_name = "Method Not Allowed"
    response = await run_test(test_name, "GET", url=api_url, headers=auth_headers)
    if response is not None:
        results.append({
            "name": test_name, "status": "PASS" if response.status_code == 405 else "FAIL",
            "details": f"Expected 405, got {response.status_code}",
            "explanation": "A2A endpoints should explicitly disallow non-POST HTTP methods."
        })

    return results, logs