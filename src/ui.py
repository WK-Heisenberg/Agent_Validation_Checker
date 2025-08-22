def get_ui(api_url: str = "", bearer_token: str = ""):
    """
    Returns a dictionary representing the UI components, with helpful tooltips
    and no default URL.
    """
    return {
        "title": "A2A Validation Agent",
        "input_fields": [
            {
                "name": "api_url",
                "label": "A2A API Endpoint URL",
                "type": "text",
                # --- START OF MODIFICATION ---
                # Remove the default URL to encourage user input.
                "value": api_url or "",
                "required": True,
                # Add a more descriptive tooltip explaining the endpoint.
                "tooltip": "The full URL of the agent's endpoint that accepts POST requests. This typically looks like 'https://your-agent-url.com/invoke'."
                # --- END OF MODIFICATION ---
            },
            {
                "name": "bearer_token",
                "label": "Bearer Token (Optional)",
                "type": "text",
                "value": bearer_token,
                "required": False,
                # --- START OF MODIFICATION ---
                # Add a helpful tooltip explaining what a Bearer Token is.
                "tooltip": "An API security token. If required, it is sent in the 'Authorization' header, prefixed with 'Bearer '. Example: 'Bearer sk-Abc123...'"
                # --- END OF MODIFICATION ---
            },
        ],
        "button": {"text": "Run Validation"},
    }