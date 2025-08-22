# /a2a-validation-agent/src/report_generator.py

from datetime import datetime
import json

def generate_markdown_report(
    a2a_results: list[dict], 
    owasp_results: list[dict], 
    api_url: str
) -> str:
    """
    Generates a formatted Markdown report from validation results.
    """
    report_lines = []
    
    # --- Report Header ---
    report_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    report_lines.append("# A2A Validation & Security Report")
    report_lines.append("---")
    report_lines.append(f"**Target URL:** `{api_url}`")
    report_lines.append(f"**Report Generated:** {report_date}")
    report_lines.append("\n")

    # --- Summary ---
    all_results = a2a_results + owasp_results
    total_tests = len(all_results)
    pass_count = sum(1 for r in all_results if r['status'] == 'PASS')
    fail_count = sum(1 for r in all_results if r['status'] == 'FAIL')
    skipped_count = sum(1 for r in all_results if r['status'] == 'SKIPPED')

    report_lines.append("## Executive Summary")
    report_lines.append(f"- **Total Tests Executed:** {total_tests}")
    # Using Markdown-safe formatting for colors is tricky, plain text is more reliable.
    report_lines.append(f"- **Passed:** {pass_count}")
    report_lines.append(f"- **Failed:** {fail_count}")
    report_lines.append(f"- **Skipped:** {skipped_count}")
    report_lines.append("\n")

    # --- Helper Function for Formatting ---
    def format_results(title: str, results: list[dict]):
        report_lines.append(f"## {title}")
        report_lines.append("---")
        if not results:
            report_lines.append("_No tests were run for this section._")
            report_lines.append("\n")
            return

        for result in results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⚪️"
            report_lines.append(f"### {status_icon} {result['name']} - `{result['status']}`")
            report_lines.append(f"**Details:** {result['details']}")
            report_lines.append(f"**Explanation:** {result['explanation']}")
            report_lines.append("\n")

    # --- Format Sections ---
    format_results("A2A Protocol Validation", a2a_results)
    format_results("OWASP LLM Top 10 Security Checks", owasp_results)

    return "\n".join(report_lines)