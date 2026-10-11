# Numeric meaning and arithmetic proof

## Numeric record

Record a number as `(identity, unit, scale, representation, domain, rounding,
time/context)`. Keep unknown fields unknown until a producer or contract proves
them. Two values can have the same unit and still refer to different assets,
markets, accounts, price snapshots, or accounting periods.

| Field | Questions and evidence |
|---|---|
| Identity | Which asset, network, market, outcome, account, and denomination? Is an address sufficient without its chain? |
| Unit | Money, shares, money/share, base-token/quote-token, fraction, basis points, seconds, blocks, rate per period? |
| Scale | Human units or raw atoms? Decimal exponent, fixed-point binary exponent, database scale, oracle decimals? |
| Representation | Integer width/sign, float, decimal context, bigint, numeric string, database numeric, JSON number? |
| Domain | Allowed and reachable bounds, zero/negative semantics, nullability, finiteness, maximum intermediate? |
| Rounding | Floor, ceiling, truncation, nearest/ties, exactness required, remainder owner, application order? |
| Time/context | Price as of which snapshot? Annual versus per-second rate? Duration versus timestamp? Available versus reserved money? |

Compact labels such as `D6{USDC@chain}`, `D0{shares}`, and
`D8{USD/BTC}` mean raw value divided by `10^scale` gives the stated unit.
Use labels only after establishing that convention. A decimal library's
mantissa/exponent pair is not a fixed `D18` value merely because it handles money.

## Inventory from both ends

Start from the repository file census and registrations, not a list of files
containing `amount`. Assign every scoped file a relevant/N/A/blocked result.
Then find numeric entities and link their edges across languages.

| Surface | Search and trace |
|---|---|
| External inputs | HTTP/RPC/message schemas, form parsers, CLI arguments, events, provider payloads, env/config parsers |
| Numeric construction | Decimal/Big constructors, parseInt/parseFloat, Number, bigint casts, from/to units, serde conversions |
| Operators | Add/subtract/multiply/divide, mod, shifts, powers, min/max, clamps, comparisons, negation, compound assignments |
| Aggregation | SQL SUM/AVG/CASE, grouping/join grain, reduce/fold, running totals, weighted averages, batching |
| Conversion | toFixed, quantize, rescale, round, floor/ceil/trunc, as/casts, checked/saturating/wrapping operations |
| Storage | Column scale/precision, constraints, generated columns, triggers, procedures, migrations/backfills |
| Consumers | Ledger writes, signed amounts, chain/provider calls, order size, fees, API JSON, event payloads, display formatters |
| Implicit arithmetic | ORM increment/decrement, currency formatters, percent widgets, unit-bearing defaults, library helpers |

Read the actual definitions behind aliases and wrappers. Expand dynamic dispatch,
generated bindings, alternate implementations, and stored procedures when they
carry the same value. A missing parser means a coverage gap, not N/A.

For each edge record the source record, transformation, destination record,
caller, governing evidence, and whether it was inspected. Equal variable names
on opposite sides of an RPC boundary are not proof of agreement.

## Algebra obligations

If `raw_x` encodes `x * 10^sx` and `raw_y` encodes `y * 10^sy`:

| Operation | Required relationship |
|---|---|
| Addition/subtraction/comparison | Same unit and compatible identity/context; align scales before operating |
| Multiplication | Units multiply; unadjusted raw scale is `sx + sy` |
| Division | Units divide; unadjusted raw scale is `sx - sy`; account for integer division and desired output scale |
| Rescale to `sz` | Multiply by `10^(sz-s)` or divide with the required rounding if the exponent is negative |
| Rate application | Convert percent/basis points/fraction exactly once and apply the correct time basis |
| Aggregation | Same units and grain; prevent joins, duplicated events, mixed assets, or repeated principal from inflating totals |

