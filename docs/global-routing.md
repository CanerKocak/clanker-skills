# Global skill routing

After installing the Codex plugin, add the section below to
`~/.codex/AGENTS.md`. Keep repository-specific instructions in that
repository's `AGENTS.md`.

```markdown
## Clanker skill routing

Select the smallest installed workflow that matches the task. Read its
`SKILL.md` before acting and load references only when they affect the next
decision. Scale planning and review to the change. Skills and feature flags
do not authorize delegation or external actions; follow the active instructions.

Use `$writing-plans` for a multi-step specification before implementation.
Use `$adaptive-code-orchestrator` when uncertain or cross-cutting work needs
an execution strategy. For non-trivial code changes, `$edit-the-chain` owns
the change workflow, `$semantic-blast-radius` maps its impact,
`$ast-grep-callchain-audit` supplies structural evidence, and
`$call-chain-invariants` identifies surfaces that share the contract.
Use `$differential-review` for security-focused diffs. Apply
`$yagni-anti-ceremonial` to proposed guards and fallbacks. Complete source
changes with both passes of `$thermo-nuclear-code-quality-review`.

Use `$codebase-search` for a focused read-only source investigation when
delegation is permitted. Handle simple known-file lookups directly and check
decisive citations against the requested checkout.

Use `$gather-business-context` when missing business context prevents analysis,
then use `$analyze-data-quality` to assess the data and equations. Apply
`$uncodixfy` to frontend UI work. Use `$git-hygiene` for commits, branches,
and history changes, and `$issue-and-pr` for issue and pull request prose.

Before editing or publishing durable prose, apply `$prompt-leakage` and its
deletion test. Use `$simple-english` for technical prose with aircraft-manual
clarity. Preserve facts, uncertainty, and the difference between requirements
and recommendations. Do not apply this style to marketing or brand copy
unless requested. Keep internal review notes out of the artifact.

Use tables for comparable findings, inventories, and mappings. Use prose for
causal explanations and ordered steps for procedures. Preserve the evidence
and its limits in the form that best helps the reader.

When runtime history or notes tools are available, use them to preserve the
task outcome, constraints, authorized actions, rejected ideas, and unresolved
questions. Check retrieved conclusions against current evidence. Distinguish
configured features, exposed tools, and successful execution. Continue with
the available context when runtime tools are unavailable.
```
