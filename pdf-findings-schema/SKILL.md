---
name: pdf-findings-schema
description: >
  Canonical JSON schema for security findings used as the single source of
  truth before any audit PDF is rendered. Use when freezing review results,
  merging specialist output, or feeding pdf-security-audit-report.
---

# Findings schema (freeze before PDF)

The PDF is a **compiler**. It must not invent claims.

## File

`audit-out/<engagement-id>/findings.frozen.json`

## Minimal document shape

```json
{
  "meta": {
    "engagement_id": "EXAMPLE-2026-001",
    "title": "Application Security Assessment",
    "client": "Example Protocol",
    "firm": "Independent Security Review",
    "date": "2026-08-09",
    "git_commit": "32779fc…",
    "git_branch": "staging",
    "classification": "Example",
    "scope_summary": "Authentication and administrative API boundaries"
  },
  "counts": { "critical": 0, "high": 1, "medium": 6, "low": 4, "informational": 1 },
  "overall": "One sentence honest assessment.",
  "priorities": [
    { "window": "0-7 days", "actions": "…" }
  ],
  "ruled_out": [
    {
      "hypothesis": "One quote funds multiple withdrawals",
      "control": "quote row lock + single consumption"
    }
  ],
  "findings": []
}
```

## Finding object

```json
{
  "id": "EX-001",
  "severity": "high",
  "title": "Scoped API key reaches an administrative route outside its grant",
  "status": "verified",
  "affected_surface": "API-key auth + /api/v1/admin/*",
  "required_capability": "Possession of an API key owned by an administrator",
  "security_property": "Scopes must constrain all authority granted to the key",
  "description": "…",
  "impact_scenario": ["step 1", "step 2"],
  "evidence": [
    "src/auth.ts:120-164",
    "Local: records:read key → GET /api/v1/admin/settings → 200"
  ],
  "counterevidence": "Not anonymous escalation; requires an administrator-owned key.",
  "remediation": "Enforce the key's granted scopes at the admin boundary; …",
  "evidence_label": "verified"
}
```

### Enums

- `severity`: `critical` | `high` | `medium` | `low` | `informational`
- `status` / `evidence_label`: `verified` | `partial` | `open` | `ruled_out`

## Rules

1. Sort findings Critical → Informational, stable `id` order within band.  
2. Every High/Medium needs evidence path or local proof string.  
3. Do not raise severity in the PDF layer.  
4. Ruled-out high-risk hypotheses stay in `ruled_out`, not as findings.  
5. Human or coordinator says **FREEZE** before render.
