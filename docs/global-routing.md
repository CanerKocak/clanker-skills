# Global Codex routing

Add the following section to `~/.codex/AGENTS.md` after installing the plugin.
It routes work by contract and avoids invoking adjacent skills without a reason.

```markdown
## Table-first output

Use a Markdown table whenever a response contains two or more items that share
meaningful attributes. If prose and a table would be equally clear, choose the
table. Tables are required for comparisons, inventories, mappings, findings,
risks, ownership, scope, status, before-and-after summaries, verification
results, requirements, decisions, and acceptance criteria with at least two
comparable entries. Make each row one entity, use specific headings, keep cells
concise, preserve evidence and limitations in the relevant row, and derive
counts from the displayed rows. Use prose or ordered steps when sequence or
causality is the main point, and do not create decorative or one-column tables.

## Evidence-first skill routing

Select the smallest installed workflow that matches the task and read its
`SKILL.md` before acting. For a multi-step specification, use `$writing-plans`
before implementation. Use `$adaptive-code-orchestrator` for uncertain,
cross-cutting, or high-risk work. For non-trivial code changes,
`$edit-the-chain` owns the change workflow, `$semantic-blast-radius` owns the
impact graph, `$ast-grep-callchain-audit` contributes structural edges, and
`$call-chain-invariants` classifies applicable product surfaces; use
`$differential-review` for security-focused diffs, gate proposed guards and
fallbacks with `$yagni-anti-ceremonial`, and finish source changes with both
passes of `$thermo-nuclear-code-quality-review`. When analysis lacks business
framing, run `$gather-business-context` before `$analyze-data-quality`. Apply
`$uncodixfy` to frontend UI work and `$prompt-leakage` to comments,
READMEs, durable instructions, and commit text. Do not invoke adjacent skills
ceremonially.
```
