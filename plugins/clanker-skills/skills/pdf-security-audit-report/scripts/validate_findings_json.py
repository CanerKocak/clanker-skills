#!/usr/bin/env python3
"""Validate findings.frozen.json before PDF render. Exit 1 on failure."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SEVERITIES = {"critical", "high", "medium", "low", "informational"}
LABELS = {"verified", "partial", "open", "ruled_out"}


def main(path: str) -> int:
    data = json.loads(Path(path).read_text())
    errors: list[str] = []
    if "meta" not in data:
        errors.append("missing meta")
    findings = data.get("findings")
    if not isinstance(findings, list):
        errors.append("findings must be a list")
        findings = []
    for i, f in enumerate(findings):
        for key in ("id", "severity", "title", "description", "remediation"):
            if key not in f:
                errors.append(f"findings[{i}] missing {key}")
        sev = str(f.get("severity", "")).lower()
        if sev and sev not in SEVERITIES:
            errors.append(f"findings[{i}] bad severity {sev}")
        label = str(f.get("evidence_label") or f.get("status") or "").lower()
        if label and label not in LABELS:
            errors.append(f"findings[{i}] bad evidence_label {label}")
    counts = data.get("counts") or {}
    if findings and counts:
        bucket: dict[str, int] = {s: 0 for s in SEVERITIES}
        for f in findings:
            s = str(f.get("severity", "")).lower()
            if s in bucket:
                bucket[s] += 1
        for s, n in bucket.items():
            if int(counts.get(s, n)) != n:
                errors.append(f"counts.{s}={counts.get(s)} != actual {n}")
    if errors:
        print("INVALID:", *errors, sep="\n- ")
        return 1
    print(f"OK: {len(findings)} findings in {path}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: validate_findings_json.py findings.frozen.json", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
