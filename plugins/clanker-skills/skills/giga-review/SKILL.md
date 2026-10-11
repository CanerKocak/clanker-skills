---
name: giga-review
description: >
  Run a comprehensive, read-only financial-code audit with twice-run scouts,
  explicit coverage ledgers, differential review, and four specialist branches:
  dimensional arithmetic, race conditions, unsafe defaults, and unsafe fallbacks.
  Use for deep repository, flow, or change audits; not routine small code edits.
---

# Giga review

Map before judging. An audit is complete only for its declared scope, and only
when every inventoried surface has an evidenced disposition. A long checklist,
two agreeing agents, and no findings do not prove safety.

## Authority and execution

The lead owns the scope, evidence ledger, integration, and final verdict.
Workers gather evidence; their confidence does not establish a defect.
Keep review read-only unless the user separately authorizes changes. Do not
create issues, write repository reports, install dependencies, modify data,
call live services, publish code, or conduct live race/fuzz/exploit attempts
merely because this skill was invoked. Use working-context ledgers by default.
Run permitted synthetic tests only in an isolated location and inspect test
setup for network, secrets, database, and startup side effects first.

Use the runtime's actual delegation tools, not assumed `Task` or named-agent
installations. If delegation is available, this workflow explicitly calls for
two runs of the same scout role per branch plus independent finding validation.
Bound concurrency to available capacity. Workers are read-only and do not
subdelegate. If delegation is unavailable, run the passes sequentially and
report the missing independence; do not represent a self-check as another agent.

## 1. Freeze scope and build the denominator

Read [coverage.md](references/coverage.md). Establish FULL, TARGETED, or DIFF
mode, the exact repository/worktree snapshot, and all exclusions. Do not infer
an arbitrary base branch. Record the user-selected base/head or resolve the
review base from the actual PR/branch metadata. An unresolved base leaves
regression attribution blocked; it need not stop a current-state audit.

Inventory all scoped files before filtering by risk or keywords. Map registered
entry points, definitions, callers, schemas, persistence, deployment/config,
dependencies, jobs, callbacks, and recovery paths. Include untracked/ignored
source and nested repositories when relevant and authorized; record absent
access explicitly. Trace security and financial authority, not folder names.

For a deep function read, record input origins, preconditions, branches, reads,
writes, external effects, ordering, returns/errors, and unresolved assumptions.
Derive invariants from the active contract. Do not manufacture a fixed quota of
invariants or assumptions to fill a form.

## 2. Establish the differential map

For DIFF mode, read [differential.md](references/differential.md) and the installed
`differential-review` skill. Reuse its history, adversarial analysis, and
finding-promotion methods. Giga-review owns scope: risk tiers order the work;
they never authorize skipping low-risk files, stopping at one hop, or excluding
unchanged dependencies that carry an affected invariant. If that skill is not
installed, use the self-contained differential reference and disclose this.

Map every changed hunk, including removals, renames, config, schemas, dependency
versions, and generated-source changes. Assign before/after semantics, affected
entry points, and branch applicability. Cover branch-independent regressions
such as removed authorization, validation, secret exposure, parser trust, or
unsafe external calls in the differential pass itself; the four specialists
are not a reason to drop a changed hunk that fits none of them.

FULL and TARGETED audits may use history to explain intent, but cannot label a
condition newly introduced without a verified baseline.

## 3. Open four mapping tasks; run each scout twice

Create one internal mapping work item per branch. This is not an instruction
to create four issues on an external tracker. Read each branch reference before
dispatch; give workers only its needed reference and the common coverage rules.

| Branch | Required mapping unit | Reference |
|---|---|---|
| Dimensionals | Every numeric source, unit/scale/context change, operation, comparison, aggregation, and serialization/storage boundary | [dimensional-analysis](../dimensional-analysis/SKILL.md), [arithmetic](../dimensional-analysis/references/arithmetic.md) |
| Races | Every shared invariant with all readers, writers, actors, ordering windows, durable guards, and external effects | [races.md](references/races.md) |
| Defaults | Every explicit or implicit default and its precedence, omission trigger, producer, and consumer | [defaults.md](references/defaults.md) |
| Fallbacks | Every exceptional/alternate path, its trigger, effect history, substituted result, and recovery consumer | [fallbacks.md](references/fallbacks.md) |

For each branch use the identical scout role contract twice:

1. **Pass A:** enumerate from entry points/producers toward stores and effects.
2. **Pass B:** fresh run of that same role, same frozen scope and schema, but
   enumerate backward from stores/effects and implicit/runtime behavior. Do not
   supply Pass A's inventory or findings before Pass B returns its own map.
3. **Reconcile:** union the maps by semantic identity. Investigate A-only and
   B-only rows, conflicts, unvisited files, and unresolved edges. Record whether
   the second pass found additions. Two runs agreeing is not proof of coverage.

Keep scouting separate from defect adjudication: scouts return maps, evidence,
and suspicions without severity. If the frozen source changes, invalidate the
affected maps and downstream results, rather than mixing snapshots.

## 4. Review the reconciled maps

Only start a branch's review after its two passes and reconciliation are
recorded. The branches may run in parallel; the lead owns shared rows and
cross-branch effects. Give a branch reviewer its entire reconciled map, its
reference, the differential map, known invariants, and unresolved boundaries.
Do not give it a predetermined verdict.

Review all rows, not merely suspicious ones. End each row with REVIEWED,
NOT_APPLICABLE plus reason, or BLOCKED plus the missing evidence. REVIEWED means
the row's proof obligations were addressed, not necessarily that it is safe.
Track candidates separately. Apply the dimensional skill inside this shared
ledger; do not launch another dimensional scouting cycle.

Trace combinations: a default can relax a bound that enables overflow; a
fallback can replay an external transfer; a race can reuse a stale quote with
different units. One worker's local guard does not discharge another boundary.

## 5. Validate findings and close variants

Read [findings.md](references/findings.md). Give an independent validator the
candidate claim, exact source/snapshot, proposed reproducer, contract evidence,
and strongest known defense—not a preassigned severity or trusted verdict.
The validator attempts to disprove reachability and harm.

For a confirmed root cause, search semantic variants across callers, rails,
implementations, statuses, feature/config states, and retry/recovery paths.
Use compiler/LSP evidence where available, AST searches, and independent text
searches; one channel alone is not exhaustive. Record unavailable tooling and
every unresolved boundary. Follow through to observable harm and state recovery.

## 6. Report the bounded result

Lead with findings and the exact scope. Use tables for comparable findings and
coverage. Report the snapshot, differential attribution, both scout runs per
branch, reconciliation deltas, reviewed/total counts, blocked rows, exclusions,
tests actually executed, and remaining uncertainty. Show zero findings when
appropriate, not a fabricated issue for each branch.

Completion requires every file, changed hunk, relevant edge, and branch item to
have an evidenced disposition; every candidate must be confirmed, rejected, or
open. New inventory rows reopen their review obligations. No pending rows may
be hidden in summary totals. BLOCKED/OPEN rows mean PARTIAL assurance, even if
the accessible work is finished. Never say the repository is secure or that two
scouts guarantee no corner was missed.
