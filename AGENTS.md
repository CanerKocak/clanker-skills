# Clanker output contract

## Default to tables

Use a Markdown table whenever a response contains two or more items that share
meaningful attributes. If prose and a table would be equally clear, choose the
table.

A table is required for comparisons, inventories, mappings, findings, risks,
ownership, scope, status, before-and-after summaries, inputs and outputs,
verification results, requirements, decisions, and acceptance criteria when
there are at least two comparable entries.

Make each row one comparable entity. Use specific column headings, keep
evidence and limitations with the row they apply to, and compute reported
counts from the displayed rows.

Lead with a brief conclusion when context is needed, then put the structured
evidence in the table. Do not create decorative or one-column tables.

## Keep tables narrow

A table must fit a terminal that is 80 to 120 columns wide. A wider table
wraps into a column of fragments that the reader cannot scan.

- Use 2 to 4 columns.
- Keep each cell to about 8 words or fewer. Do not put full sentences in
  cells.
- Make the first column the row label. It names the thing that the row is
  about.
- Put a long reason on one short line under the table. Start the line with
  the row label, for example: `parser.py: the cache key omits the locale.`
- If a table is still too wide, split it into two tables that share the row
  label, or use a numbered list.

## Use other forms where they fit

- Write ordered steps as a numbered list, not a table.
- Put commands and code in code blocks.
- Use prose for a single fact or a causal explanation.
