#!/usr/bin/env python3
"""
Security assessment automation.

Runs four security checks where the relevant tools are installed:
- SAST: Semgrep
- Dependency audit: pip-audit
- Secrets: Gitleaks
- IaC: Checkov

The script intentionally treats missing tools as an explicit finding rather
than silently pretending that a scan succeeded.
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


TOOLS = {
    "sast": ("semgrep", ["semgrep", "scan", "--json", "--quiet"]),
    "dependency": ("pip-audit", ["pip-audit", "--format", "json"]),
    "secrets": ("gitleaks", ["gitleaks", "detect", "--source", ".", "--report-format", "json", "--report-path", "gitleaks-report.json"]),
    "iac": ("checkov", ["checkov", "-d", ".", "-o", "json"]),
}


def run_command(command, cwd):
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=300,
    )
    return {
        "return_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def parse_json(text):
    try:
        return json.loads(text) if text.strip() else None
    except json.JSONDecodeError:
        return None


def scan_target(target: Path):
    results = {}
    temp_report = target / "gitleaks-report.json"

    for category, (tool, command) in TOOLS.items():
        if shutil.which(tool) is None:
            results[category] = {
                "tool": tool,
                "status": "NOT_INSTALLED",
                "passed": False,
                "message": f"{tool} is not installed or not available in PATH.",
            }
            continue

        try:
            result = run_command(command, target)
            parsed = parse_json(result["stdout"])

            # Security scanners commonly return non-zero when findings exist.
            # We therefore record the tool exit code separately and derive
            # pass/fail from whether the scanner reported findings.
            if category == "secrets" and temp_report.exists():
                parsed = parse_json(temp_report.read_text(encoding="utf-8"))
                temp_report.unlink(missing_ok=True)

            results[category] = {
                "tool": tool,
                "status": "COMPLETED",
                "return_code": result["return_code"],
                "passed": result["return_code"] == 0,
                "findings": parsed,
                "stderr": result["stderr"][-4000:],
            }
        except subprocess.TimeoutExpired:
            results[category] = {
                "tool": tool,
                "status": "TIMEOUT",
                "passed": False,
                "message": "Scanner exceeded the 300 second timeout.",
            }
        except Exception as exc:
            results[category] = {
                "tool": tool,
                "status": "ERROR",
                "passed": False,
                "message": str(exc),
            }

    overall_pass = all(item["passed"] for item in results.values())

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "target": str(target),
        "overall_status": "PASS" if overall_pass else "FAIL",
        "checks": results,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run SAST, dependency, secrets and IaC security checks."
    )
    parser.add_argument("--path", default=".", help="Path to application/source directory")
    parser.add_argument(
        "--format",
        choices=["json", "pretty"],
        default="pretty",
        help="Output format",
    )
    args = parser.parse_args()

    target = Path(args.path).resolve()
    if not target.exists() or not target.is_dir():
        print(f"ERROR: target directory does not exist: {target}", file=sys.stderr)
        return 2

    report = scan_target(target)

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(json.dumps(report, indent=2))

    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
