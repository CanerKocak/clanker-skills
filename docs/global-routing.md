# Global Codex routing

Add the following section to `~/.codex/AGENTS.md` after installing the plugin.
It routes work by contract and avoids invoking adjacent skills without a reason.

```markdown
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
framing, run `$gather-business-context` before `$analyze-data-quality`. Build
security reports from frozen `$pdf-findings-schema` data with
`$pdf-security-audit-report`, use `$pdf-typst-report` when Typst is the selected
engine, and always finish generated PDFs with `$pdf-visual-qa`. Apply
`$uncodixfy` to frontend UI work and `$prompt-leakage` to comments, READMEs,
durable instructions, and commit text. Do not invoke adjacent skills
ceremonially.
```
