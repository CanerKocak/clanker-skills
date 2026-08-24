---
name: pdf-security-audit-report
description: >
  Build a professional multi-page security assessment PDF from frozen findings
  JSON (not from freeform invention). Structure follows Spearbit/OWASP/ToB-style
  sections: letter, exec summary, scope, methodology, findings cards, ruled-out,
  retest plan. Use after a code review when the user wants an audit-style PDF.
  Always run pdf-visual-qa before delivery. Does not invent vulnerabilities.
---

# Security audit PDF (findings → booklet)

## Hard rules

1. **Source of truth** = `findings.frozen.json` (see `pdf-findings-schema`).  
2. **Do not invent** findings, severities, or evidence while rendering.  
3. **Freeze first**, then render.  
4. After render, run **`pdf-visual-qa`**.  
5. If the user wants bug hunting, not a PDF — stop and do not open this skill.

## Document spine (what good reports share)

Distilled from OWASP WSTG reporting, Spearbit markdown templates, and public
Trail of Bits assessment layouts:

1. Cover (engagement, date, commit, classification)  
2. Letter / introduction (honest center of gravity)  
3. Contents  
4. Executive summary (counts + priorities, not novel claims)  
5. Scope and limitations  
6. Methodology / evidence standard  
7. Architecture / trust boundaries (short)  
8. Findings overview table  
9. Finding cards (one finding per section; Critical/High first)  
10. Testing / runtime corroboration  
11. Ruled-out high-risk hypotheses  
12. Remediation verification plan  
13. Severity model  

## Finding card fields (every finding)

| Field | Content |
|-------|---------|
| ID + severity chip | Stable ID |
| Title | One line, specific |
| Status | verified / partial |
| Affected surface | |
| Required capability | Precondition honesty |
| Security property | Invariant broken |
| Description | What the code does |
| Impact + scenario | Numbered steps |
| Evidence | file:line + runtime proof |
| Counterevidence / limits | Kills hype |
| Remediation | Concrete |

## Severity honesty (Spearbit-shaped)

Use impact × likelihood; do not label admin footguns as Critical without a cheap
path to that admin power.

| | Impact high | Impact medium | Impact low |
|--|-------------|---------------|------------|
| Likelihood high | Critical | High | Medium |
| Likelihood medium | High | Medium | Low |
| Likelihood low | Medium | Low | Low |

## Generator choice

| Engine | When |
|--------|------|
| **ReportLab Platypus** | Default; always available via pip; matches prior CK Web3 run |
| **Typst** | If `typst` installed and user wants higher typesetting — use `pdf-typst-report` |

Prefer a **Python build script** under `tmp/pdfs/build_*.py` that only reads
JSON + assets. Keep the script disposable or under `audit-out/<id>/`.

## Visual design (enough to cook, not a brand agency)

- Dark cover OK; interior should stay high-contrast for print/PDF readers.  
- Severity colors: Critical red, High dark red, Medium amber, Low blue, Info gray.  
- Mono block for evidence paths.  
- Header: firm + doc id; footer: classification + short commit + page.  
- Avoid multi-page TOC with decorative dot leaders (wastes pages).  

## Delivery checklist

- [ ] `findings.frozen.json` present and counts match PDF banner  
- [ ] Commit hash on cover matches `git rev-parse HEAD` used in review  
- [ ] No staging secrets / API keys in PDF  
- [ ] `pdfinfo` page count sane  
- [ ] SHA-256 printed for user  
- [ ] `pdf-visual-qa` clean on cover + densest pages  

## Output

```
output/pdf/<Firm>_<Short_Title>_Security_Audit.pdf
```

## Companion

- Schema: `pdf-findings-schema`  
- Visual gate: `pdf-visual-qa`  
- Base ops: `pdf`  
