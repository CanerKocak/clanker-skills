# Differential review across all branches

## Freeze what changed

Use the actual requested revision range. For a PR, resolve its base/head and
merge-base as appropriate; distinguish the PR diff from changes already in its
target branch. A local working tree may add staged, unstaged, and untracked
changes beyond HEAD. Record each included layer. Do not silently compare with
`main`, drop dirty changes, or invent a baseline for greenfield code.

Build the hunk census using rename-aware name/status and full diffs. Inspect
both sides of removals and renames. Read complete affected functions/types plus
their callers, tests, schemas, config loaders, generated-source inputs, and
dependency version changes. A zero-line diff in a caller does not make its new
behavior irrelevant.

Load the sibling differential-review skill when available. Its triage and
history guidance complements this workflow; its size-based sampling is not a
coverage exemption here. The four branch inventories consume the same hunk map.

## Hunk and behavior map

For every hunk record before -> after semantics, changed invariant, affected
entry points, branch applicability, and the proof needed. If a hunk affects no
specialist branch, review its security/correctness consequences directly and
record why the specialist lenses do not apply.

| Delta | Questions that drive expansion |
|---|---|
| Arithmetic/type | Did units, scaling, rounding, overflow behavior, accepted bounds, or serialization change? |
| Concurrency | Did read/write order, lock scope, await placement, transaction client, uniqueness, isolation, or ack timing change? |
| Default | Did omission, empty/null/zero, config precedence, schema default, or effective deployment behavior change? |
| Fallback | Did errors become success, retry conditions change, alternate sources gain authority, or partial effects escape? |
| Validation/auth | Was a check removed, moved after use, bypassed by a new entry point, or changed from deny to allow? |
| Shared contract | Which unchanged readers/writers now receive a different value, status, error, identity, or timing guarantee? |
| Schema/migration | Can old and new readers coexist? What happens to residual rows and rollback/replay? |
| Library/build | Did a version, feature, flag, target, or runtime switch change numeric, retry, parse, or transaction semantics? |
| Tests | Does a changed fixture mask the old invariant? Did tests remove an important negative or concurrency case? |

Trace changed producers forward and unchanged consumers backward until both
agree on the new contract. Search for removed helpers and old assumptions as
well as new names. Resolve indirect exports and dynamic registrations, not just
textual references to the changed symbol.

## History is evidence, not permission

Read blame/log around changed safeguards, previous incident fixes, and schema
evolution. Use history to learn why a condition existed. A commit message is
evidence of intent, not proof that a risk is accepted or a new behavior is safe.
Reconcile current specs, tests, comments, and executable behavior when they
conflict; mark unresolved policy rather than choosing whichever supports a bug.

| Attribution | Required evidence |
|---|---|
| Introduced | Violating path exists at head and is absent or guarded at base |
| Worsened | Existing exposure grows in reachability, magnitude, frequency, or recovery cost; show the delta |
| Newly reachable | Defective unchanged code becomes callable through a new route/config/state or input domain |
| Pre-existing | Same harmful path and relevant conditions occur at base; report separately from regressions |
| Fixed | Base counterexample is prevented at head and the replacement path preserves the invariant |
| Unresolved | Baseline, deployment, or contract evidence cannot establish attribution |

Newly introduced defaults/fallbacks include changed effective values and newly
reachable old branches, not only added `||` or `catch` lines. Full audits map all
existing instances. Diff audits inventory affected instances plus their shared
dependencies, and explicitly label unrelated legacy behavior out of scope.

## Differential verification

When safe and practical, run the same minimal counterexample against base and
head in isolated locations with the relevant dependency/config versions. A
head-only failure establishes current behavior, not when it was introduced.
Do not checkout/reset the user's working tree to compare revisions.

For each claim check a nearby valid case, negative case, boundary, and relevant
replay/ordering case. Property tests should state the invariant rather than copy
the implementation. Do not mutate app tests during a read-only review unless
authorized; isolated fixtures can demonstrate the reasoning with that limit.

## End condition

Every hunk has a disposition and every changed invariant has its dependent
boundaries accounted for. A clean diff review can coexist with pre-existing
findings. Report regressions, existing findings, fixed behavior, and unknown
attribution separately; do not charge a patch with bugs it did not introduce.
