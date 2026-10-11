# Unsafe-default branch

## Map effective behavior under omission

A default is any value, permission, status, provider, unit, or action selected
when an explicit value is absent or rejected. Inventory implicit behavior as
well as literals. Track source, trigger, precedence, effective value, consumers,
reachable input domain, and controlling contract.

In DIFF mode record base/head values and classify introduced, modified, newly
reachable, or pre-existing. A new caller omitting an existing parameter can
introduce a default regression without changing the callee.

| Surface | Search anchors and hidden defaults |
|---|---|
| Expressions | `||`, `??`, ternaries, `get(..., value)`, optional parameters, destructuring defaults |
| Language/types | Zero initialization, enum first member, empty collection, implicit return, bool default, sentinel values |
| Parse/coercion | Number/Boolean coercion, parse failure to zero, empty string, whitespace, invalid enum, numeric strings |
| Config | Env parser, layered config merge, CLI flags, feature gates, platform manifests, SDK defaults |
| Persistence | Schema defaults, nullability, migration backfills, generated columns, ORM omission versus explicit null |
| Security | Allow/deny policy, authentication disabled, missing secret, TLS checks, wildcard tenant/origin/network |
| Finance | Currency/chain/decimals, fees, rate basis, price, slippage, limits, quote expiry, rounding, balance/status defaults |
| Operations | Worker concurrency, retries, timeouts, cache lifetime, transaction isolation, dedupe retention |

Search wrappers and library initialization; runtime defaults may be applied
outside the changed file. Inspect lockfiles and constructors for changed SDK
behavior. Do not inspect secret values; presence and configuration logic are
enough unless the authorized task explicitly requires more.

## Input-state truth table

For each default distinguish these inputs where the language/schema permits
them. Do not equate falsy with missing.

| State | What to establish |
|---|---|
| Omitted/undefined | Default selected? Inherited value? Validation performed before or after default? |
| Explicit null | Rejected, stored, cleared, or treated as omission? Same semantics in API and ORM? |
| Zero/false | Legitimate user choice preserved, or overwritten by a truthiness operator? |
| Empty/whitespace | Rejected, interpreted as zero, empty scope, wildcard, or configured-but-invalid? |
| Invalid/out-of-range | Error or substitution? Does validation examine raw input or sanitized fallback? |
| Explicit valid value | Does merge order unexpectedly overwrite it? |

Trace precedence end to end: built-in -> library -> file -> deployment -> env
-> CLI -> per-request override, using the actual order in this application.
Check absent keys separately from explicitly empty keys. Record the effective
configuration at each supported target only from authorized evidence.

## Financial and authority probes

| Default | Failure pattern to try to falsify |
|---|---|
| Amount/balance/price zero | Unknown data becomes a real financial zero or clears obligations |
| Currency/chain/decimals | Omitted identity routes value to the wrong asset or interprets raw atoms at another scale |
| Fee/slippage/limit | Missing value removes a safety bound, or explicit zero is replaced unexpectedly |
| Status/permission | Missing/unknown enum becomes approved, settled, enabled, or globally authorized |
| Time/expiry | Seconds and milliseconds mixed; zero means both never and already expired; absence means unlimited |
| Concurrency/retry | Deployment omission creates overlap, duplicate external effects, or unbounded retries |

## Adjudication

Show a reachable omission/invalid input and the resulting contract violation.
A surprising default is not automatically unsafe. Determine whether its value
is intentional, validated, documented, and appropriate to each consumer's
authority. “Fail closed” is not universal: refusing reconciliation can also
strand funds. Name the governing outcome instead of prescribing one slogan.

Test the omission truth table against the actual parser and downstream use when
safe. If a schema requires a field at every reachable boundary, prove that all
producers pass through that schema before rejecting the candidate. UI validation
alone does not rule out direct API, worker, import, or migration producers.

Close every row with the resolved effective value, precedence proof, input
semantics, consumer consequences, and finding or evidence-backed rejection.
