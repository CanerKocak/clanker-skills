# Validate findings and report bounded coverage

## Promotion gate

A scout match or reviewer suspicion is a candidate. Before assigning defect
severity, establish all of these:

1. The current contract and why it applies to the specific actor, asset,
   operation, state, deployment, and time.
2. A reachable producer/input and an end-to-end path to the harmful boundary.
3. A concrete counterexample: values, interleaving, omission, or failure window.
4. The observed/source-proven invariant violation and resulting impact.
5. The strongest plausible defense and an attempt to verify it.
6. Baseline attribution when reviewing a change.

Policy disagreements are not defects without a violated contract. A documented
choice does not excuse a demonstrated violation of a stronger boundary. Keep
uncertain contract/authority facts explicit; do not invent an approval process.

## Independent validation packet

Send a separate read-only validator the snapshot, candidate claim, relevant
ledger IDs/source locations, contract evidence, counterexample, and known
defenses. Ask it to reproduce or refute the claim and search for the smallest
counterexample to the proposed reasoning. Do not give it a trusted verdict or
severity. It may inspect callers and guards needed to adjudicate the claim.

| Disposition | Meaning |
|---|---|
| CONFIRMED | Reachable contract violation supported; label static/model/runtime evidence accurately |
| REJECTED | Specific guard, unreachable precondition, or valid contract disproves this claim |
| OPEN | Evidence is insufficient or contradictory; name the discriminating check |
| POLICY | Proposed behavior preference without an established contract violation |
| OUT_OF_SCOPE | Separate issue beyond the authorized review boundary; do not silently broaden work |

A model reproducer is not production runtime proof. A failed test setup is not
a rejected candidate. No tests is an assurance gap, not a severity multiplier.
The lead inspects decisive evidence and resolves disagreements by a focused
source check/test, not majority vote or repeated confident wording.

## Variant closure

Generalize the root cause into a semantic predicate. Search for the same missing
guard, conversion, identity rule, default, or fallback—not only copied syntax.
Enumerate candidate entities independently of the defect qualifier, then decide
each one. A search for `catch { return 0 }` cannot rule out `Result.or(0)`.

| Axis | Examples to inspect when applicable |
|---|---|
| Entry point | App/admin/API, RPC, worker, scheduler, webhook, manual tool |
| Lifecycle | Create/update/cancel/replace, partial/terminal, expiry, recovery, replay |
| Representation | Float/decimal/integer/string, DB/API/chain, seconds/milliseconds |
| Implementation | Sibling asset/rail/provider, overload, subclass, SQL procedure, wrapper |
| State | Fresh/existing/legacy row, missing/null/zero, failed/unknown/successful external outcome |
| Runtime | Single/multiple workers, restart, lease expiry, changed config/library version |

Do not assume every sibling shares one invariant. Classify applicable,
different-contract, not applicable, or unknown, with evidence. A dismissed
variant remains in coverage so a future worker does not rediscover it.

## Report schema

Include summary tables for multiple findings and per-branch coverage. A finding
record contains location and snapshot, invariant, trigger/reproducer, complete
call/effect chain, impact, checked counterevidence, evidence strength, attribution,
and variant coverage. Assign severity from demonstrated harm and reachability,
separately from confidence and review priority. Suggest only a remedy supported
by the established contract; do not implement it during a review.

Coverage shows files, hunks in diff mode, edges, and branch items as separate
populations. Show both scout run identifiers, A/B-only additions, resolved
disagreements, exclusions, BLOCKED/OPEN entries, and tests actually executed.
State which environment was inspected; no local result implies staging or
production verification. Do not include secrets or private transcript residue.

## Final gate

Verify that every original scope item and newly discovered item remains in the
ledger with an outcome. Ensure both scout runs used the same snapshot and all
confirmed candidates received independent adjudication when delegation exists.
If a worker is interrupted, missing output remains pending/blocked—not a pass.

Report PARTIAL for missing baseline, unreviewed scope, unresolved dynamic edges,
inaccessible writers/configuration, open material candidates, or unavailable
required independence. Report “coverage completed for [scope]” only when its
obligations are discharged. Neither outcome is a guarantee that no bugs exist.
