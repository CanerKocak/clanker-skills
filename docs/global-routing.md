# Global skill routing

Add the following section to your harness's global instructions after installing
the package. It routes work by contract and avoids invoking adjacent skills without
a reason.

| Harness | Where to put it |
| --- | --- |
| Codex | Append to `~/.codex/AGENTS.md` |
| Claude Code | Append to `~/.claude/CLAUDE.md` |
| OpenCode | Add the file to the `instructions` array in `~/.config/opencode/opencode.json` |
| Pi / Grok Build | Append to the harness's global instructions file |

Skill references below use the `$name` form as the skill ID; invoke each skill
with your harness's native syntax (for example, the `skill` tool by exact ID
in OpenCode).

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
READMEs, durable instructions, and commit text. Use `$git-hygiene` for commits,
branches, and history rewrites, and `$issue-and-pr` for human-readable issues,
pull requests, and reviews. Write all durable prose with `$simple-english`:
short sentences, common words, redundancy checked. Do not invoke adjacent skills
ceremonially.
```