Examples: `USD / (USD/share) = share`; `share * (USD/share) = USD`.
`USD + share`, `USDC@chainA + USDC@chainB`, or comparing seconds to milliseconds
requires an explicit, evidenced conversion or bridge contract.

Do not assume multiplying before dividing is universally correct. It may
preserve precision but overflow; dividing first may avoid overflow but erase
valid value. Prove both the intermediate range and acceptable error, then inspect
whether the implementation uses widened or full-precision multiply/divide.

## Range and precision

For each expression, inspect the exact type and deployed dependency version from
the repository's lockfile/source. Name its error behavior. Do not infer that
`Decimal` is unbounded or that a Rust integer cannot panic/wrap in this build.

| Boundary | Required probes |
|---|---|
| Accepted domain | Negative, signed zero, zero, minimum tick/atom, maximum accepted input, absent/null/empty, scientific notation |
| Integer range | Limit minus one, limit, limit plus one; signed/unsigned conversion; widened products and narrowing return |
| Floating range | Integers around `2^53`, subnormals, nonfinite values, cancellation, binary representation of decimal fractions |
| Decimal context | Maximum mantissa/exponent, multiplication/division precision, quantization failure, DB column rounding/rejection |
| Denominator | Zero, tiny nonzero, inverted price, empty aggregate, total supply/reserves after fees |
| Repetition | Many small fills/transfers, accrued interest, repeated compounding, adversarial split/merge strategies |
| Encoding | String -> number -> string, JSON bigint policy, locale separators, exponent encoding, display input round trip |

Use bounds at every layer. A UI maximum does not protect a public backend; a
backend check may protect the internal worker only if every producer passes it.
If accepted input can overflow, trace error propagation: request rejected,
transaction rolled back, actor/task terminated, queue stalled, process exited,
or state partially committed. Do not call an actor failure a whole-process crash.

## Rounding and conservation

Name who receives the remainder and at which point quantization happens. Inspect
the order of fee, discount, reserve, fill, settlement, and refund calculations.
Rounding obligations come from the actual economic contract, not a universal
"round in favor of the protocol" rule.

| Property | Falsification question |
|---|---|
| Conservation | Do debits equal credits plus named fees/dust, per asset and operation? Are locked funds counted exactly once? |
| Monotonicity | Can a larger input buy less solely from a conversion error, or lower collateral appear safer? |
| Round trip | Does encode/decode preserve values within the allowed quantum? Does price inversion double-convert scale? |
| Split/merge | Can many tiny orders avoid fees or mint value compared with one combined order? Is this intended? |
| Bounds | Can net output be negative, exceed gross input, or release more reserve than was held? |
| Dimensional identity | Is a fee in quote units subtracted from a base quantity? Is a rate treated as an amount? |
| Temporal identity | Does a cached quote combine old price with new precision, fees, balances, or market definition? |

Follow partial fills, cancellation, expiry, reversal, retry, and reconciliation.
The successful trade path does not cover amount restoration after failure.

## Small counterexamples

| Shape | Candidate counterexample | Defense to inspect |
|---|---|---|
| Mixed scale | Add raw `1_000_000` (one D6 token) to raw `1_000_000_000_000_000_000` (one D18 token) | Common-scale conversion at the actual addition |
| Early truncation | Integer `quantity / denominator * price` becomes zero despite a nonzero payable result | Full-precision mul/div, guaranteed divisibility, permitted dust rule |
| Safe result, unsafe intermediate | `amount * scale / divisor` fits only after division | Widened product, checked domain bound, bounded numeric library |
| Fee leakage | Per-fill floor makes repeated sub-quantum fees zero | Cumulative fee accounting or explicit minimum/dust policy |
| False alarm | Bounded input cannot exceed the numeric type even after multiplication | Prove the bound on every reachable input path, not only the UI |

A minimal reproducer should exercise the actual helper when safely importable.
Otherwise label it an isolated model and state which parser, library, or runtime
boundary remains unverified. Keep intended policy differences separate from bugs.
