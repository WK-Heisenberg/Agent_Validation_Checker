def get_ui(api_url: str = "", bearer_token: str = ""):
    """
    Returns a dictionary representing the UI components, including the CORRECT
    default endpoint URL and a tooltip for it.
    """
    return {
        "title": "A2A Validation Agent",
        "input_fields": [
            {
                "name": "api_url",
                "label": "A2A API Endpoint URL",
                "type": "text",
                # --- START OF CORRECTION ---
                # Add the correct "/invoke" path to the end of the default URL.
                "value": api_url or "https://my-fastapi-bq-agent-api-gateway-c0lnz9zq.uc.gateway.dev/invoke",
                # --- END OF CORRECTION ---
                "required": True,
                "tooltip": "This is an open API endpoint to an LLM hosted on Cloud Run - do not abuse!"
            },
            {
                "name": "bearer_token",
                "label": "Bearer Token (Optional)",
                "type": "text",
                "value": bearer_token,
                "required": False,
                "tooltip": None
            },
        ],
        "button": {"text": "Run Validation"},
    }