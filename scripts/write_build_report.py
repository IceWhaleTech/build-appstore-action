#!/usr/bin/env python3
"""Write a structured build-v2 report JSON file."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write AppStore build-v2 report")
    parser.add_argument("--report-json", required=True)
    parser.add_argument("--report-title", default="Build V2 Store Report")
    parser.add_argument("--source", default=".")
    parser.add_argument("--output", default="dist")
    parser.add_argument("--base-url", default="")
    parser.add_argument("--build-outcome", default="unknown")
    return parser.parse_args()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def detect_status(build_outcome: str) -> str:
    if build_outcome == "success":
        return "success"
    if build_outcome in {"failure", "cancelled", "timed_out"}:
        return "failed"
    return "unknown"


def main() -> int:
    args = parse_args()
    report_path = Path(args.report_json)
    output_dir = Path(args.output)
    status = detect_status(args.build_outcome)
    dist_exists = output_dir.exists()

    issues = []
    if status != "success":
        issues.append(
            {
                "severity": "error",
                "code": "BUILD_V2_FAILED",
                "file": "",
                "message": "The AppStore build action failed.",
                "suggestion": (
                    "Check the workflow log for the failing build step, then fix the "
                    "reported app metadata, compose file, or registry resolution error."
                ),
            }
        )

    artifacts = [
        {
            "name": "build-v2-report.json",
            "path": report_path.as_posix(),
            "note": "Upload this file as a workflow artifact for debugging and HTML rendering.",
        }
    ]
    if dist_exists:
        artifacts.append(
            {
                "name": "dist",
                "path": output_dir.as_posix(),
                "note": "Upload the generated v2 store output as a workflow artifact.",
            }
        )

    report = {
        "title": args.report_title,
        "kind": "build-v2",
        "status": status,
        "started_at": now_iso(),
        "finished_at": now_iso(),
        "summary": {
            "build_outcome": args.build_outcome,
            "dist_exists": dist_exists,
            "issues_total": len(issues),
        },
        "context": {
            "repo": os.getenv("GITHUB_REPOSITORY", ""),
            "ref": os.getenv("GITHUB_REF", ""),
            "sha": os.getenv("GITHUB_SHA", ""),
            "trigger": os.getenv("GITHUB_EVENT_NAME", ""),
            "source": args.source,
            "output": args.output,
            "base_url": args.base_url,
        },
        "issues": issues,
        "artifacts": artifacts,
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Build report written to {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
