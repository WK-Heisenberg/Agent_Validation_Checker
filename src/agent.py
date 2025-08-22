# /a2a-validation-agent/src/agent.py

from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import json

from .ui import get_ui
from .validation.a2a_checks import run_a2a_checks
from .validation.owasp_checks import run_owasp_checks
# Revert to the Markdown report generator function
from .report_generator import generate_markdown_report

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")

# In-memory storage for the last run results
last_run_results = {}


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request, "ui": get_ui()})


@app.post("/run-validation", response_class=HTMLResponse)
async def run_validation(
    request: Request,
    api_url: str = Form(...),
    bearer_token: str = Form(None),
):
    """
    Receives form submission, runs tests, and returns results.
    """
    global last_run_results

    clean_api_url = api_url.strip()
    clean_bearer_token = bearer_token.strip() if bearer_token else None

    a2a_results, a2a_logs = await run_a2a_checks(clean_api_url, clean_bearer_token)
    owasp_results, owasp_logs = await run_owasp_checks(clean_api_url, clean_bearer_token)
    
    all_logs = a2a_logs + owasp_logs

    # Store results for download
    last_run_results = {
        "api_url": clean_api_url,
        "a2a_results": a2a_results,
        "owasp_results": owasp_results,
    }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "ui": get_ui(api_url=api_url, bearer_token=bearer_token),
            "a2a_results": a2a_results,
            "owasp_results": owasp_results,
            "request_logs_json": json.dumps(all_logs)
        },
    )


@app.get("/download-report")
async def download_report():
    """
    Generates a Markdown report and returns it as a downloadable .md file.
    """
    if not last_run_results:
        return HTMLResponse("No results to download. Please run a validation first.", status_code=404)

    # Generate the report content using the Markdown function
    report_content = generate_markdown_report(**last_run_results)

    # Create a dynamic filename
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"A2A_Validation_Report_{timestamp}.md"

    # Return as a file download
    return Response(
        content=report_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )