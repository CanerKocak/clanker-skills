---
name: pdf-typst-report
description: >
  Generate high-quality multi-page PDF reports with Typst when the typst CLI is
  available. Prefer for security booklets and long technical reports that need
  clean headers, footers, and stable page setup. Fall back to reportlab (pdf
  skill) if typst is missing. Always run pdf-visual-qa after compile.
---

# Typst report path

Typst is faster and cleaner than LaTeX for agent-built reports. Use when
installed; do not require it as a hard dependency of the whole fleet.

## Check

```bash
command -v typst && typst --version
# install if user wants: brew install typst
```

## Page setup (from Typst docs)

```typst
#set page(
  paper: "a4",
  margin: (top: 2.2cm, bottom: 2cm, x: 1.8cm),
  header: context [
    #smallcaps[CK Web3 Solutions]
    #h(1fr)
    #text(size: 8pt)[CONFIDENTIAL]
  ],
  footer: context [
    #text(size: 8pt)[Client Confidential]
    #h(1fr)
    #counter(page).display("1")
  ],
  numbering: "1",
)

#set text(font: "New Computer Modern", size: 10pt)
#set par(justify: true, leading: 0.65em)
```

Skip header on cover:

```typst
#set page(header: context {
  if counter(page).get().first() > 1 [ …header… ]
})
```

## Workflow

1. Write `audit-out/<id>/report.typ` (or generate from frozen JSON via a small script).  
2. `typst compile report.typ output/pdf/report.pdf`  
3. Run `pdf-visual-qa`.  
4. Do not invent findings in Typst markup — inject from frozen JSON only.

## When not to use

- `typst` missing and user did not ask to install it → ReportLab via `pdf` + `pdf-security-audit-report`.  
- One-page receipt / simple dump → plain ReportLab canvas is enough.

## Template stub

See `templates/security-audit.typ` in this skill folder.
