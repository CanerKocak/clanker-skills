# Orchestration protocol

Use this reference for fan-out, dependency waves, parallel edits, or independent
review. Ordinary localized work should remain in the shorter SOLO loop.

## Mode decision

Answer these questions from repository evidence:

1. Are there at least two questions whose answers can be obtained independently?
2. Can each answer change the plan, acceptance checks, or risk assessment?
3. Can workers avoid shared mutable state while working?
4. Will parallel work save latency or context without creating more integration
   and verification work than it removes?
5. Is there an objective arbiter such as a test, compiler, trace, schema,
   benchmark, or canonical contract?

If one bounded decision-changing question exists, use one SCOUT. If the first
two answers are not both yes for multiple questions, do not FAN-OUT. If the
third answer is no, serialize the work. If the fifth answer is no, use workers
only to gather evidence and report the unresolved judgment to the user.

Select topology by phase:

```text
RECON: SOLO | SCOUT | FAN-OUT
EXECUTION: SOLO | DAG-WAVES | SEQUENTIAL
REVIEW: SELF-CHECK | INDEPENDENT | ADVERSARIAL
```

A task may legitimately use `FAN-OUT` reconnaissance, `SEQUENTIAL` execution,
and `INDEPENDENT` review. Do not force the whole lifecycle into one mode.

## Task and progress ledgers

Keep the stable task contract separate from mutable progress.
Keep both ledgers in working context by default; do not create repository files
for them unless the user requested or authorized durable artifacts.

```text
TASK CONTRACT
outcome:
acceptance obligations:
non-goals:
authority and approvals:
canonical sources:
baseline:
risk and reversibility:
budget or deadline:
```

```text
PROGRESS LEDGER
claim | status | exact evidence | falsifier | owner | next check
change | isolated location | dependency | integration state | verification
```

Statuses are `VERIFIED`, `PARTIAL`, or `REJECTED`. Preserve rejected hypotheses
with their smallest counterexample so later workers do not repeat them.

## Sealed worker packet

Send only the context needed for the assigned decision:

```text
ROLE: evidence channel, not a persona
DECISION: what parent decision this work can change
QUESTION: one falsifiable question
SCOPE: exact files, subsystem, sources, or hypothesis
INPUTS: task-relevant artifacts and known facts
METHOD: independent evidence method to use
MUST CHECK: native edge cases and representations
CONSTRAINTS: authority, read/write boundary, repository rules
ACCEPTANCE: evidence required from this worker
FALSIFIER: result that kills the hypothesis
RETURN: required schema
```

Do not paste the whole conversation. Do not reveal peer conclusions before an
initial independent finding when diversity matters.

## Worker return

```text
VERDICT: VERIFIED | PARTIAL | REJECTED
CLAIMS:
- falsifiable statement
EVIDENCE:
- file:line, command and result, artifact, or direct primary URL
COUNTEREVIDENCE:
- strongest conflicting observation
FALSIFICATION ATTEMPT:
- check performed and outcome
OPEN GAP:
- exact missing fact or none
RECOMMENDED NEXT ACTION:
- one decision-changing action
CHANGES:
- paths and checks, or NONE for reconnaissance
```

Narrative without exact evidence is PARTIAL. The lead must inspect decisive raw
artifacts rather than trusting the summary.

## Breadth wave

Partition by independent uncertainty, not by generic job title. Useful channels
include:

- competing root-cause hypotheses;
- structural call/data-flow and product-surface mapping;
- test and acceptance design;
- schema, API, protocol, or backward-compatibility contracts;
- security, money, performance, concurrency, or migration risks;
- an adversarial alternative that could make the planned edit unnecessary.

Use the smallest wave that covers the live channels, normally two to four
workers. Dispatch independent workers together. Cross-worker communication
requires a real dependency; otherwise they report only to the lead.

At convergence, compare evidence rather than vote counts. Preserve a correct
minority candidate until a discriminating check rejects it.

## Dependency-wave execution

Represent the implementation as a DAG:

```text
id:
depends_on:
owned files or isolated worktree:
precondition:
state produced:
acceptance command:
integration order:
```

Only nodes with satisfied dependencies enter a wave. One worker owns one node.
Use separate worktrees or sandboxes for parallel writers, even when files look
disjoint, if builds or generated state share a root.

The lead integrates nodes in topological order. After each integration:

1. inspect the diff;
2. run the node's focused check;
3. run the shared contract check affected by the merge;
4. reject or repair unexpected overlap before the next wave.

Do not let workers merge, publish, deploy, or make external changes unless the
user separately authorized that action.

## Depth drill

For the selected branch:

```text
baseline -> reproduce -> localize -> trace invariant and callers
-> minimal patch -> focused check -> regression checks -> diff review
```

Branch into multiple repair candidates only when the problem remains genuinely
ambiguous and an objective selector exists. Begin with two or three distinct
hypotheses, not many variations of the same patch. Add depth only when the
previous step produced new discriminating evidence.

## Independent review

Give the reviewer:

- the user contract and non-goals;
- the exact diff;
- baseline and post-change raw check results;
- relevant canonical sources;
- the instruction to find the smallest counterexample.

Do not give the implementer's confidence or completion verdict. Ask the
reviewer to map every finding to an affected path and a falsification check.

For high-risk ambiguous reviews, use one critic-of-review. The critic checks
whether the reviewer supplied evidence, missed a more serious invariant, or
raised speculative noise. The lead decides from evidence. One structured
disagreement round is the default; continue only when it produces a new testable
claim.

## Completion gate

Maintain an exact mapping:

```text
acceptance obligation -> observed evidence -> status
shared invariant -> callers and surfaces checked -> status
review finding -> reproduction or rejection evidence -> status
```

`VERIFIED` requires all required rows to be discharged. If a required check
cannot run or coverage cannot be established, return `PARTIAL` and state that
gap beside the result.

## Retrospective telemetry

When this workflow is used repeatedly, compare modes under similar task and
budget conditions. Track:

- acceptance and regression pass rate;
- escaped defects, reverts, and review precision;
- unresolved obligations at handoff;
- wall time, tokens, tool calls, and tool failures;
- worker overlap and merge conflicts;
- context delivered per worker;
- unique decision-changing evidence per worker;
- whether multi-agent work changed the result versus a budget-matched solo run.

Remove roles that repeatedly add no distinct evidence. Re-evaluate the harness
as models, tools, and repository tests improve.
