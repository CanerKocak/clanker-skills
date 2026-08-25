---
name: pdf-visual-qa
description: >
  Mandatory visual quality gate for any agent-generated PDF before delivery.
  Render pages with pdftoppm, inspect PNGs, fix layout defects, re-render.
  Use after reportlab/typst/weasyprint builds or when the user says the PDF
  looks wrong, clipped, dense, or unprofessional.
---

# PDF Visual QA (the part that cooks)

Text extraction can pass while the PDF looks broken. **Layout truth is pixels.**

## When

- After every meaningful PDF build or redesign.
- Before telling the user a PDF is done.
- When TOC, tables, or finding cards might overflow.

## Pipeline

```bash
mkdir -p tmp/pdfs/qa
pdftoppm -png -r 150 "$PDF" tmp/pdfs/qa/page
pdfinfo "$PDF"
pdftotext -layout "$PDF" tmp/pdfs/qa/full.txt
# Inspect PNGs with the image/read tool (or open them).
```

Contact sheet (optional, ImageMagick if present):

```bash
# montage tmp/pdfs/qa/page-*.png -geometry 200x280+4+4 tmp/pdfs/qa/contact.png
```

## Fail the build if any of these appear

| Defect | What you see |
|--------|----------------|
| Clipped text | Letters cut at box/edge |
| Overflow | Text past margin or into footer |
| Overlap | Lines through other lines, badges on text |
| Sparse TOC | Dot leaders eating a whole page for no reason |
| Table blowout | Columns smashed or page-wide empty columns |
| Black boxes | Missing glyphs / bad unicode |
| Low contrast | Gray on gray, unreadable severity chips |
| Orphan header | Heading alone at page bottom |
| Uneven gaps | Huge empty regions then cramped blocks |
| Footer collision | Body text through page number |

## Required sample set

Inspect at least:

1. Cover / title page  
2. Executive summary or densest table  
3. One full finding page (if audit)  
4. Last page  

For ≤30 pages, prefer **all pages** when time allows.

## Fix loop

1. Note page + defect.  
2. Change generator (margins, font size, table col widths, keepWithNext, page breaks).  
3. Rebuild PDF.  
4. Re-render **changed pages**.  
5. Stop only when sample set is clean.

## Report back

When done, state:

- PDF path  
- page count  
- SHA-256  
- pages visually inspected  
- defects found and fixed (or “none”)  

## Tools

```bash
brew install poppler   # pdftoppm, pdfinfo, pdftotext
```
