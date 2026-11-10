# Global skill routing

The routing block comes in two forms. The skill names are the only
difference.

| Host | Skill name form | Block |
| --- | --- | --- |
| Codex | `$<name>` | [Codex](#codex) |
| DeepSeek Harness | `$<name>` | [Codex](#codex), written by the installer |
| Claude Code | `clanker-skills:<name>` | [Claude Code](#claude-code) |

Keep repository-specific instructions in that repository's `AGENTS.md`.

## Codex

After installing the Codex plugin, add the section below to
`~/.codex/AGENTS.md`, after the output contract from the repository
[`AGENTS.md`](../AGENTS.md). For DeepSeek Harness,
`scripts/install_deepseek_harness.py install` writes the output contract and
this block into `$DSH_HOME/AGENTS.md`.

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

Use `$giga-review` for a requested deep financial-code audit across dimensional
arithmetic, races, unsafe defaults, and unsafe fallbacks. It owns coverage and
coordinates differential review for changed code. Use `$dimensional-analysis`
for a focused audit of units, scales, rounding, and numeric bounds. Neither
workflow authorizes fixes, live probes, or external issue creation.

Use `$codebase-search` for a focused read-only source investigation when
delegation is permitted. Handle simple known-file lookups directly and check
decisive citations against the requested checkout.

Use `$gather-business-context` when missing business context prevents analysis,
then use `$analyze-data-quality` to assess the data and equations. Apply
`$uncodixfy` to frontend UI work. Use `$git-hygiene` for commits, branches,
and history changes, and `$issue-and-pr` for issue and pull request prose.

After pushing commits or starting or rerunning CI, wait at least five minutes
before checking CI status. Wait at least five minutes between later CI status
checks. Do other useful work or yield while waiting.

Before editing or publishing durable prose, apply `$prompt-leakage` and its
deletion test. Use `$simple-english` for technical prose with aircraft-manual
clarity. Preserve facts, uncertainty, and the difference between requirements
and recommendations. Do not apply this style to marketing or brand copy
unless requested. Keep internal review notes out of the artifact.

Use `$i-have-adhd` only when the reader asks for it. It changes the shape of
the reply, not the Clanker output contract: put the result or next action
first, keep comparable items in a table of at most five rows per group, and
end an agentic loop with one closing message that states what changed, what
was verified, and the one next action.

Use tables for comparable findings, inventories, and mappings. Keep them
narrow enough for an 80-120 column terminal: 2-4 columns, cells of about 8
words, the row label first, and long reasons on a short line under the table.
Use prose for causal explanations and numbered lists for procedures. Preserve
the evidence and its limits in the form that best helps the reader.

When runtime history or notes tools are available, use them to preserve the
task outcome, constraints, authorized actions, rejected ideas, and unresolved
questions. Check retrieved conclusions against current evidence. Distinguish
configured features, exposed tools, and successful execution. Continue with
the available context when runtime tools are unavailable.
```

## Claude Code

Claude Code reads global guidance from `~/.claude/CLAUDE.md`. The plugin does
not write that file. Put the output contract from [`AGENTS.md`](../AGENTS.md)
at the top of the file, then the section below. The
[README](../README.md#refresh-global-guidance-in-claude-code) gives the
refresh steps after an update.

```markdown
## Clanker skill routing

Select the smallest installed workflow that matches the task. Invoke it with
the Skill tool before acting, and load references only when they affect the
next decision. Scale planning and review to the change. Skills and feature
flags do not authorize delegation or external actions; follow the active
instructions.

Use `clanker-skills:writing-plans` for a multi-step specification before
implementation. Use `clanker-skills:adaptive-code-orchestrator` when uncertain
or cross-cutting work needs an execution strategy. For non-trivial code
changes, `clanker-skills:edit-the-chain` owns the change workflow,
`clanker-skills:semantic-blast-radius` maps its impact,
`clanker-skills:ast-grep-callchain-audit` supplies structural evidence, and
`clanker-skills:call-chain-invariants` identifies surfaces that share the
contract. Use `clanker-skills:differential-review` for security-focused diffs.
Apply `clanker-skills:yagni-anti-ceremonial` to proposed guards and fallbacks.
Complete source changes with both passes of
`clanker-skills:thermo-nuclear-code-quality-review`.

Use `clanker-skills:giga-review` for a requested deep financial-code audit
across dimensional arithmetic, races, unsafe defaults, and unsafe fallbacks. It
owns coverage and coordinates differential review for changed code. Use
`clanker-skills:dimensional-analysis` for a focused audit of units, scales,
rounding, and numeric bounds. Neither workflow authorizes fixes, live probes,
or external issue creation.

Use `clanker-skills:codebase-search` for a focused read-only source
investigation when delegation is permitted. Handle simple known-file lookups
directly and check decisive citations against the requested checkout.

Use `clanker-skills:gather-business-context` when missing business context
prevents analysis, then use `clanker-skills:analyze-data-quality` to assess the
data and equations. Apply `clanker-skills:uncodixfy` to frontend UI work. Use
`clanker-skills:git-hygiene` for commits, branches, and history changes, and
`clanker-skills:issue-and-pr` for issue and pull request prose.

After pushing commits or starting or rerunning CI, wait at least five minutes
before checking CI status. Wait at least five minutes between later CI status
checks. Do other useful work or yield while waiting.

Before editing or publishing durable prose, apply
`clanker-skills:prompt-leakage` and its deletion test. Use
`clanker-skills:simple-english` for technical prose with aircraft-manual
clarity. Preserve facts, uncertainty, and the difference between requirements
and recommendations. Do not apply this style to marketing or brand copy unless
requested. Keep internal review notes out of the artifact.

Use `clanker-skills:i-have-adhd` only when the reader asks for it. It changes
the shape of the reply, not the Clanker output contract: put the result or next
action first, keep comparable items in a table of at most five rows per group,
and end an agentic loop with one closing message that states what changed, what
was verified, and the one next action.

Use tables for comparable findings, inventories, and mappings. Keep them narrow
enough for an 80-120 column terminal: 2-4 columns, cells of about 8 words, the
row label first, and long reasons on a short line under the table. Use prose
for causal explanations and numbered lists for procedures. Preserve the
evidence and its limits in the form that best helps the reader.

When runtime history or notes tools are available, use them to preserve the
task outcome, constraints, authorized actions, rejected ideas, and unresolved
questions. Check retrieved conclusions against current evidence. Distinguish
configured features, exposed tools, and successful execution. Continue with the
available context when runtime tools are unavailable.
```
