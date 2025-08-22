## A2A Validation Agent

An agentic system built with the Google Agent Development Kit (ADK) to validate Agent-to-Agent (A2A) communication implementations against protocol standards and common security vulnerabilities.

### Key Features

*   **A2A Protocol Validation:** In-depth checks for authentication, message formatting, and HTTP method compliance.
*   **OWASP Security Checks:** Basic validation against common LLM vulnerabilities like prompt injection and insecure output handling.
*   **ADK-Powered:** Built on the robust and scalable Google Agent Development Kit.
*   **Simple UI:** Easy-to-use web interface for initiating validation tests.
*   **Clear Results:** Structured and clear output of validation results.

### Installation Guide

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/a2a-validation-agent.git
    cd a2a-validation-agent
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

### Usage Instructions

1.  **Run the agent:**
    ```bash
    python src/agent.py
    ```

2.  **Access the UI:**
    Open your web browser and navigate to `http://127.0.0.1:8000`.

3.  **Run a validation test:**
    *   Enter the URL of the A2A-compliant API endpoint you want to test.
    *   (Optional) Provide a valid Bearer Token for authenticated tests.
    *   Click "Run Validation".
    *   The validation results will be displayed in the output area.

### Technical Stack

*   **Framework:** Google Agent Development Kit (ADK)
*   **Web Framework:** FastAPI
*   **HTTP Client:** httpx
*   **Schema Validation:** Pydantic

---

### Directory Structure

```/a2a-validation-agent
|
|-- src/
|   |-- agent.py          # Main agent logic and ADK integration
|   |-- ui.py             # ADK UI component definitions
|   |-- validation/
|   |   |-- __init__.py
|   |   |-- a2a_checks.py   # Functions for A2A protocol validation suites
|   |   |-- owasp_checks.py # Functions for OWASP security checks
|   |   |-- schemas.py      # Pydantic models or dicts for A2A schemas
|
|-- tests/
|   |-- test_validation.py  # Unit tests for the validation logic
|
|-- requirements.txt      # Project dependencies
|-- README.md             # Project documentation