---
name: issue-and-pr
description: >
  Write issues and pull requests as plain-words engineering tasks with tables
  for comparable evidence. Use when creating or rewriting an issue or pull
  request, when a draft reads like a filled-in form, or when a report needs
  its structure rethought.
---

# Issues and pull requests

An issue asks for one change. A pull request delivers one change. Write each
so a stranger can act on it without asking for context. A second idea gets
its own issue; an unrelated fix gets its own pull request.

## Tables

Use a Markdown table whenever two or more items share meaningful attributes.
If prose and a table would be equally clear, choose the table. One row per
item, specific column headings, and counts computed from the displayed rows.
Keep limitations with the row they apply to.

Keep each table narrow enough for an 80-120 column terminal. Use 2 to 4
columns and cells of about 8 words, with no full sentences. The first column
names the item. Put a long reason on one line under the table, keyed by the
row label. Split a wider table into two tables, or use a numbered list.

Use prose for a single fact, a causal explanation, or code. Use an ordered
list when the order is the point. Never make a one-column or decorative
table.

## Issues

1. Open with what was observed: the behavior, where it happens, and the
   conditions. Use file paths, commands, and measured numbers with their
   machine and date.
2. Put two or more comparable observations in a table: measurements,
   affected areas, before and after, or findings with severity.
3. Say what should change and how to recognize it working. For several
   tasks, use a checklist or a table with an owner or status column.

If the reader would need a chat history to understand the request, pull the
needed facts into the text.

## Pull requests

1. Open with what changed and why, in two to four plain sentences.
2. Follow with a verification table: each command or check, and what it
   showed. This table is the default for any pull request with more than
   one check, including passing ones.
3. Add a second table when it helps review: files or areas to read first,
   edge cases checked, or before and after behavior.

Skip what the diff already shows, such as file lists without a reason,
restated commit messages, and process notes about how the work was done.

## Structure

Do not pour every report into fixed sections such as Summary, Problem,
Solution, Testing, or Non-goals. A heading earns its place only when it
names the thought below it. Put the point in the first sentence; readers
scan before they read. Keep paragraphs to four lines or fewer.

## Evidence

Point at things a stranger can open: paths, commands, logs with their
conditions. Never link a private conversation or paste a transcript as
context. Mark guesses as guesses. Run $prompt-leakage on the final draft,
and use $simple-english for the wording. Commit messages, branches, and
history rewrites belong to $git-hygiene.
