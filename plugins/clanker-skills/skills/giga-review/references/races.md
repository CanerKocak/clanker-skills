# Race-condition branch

## Map shared invariants, not just locks

Inventory every mutable authority: database row/set, in-memory book, queue,
cache, filesystem object, nonce, lease, external provider operation, and chain
observation. For each record its business identity, invariant, every reader and
writer, competing actors, read/decision/write sequence, durable guard, failure
windows, retry identity, and downstream effects.

Examples of invariants are “one credit per canonical event” or “available funds
cannot be spent twice.” A row ID may not be the correct identity. Derive the
identity from the invariant: tenant, account, asset/network, operation kind,
event/log index, and request digest where those fields matter.

Enumerate API/admin handlers, workers, schedulers, webhooks, replays, migrations,
manual scripts, and recovery endpoints. If any writer is inaccessible, the
invariant cannot receive full concurrency assurance.

| Search family | Follow through to |
|---|---|
| exists/find/get/count/balance/status/version | Decisions and later mutations or external actions based on that read |
| create/insert/upsert/update/delete/increment/decrement | Predicates, affected-row checks, unique keys, triggers, other writers |
| transaction/lock/mutex/atomic/CAS/lease | Exact scope, connection, isolation, ownership, lifetime, process boundary |
| await/spawn/select/cancel/timeout/retry | Suspension, cancellation, duplicate execution, partial state persistence |
| publish/enqueue/claim/ack/outbox/inbox | Durable intent, delivery semantics, dedupe identity and recovery ordering |
| file access/stat/open/rename/temp | Stable object identity versus repeated path lookup, symlinks and replacement |

## Required interleaving

For each suspected race write the smallest schedule with initial state, actor
identities, reads, ordering, writes/effects, and final invariant violation:

```text
Initial: spendable=100, no reservation
A reads spendable=100
B reads spendable=100
A authorizes 80 and persists/sends its effect
B authorizes 80 using its stale decision
Final: obligations=160 against 100
```

Then try to disprove that schedule using the actual guard. An `await`, two
requests, or missing lock is not alone a defect. A single-threaded event loop
does not serialize work across awaits; a local mutex does not cover another
process. Conversely a verified single-writer authority may eliminate a race
without a database lock.

## Proof obligations by pattern

| Pattern | Required checks |
|---|---|
| Check then insert | Business uniqueness in the real schema; nullable/partial/composite keys; atomic conflict handling; no external effect before dedupe |
| Check then update | Conditional mutation/CAS or lock before the governing read; affected-row result checked; every writer obeys the same protocol |
| Absence/count invariant | No assumption that locking existing rows locks an absent row or prevents phantoms; inspect parent/counter/predicate protection |
| Transaction wrapper | All queries use the same transaction client; correct isolation; commit/rollback path; no swallowed failure committing partial work |
| Multi-row invariant | Write skew, lock ordering, range predicates, deadlocks, consistent retry of the whole decision unit |
| In-memory actor | Serialization includes all entry points; state not split across detached tasks; crash/restart cannot replay inconsistent state |
| Lease/distributed lock | Expiry/renewal, ownership-checked release, stale holder writes, fencing or durable version enforcement |
| Idempotency | Key binds actor and request meaning; same key/different payload; effect and dedupe ordering; retention versus replay horizon |
| Queue/webhook | Concurrent claim, redelivery, result before ack, ack before result, poison message, scheduler/manual overlap |
| External effect | Timeout means unknown; stable operation identity; query/reconcile before retry; double send after lost response |
| Cache | Stale positive/negative entries, invalidation ordering, tenant key, fallback source, authorization recheck at irreversible action |
| Filesystem | Opened-handle identity versus check/reopen, symlink/reparse traversal, safe atomic create/replace |

Verify database/runtime semantics against the project's actual version and
schema. `upsert`, `transaction`, “exactly once,” and “atomic” in a name are not
proof. A uniqueness constraint can protect rows while duplicate transfers still
escape before insertion.

## Crash and cancellation matrix

List interruption points for each load-bearing operation:

```text
read/check -> reserve -> persist intent -> dispatch -> observe result
-> commit result -> publish event -> acknowledge -> release resources
```

For each boundary ask what is durable, what the caller believes, who retries,
which identity is reused, and how reconciliation resolves unknown outcomes.
Cover cancellation after a side effect but before success acknowledgment,
crash after commit but before publish, and release/compensation running twice.
Rollback cannot undo an already-sent network or chain action.

For matching/settlement flows, include place/cancel/replace, partial fill,
expiry/resolve/void, reload after crash, and concurrent admin/worker transitions.
For custody/watchers, include duplicate/out-of-order events, backfills, reorgs,
and per-event rather than merely per-transaction identity.

## Verification and closure

Use deterministic barriers or a model schedule in isolated tests when allowed,
not sleep-based live races. Check both failing schedule and guard-enforced
serialization; distinguish a model from the real transaction boundary.

Every mapped invariant needs either a demonstrated violation, a verified guard
that covers all relevant actors and failure windows, or a named evidence gap.
“Could race” is a candidate, not a finding. Guard coverage must link to the
actual schema/lock/protocol and all writers, not one happy-path test.
