# pytest_custom.py

def pytest_report_teststatus(report):
    if report.when == "call":
        return report.outcome, "*", f"{report.nodeid} {report.outcome}"


def pytest_terminal_summary(terminalreporter):
    terminalreporter.write_sep("-", "Test Results")
    for report in terminalreporter.stats.get("passed", []):
        terminalreporter.write_line(f"{report.nodeid} PASSED")
    for report in terminalreporter.stats.get("failed", []):
        terminalreporter.write_line(f"{report.nodeid} FAILED")
    for report in terminalreporter.stats.get("skipped", []):
        terminalreporter.write_line(f"{report.nodeid} SKIPPED")
