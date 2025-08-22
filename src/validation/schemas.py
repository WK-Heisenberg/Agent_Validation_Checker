### /a2a-validation-agent/src/validation/schemas.py

A2A_MESSAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "message_id": {"type": "string"},
        "sender_id": {"type": "string"},
        "timestamp": {"type": "integer"},
        "message": {"type": "string"},
    },
    "required": ["message_id", "sender_id", "timestamp", "message"],
}