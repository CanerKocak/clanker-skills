# Unsafe-fallback branch

## Enumerate failure and alternate-path edges

A fallback changes behavior when the primary operation cannot provide its
normal result. Include exceptions, errors-as-values, empty results, timeouts,
stale caches, unsupported versions, circuit breakers, provider failover,
compatibility paths, retry exhaustion, and manual recovery.

For each row map primary source/authority, failure trigger, prior side effects,
replacement source/value/action, validation repeated or skipped, retry bounds,
idempotency identity, response semantics, and eventual reconciliation.

| Search family | Trace beyond the match |
|---|---|
| catch/except/rescue/recover | Error classes swallowed, returned success, partial mutations, finally/cleanup effects |
| Result/Option unwrap-or, `orElse`, null coalescing | Unknown versus absent, numeric zero, missing identity, alternate provider |
| retry/backoff/timeout/circuit breaker | Attempts, identity reuse, full versus partial retry, unknown external result |
| cache/stale/last-known | Age, scope/key, source authority, invalidation, stale authorization or price |
| legacy/compat/unsupported/version | Validation bypass, different units/contracts, downgrade trigger |
| repair/reconcile/reset/replay | Who may invoke it, terminal state reopening, duplicate credit/send, trusted evidence |
| finally/defer/drop | Compensation/release on success and failure, cancellation, double release |

Default and fallback can overlap: a `catch` returning zero belongs in both maps,
with a shared identity and distinct obligations. Do not duplicate the final
finding solely because two branches discovered it.

## Failure-state table

For each primary call, separate outcomes before evaluating its fallback:

| Outcome | Core question |
|---|---|
| Definitely failed before effect | Is an alternate attempt safe under the same identity and policy? |
| Definitely succeeded | Can a later local failure trigger the effect again? |
| Unknown external outcome | Is state reconciled by stable identity before another send/credit? |
| Partial local success | Which writes committed and which were rolled back? |
| Valid empty result | Is it distinguishable from timeout/permission/parse failure? |
| Stale/malformed result | Is freshness/identity/shape verified before it becomes authority? |

Trace errors through wrappers. An HTTP success can contain provider failure; a
timeout can follow a successful transfer. A local rollback cannot reverse that
transfer. Logs alone do not guarantee that a caller or worker knows it must stop.

## Specific patterns

| Pattern | Proof obligations |
|---|---|
| Exception -> zero/empty | Show downstream arithmetic, permission, settlement, or status meaning; preserve unknown where contract requires it |
| Primary -> secondary provider | Same asset/network/units/finality, freshness, source authority, error semantics, and validation |
| Live -> cache | Maximum allowed age, quote/operation binding, tenant key, invalidation, permission revocation |
| Retry after send | Persisted intent, operation identity, response replay, dedupe horizon, reconciliation before re-send |
| Fallback database/client | Same transaction/consistency boundary, authorization and schema version, no split-brain writes |
| Strict -> permissive parser | Downgrade trigger attacker control, equivalent validation, canonical identity binding |
| Compensation/refund | Releases exactly the reserved amount once; cannot double refund or ignore a completed external effect |
| Manual repair | Evidence required to mark success, authorization, amount/identity binding, terminal transition and replay guard |
| Nested retries | Effective attempt multiplication, total time budget, overlapping original requests, cancellation propagation |
| Broad catch | Programmer/invariant failures not silently recast as transient provider trouble |

Inspect the previous error contract in DIFF mode. Moving an exception into a
success-shaped result changes every unchanged consumer that depended on failure.
Removing a fallback may also introduce loss of availability or stranded state;
review its real contract rather than presuming all fallback removal is good.

## Verify the failure windows

Use controlled fault injection in isolated tests when allowed: before an effect,
after the effect but before its response, before/after local commit, while
publishing, and during compensation. Verify state, return status, retry count,
and eventual reconciliation, not only which log line appears.

For a safe fallback, demonstrate that preconditions, identity, amounts, units,
authorization, and monotonic state transitions survive the alternate path. For
an unsafe candidate, show the reachable trigger and violated invariant. If the
provider's outcome or idempotency contract is unknown, retain an evidence gap
instead of asserting either duplicate payment or safety.

Every fallback row needs a primary/failure/alternate path trace, effect timeline,
and reviewed outcome. Absence of an exception handler does not prove no fallback:
inspect error-return values, middleware, SDK defaults, and background retries.
