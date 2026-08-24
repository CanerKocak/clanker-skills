# Review convergence contract

Use this contract for reviews whose conclusion will support a code change,
merge, deployment, money calculation, authorization decision, or other
load-bearing claim. The goal is not fewer checks or more checks. The goal is
independent evidence that closes named obligations.

## 1. Bind evidence to one candidate

Freeze these fields before review:

- repository root and a hash of the user-contract brief;
- base ref, fetched base SHA, and merge-base SHA;
- HEAD SHA and HEAD tree SHA;
- staged, unstaged, and untracked-state hashes;
- initialized submodule commit pointers, with dirty nested repositories reviewed
  separately;
- combined candidate fingerprint and exact changed-file set;
- impact-graph version;
- test-evidence version;
- runtime evidence source, environment identity, and timestamp when applicable.

The repository, base, HEAD, dirty-state, fingerprint, and changed-file fields
identify code. The graph and test versions identify supporting evidence.
Runtime identity identifies the external world against which the code was
checked. A copied SQL expression, fixture, or synthetic database is not the
production query boundary. A screenshot is not a runtime identity.

Every review artifact names the candidate fingerprint. When the candidate
changes, invalidate only evidence whose stated assumptions or scope changed.
Unrelated evidence may remain valid; candidate-wide approval does not.

## 2. Use proof-carrying review actions

A review action is admissible only when it names:

1. the open obligation it can close;
2. the exact candidate or runtime snapshot it inspects;
3. the oracle or method;
4. a relevant failure class the current evidence can miss;
5. the artifact it will produce;
6. the conditions that would invalidate that artifact.

If the action cannot name a distinct miss, classify it as attention sampling.
Sampling may find a bug, but it is not new semantic coverage and cannot close a
database, runtime, contract, or candidate-binding gap.

## 3. Separate review failure modes

Use these roles when all three risks apply. Do not send the same prompt to three
reviewers and call their agreement independent evidence.

### Blind contract reconstruction

Receives the user contract, canonical domain sources, impact graph, and exact
candidate. It does not receive prior findings or dispositions. It reconstructs
the intended behavior and tries to find an implementation that violates it.

### Runtime-boundary falsification

Attacks joins between code and the environment: database query boundaries,
external APIs, lifecycle states, exact-once behavior, units, decimal scaling,
valuation time, permissions, retries, and stale or partial data. It distinguishes
logic-unit tests from evidence against the deployed boundary.

### Evidence audit

Audits the acceptance ledger itself. It looks for proxy evidence, copied
expressions, synthetic-only tests, stale artifacts, wrong repository or base,
wrong database or role, fixture screenshots presented as live, and claims whose
scope is broader than the observed evidence.

Code-structure review belongs to `thermo-nuclear-code-quality-review`; structural
edge discovery belongs to `ast-grep-callchain-audit`. Repeating those entire
passes here adds correlation, not coverage.

## 4. Adjudicate findings before changing code

A review finding is a falsifiable claim, not an instruction. Before accepting
it, bind the claimed failure to the reachability envelope in the brief:

- the target branch, deployment, and rollout epoch;
- a supported product producer, or an unsupported input that is relevant at an
  untrusted security boundary;
- historical state or a format that actually shipped and can remain at cutover;
- a concrete contract harm and whether this candidate introduced or worsened
  it;
- the user's authorized scope.

Use `yagni-anti-ceremonial` and record one disposition:

| Disposition | Required evidence | Candidate action |
|---|---|---|
| **ACTIONABLE** | `LIVE` or justified `RESIDUAL`, harmful in the target envelope, with an in-scope remedy. | Fix the smallest owning boundary. |
| **DECLINED** | `N/A`, `CEREMONIAL`, or `THEATER`. | Do not change code. Preserve the failed reachability premise. |
| **FOLLOW-UP** | Real and reachable, but pre-existing or outside the authorized candidate, which does not worsen it. | Report separately. Do not smuggle it into the patch. |
| **OPEN** | Material producer, inventory, deployment, or security evidence is missing (`PARTIAL`). | Obtain the missing proof or report the exact limitation. Do not guess by adding compatibility code. |

Stop as soon as authoritative evidence disproves a load-bearing premise. A
legacy migration is not justified when the old format never shipped to the
target, and an inventory query is unnecessary when no target producer ever
existed. Staging state does not imply production state. Product support for one
wallet flow does not imply support for every technically constructible client
transaction; separately evaluate hostile inputs only where the trust boundary
makes them security-relevant.

## 5. Converge by evidence gap

When a finding repeats without new evidence, choose one of four actions:

- create executable evidence against the missing boundary;
- inspect a new authoritative source with a different failure mode;
- narrow the claim and record the exact `partial` limitation;
- request the authority or external state change needed to continue.

Do not request another opinion merely because the prior opinion was
uncomfortable. Do not run a full restart after every edit. Batch accepted
changes, update the candidate, and re-run only the evidence invalidated by those
changes. Final hook or policy requirements still apply to the final fingerprint.

## 6. Resolve competing improvements consistently

Use this precedence order:

1. user contract and authorized scope;
2. canonical money, authority, state, unit, and time semantics;
3. closure of material evidence gaps;
4. smallest behaviorally correct change;
5. structural simplification that reduces concepts without expanding blast
   radius;
6. follow-up refactors outside the current contract;
7. style preferences.

This order prevents oscillation between "make it minimal" and "make it more
abstract." A refactor wins only when it preserves the higher-ranked contracts
and deletes meaningful complexity inside the authorized scope.

## 7. Acceptance ledger

Keep one internal row per obligation:

| Obligation | Candidate/runtime | Evidence | Distinct miss covered | Status | Invalidation condition |
|---|---|---|---|---|---|

Status is `verified`, `partial`, or `open`. Completion requires no open blocking
obligation. `Partial` is an honest terminal state only when the limitation is
named and the user did not require stronger proof.
