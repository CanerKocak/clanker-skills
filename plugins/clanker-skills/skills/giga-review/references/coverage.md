# Coverage contract and repeated scouts

## Snapshot and denominator

Record repository root, mode, base/head SHAs if applicable, tracked dirty diff,
staged diff, relevant untracked files, submodule revisions, and relevant
configuration/dependency versions. Keep a fingerprint of the actual reviewed
content; HEAD alone does not identify a dirty worktree. Do not read secrets to
construct it. Record the boundary of environment evidence, not secret values.

Inventory scoped files from version-control/file listings, not search hits.
Use NUL-safe paths when scripting. Include schemas, SQL functions/triggers,
deployment manifests, shared packages, frontend inputs, API/RPC bindings,
workers, migrations, maintenance tools, and generated code's source generators.
List vendor/binary/generated exclusions and why their behavior is or is not
represented elsewhere. Explicitly identify unavailable submodules/packages.

FULL means all scoped source/config units. TARGETED means named flows plus
reachable producers/consumers; label unrelated flows unreviewed. DIFF means all
changed units plus the transitive invariant boundary, not the whole repository.
Never silently expand a targeted request into unrelated app or live-system work.

## Ledger shapes

These are logical records, not a requirement to write JSON files. Tables,
structured working notes, or a requested artifact can hold them. Use stable IDs
across passes. Counts must be calculated from these records, not model estimates.

| Record | Required fields |
|---|---|
| Scope | Snapshot, mode, included roots/flows, excluded roots with reason, unavailable inputs |
| File | Path, revision/content fingerprint, role, per-branch applicability, reviewed status and evidence |
| Edge | Source and destination symbols/identities, kind, representation/context, discovery channel, caller proof, resolved status |
| Hunk | Base/head path and lines, before/after behavior, branch mapping, entry points, disposition |
| Branch item | ID, semantic identity, locations, producer/consumer IDs, proof obligation, discovered-by A/B/both, outcome, evidence |
| Scout run | Branch, role contract, snapshot, run ID, pass A/B, roots visited, methods, row IDs, gaps |
| Candidate | Claim, invariant, linked item IDs, evidence, counterevidence, validator result, variant IDs, attribution |

For each branch, use PENDING until its proof is done. Final file/item/edge
outcomes are REVIEWED, NOT_APPLICABLE with a concrete reason, or BLOCKED with a
specific missing fact. A file with no relevant branch items still needs an
applicability explanation supported by its contents/role, not zero search hits.
An edge is REVIEWED only after its semantics were checked, not merely discovered.

## Topology discovery

Start with registration and authoritative data definitions; confirm traversal
against independent AST and text searches. Useful frontier questions:

| Frontier | What closes it |
|---|---|
| User input | All route/RPC/CLI/message registrations and handlers, not one controller name |
| Shared helper | Definitions, exports/re-exports, aliases, wrappers, overrides, indirect callers |
| Persistent state | Readers/writers, schema constraints, triggers/procedures, migrations and live-version evidence when authorized |
| Async work | Producer, serializer, queue/topic registration, consumers, retries, scheduler, manual trigger |
| External effect | Sign/send request, idempotency identity, response decoder, receipts, reconciliation and recovery |
| Representation | Encode/decode, DB/API types, units, timestamps, enums, nullability, version negotiation |
| Build/config | Env loaders, merge precedence, feature gates, dependency versions, platform-specific implementations |

For every traversed symbol, inspect alternate implementations and error exits,
then add unvisited neighbors that carry the same invariant. Continue until the
frontier closes at an evidenced boundary: validated public input, authoritative
store, verified external contract, explicit scope boundary, or BLOCKED edge.
A directory boundary, one-hop limit, or high fanout count is not a valid stop.

## Scout packet — use this role twice per branch

Give each run the same scope, branch reference, ledger schema, and obligation:

```text
ROLE: [branch] coverage scout (mapping only)
SNAPSHOT: exact reviewed content identifier
SCOPE: included files/flows; explicit exclusions
QUESTION: What are all branch-relevant entities and edges in this scope?
PASS: A producer-forward | B consumer-backward
INPUT: frozen census, registrations, schema roots, branch reference
MUST RETURN: visited files with applicability reasons; item/edge records;
             discovery methods; unvisited files; unresolved frontier
RULES: read-only; no severity or final bug verdict; no scope expansion;
       no delegation; no assumption that keyword absence proves absence
```

Pass B is a fresh invocation of the same scout definition, not a new specialized
role. Use a new agent/context if possible; reusing an agent with Pass A still
visible is a correlated repeat and must be disclosed. Before its independent
map returns, do not show Pass A's inventory, suspects, or conclusions. Both
passes must cover the same frozen census, including lower-priority units.

## Reconciliation

Union by semantic identity (operation + state/amount/condition + boundary), not
line number alone. Keep aliases that refer to the same entity and distinct
instances that happen to have the same spelling. Preserve both evidence sets.

| Difference | Required action |
|---|---|
| A-only or B-only entity | Read its source and attach/deny it with evidence; never drop a minority row by vote |
| Same entity, different semantics | Trace definitions/producers and resolve with source or a discriminating test |
| Unvisited file | Assign it a read or record BLOCKED; not “probably irrelevant” |
| Unresolved call/store/config edge | Follow it or record the exact access/tooling boundary |
| Newly found branch item | Add it to the denominator and schedule its proof obligations |
| Missing branch applicability | Examine contents and classify, including cross-branch interactions |

Stop requesting repeat scouts after the required two unless a named new
frontier needs a bounded follow-up. “Run until nothing new appears” is not a
termination rule or a completeness proof. Closing the enumerated frontier with
evidence is the gate. Avoid rediscovering unaffected source after small changes;
invalidate affected rows and dependents using the snapshot/edge map.

## Branch review handoff

Each reviewer receives all reconciled branch rows, linked source, the applicable
contract, required before/after facts, and known evidence gaps. Ask for one
outcome per assigned row. Batch by shared invariant or end-to-end flow, not by
arbitrary file slices that split a transaction or conversion boundary.

The lead joins cross-branch findings, inspects decisive evidence, and checks
that rows have not disappeared. A discovered flaw does not excuse abandoning
the rest of the map. Under a time/token limit, deliver a prioritized partial
audit listing exactly which obligations remain unreviewed.

## Completion arithmetic

For each population separately, total = REVIEWED + NOT_APPLICABLE + BLOCKED +
PENDING. Count unique IDs, not repeated mentions. Keep file, hunk, edge, and
branch-item counts separate; do not inflate a review count by counting one file
four times. Show branch counts separately when a shared item belongs to several
branches. Complete execution requires zero PENDING; complete bounded assurance
also requires zero material BLOCKED/OPEN and both scout runs. NOT_APPLICABLE
needs a semantic reason. A confirmed bug is compatible with completed coverage.
