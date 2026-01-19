from __future__ import annotations

import argparse
import sys
from pathlib import Path

import uvicorn

from engine.validate import ValidationFinding, validate_ssp_file
from web.app import app


def run() -> None:
    parser = argparse.ArgumentParser(description="Open OSCAL Wizard")
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser("serve", help="Run the web server")
    serve_parser.add_argument("--host", default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8000)

    validate_parser = subparsers.add_parser("validate", help="Validate SSP JSON")
    validate_parser.add_argument("--file", required=True)

    args = parser.parse_args()
    command = args.command or "serve"

    if command == "serve":
        host = getattr(args, "host", "0.0.0.0")
        port = getattr(args, "port", 8000)
        uvicorn.run(app, host=host, port=port)
        return

    if command == "validate":
        findings = validate_ssp_file(Path(args.file))
        _print_findings(findings)
        sys.exit(1 if findings else 0)

    raise SystemExit(f"Unknown command: {command}")


def _print_findings(findings: list[ValidationFinding]) -> None:
    if not findings:
        print("OK: no validation findings.")
        return

    print("Validation findings:")
    for finding in findings:
        print(f"- [{finding.severity}] {finding.location}: {finding.message}")


if __name__ == "__main__":
    run()
