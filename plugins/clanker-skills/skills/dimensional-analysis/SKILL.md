---
name: dimensional-analysis
description: >
  Audit numeric code for unit, asset, decimal-scale, rounding, range, and
  representation errors across calls and storage boundaries. Use for financial
  arithmetic, quotes, balances, fees, settlement, fixed-point math, or scientific
  conversions. Read-only by default; a single-formula question stays local.
---

# Dimensional analysis

Prove what each number means before judging what the formula does. Equal
machine types do not imply equal units; equal units do not imply safe ranges.

## Contract

Keep the requested scope and output medium. Read-only review does not authorize
source annotations, generated manifests, dependency installation, live calls,
transactions, or changes to balances. Keep ledgers in working context unless a
file is requested. Synthetic checks must run in an isolated temporary location
without importing modules that connect to live services.

Read [arithmetic.md](references/arithmetic.md) before analysis. It defines the
numeric record, search families, proof obligations, and counterexamples.

For a full repository or flow audit, inventory files independently of arithmetic
keywords. For a local formula question, inspect its inputs and consumers without
starting a repository audit. When invoked by giga-review, consume its snapshot,
scope, and reconciled dimensional inventory. Do not restart its two scout passes
or create a second coverage ledger.

## Standalone workflow

1. **Bind the scope.** Record revision, working-tree changes, requested flow or
   directories, and exclusions. Inspect schemas, public inputs, storage,
   serialization, workers, configuration, and callers as well as arithmetic
   helpers. Name inaccessible dependencies.
2. **Discover twice for a broad audit.** Run the same read-only arithmetic scout
   twice with the same scope and record schema. First trace inputs forward to
   effects. In a fresh agent run, trace effects and stored values backward to
   sources without seeing the first inventory. Then reconcile both inventories.
   The repeated role is intentional; fresh context and reversed traversal reduce
   anchoring. If subagents are unavailable, perform two separate passes and
   report that they were not independent agent runs. Never claim equivalence.
3. **Build the vocabulary.** Infer asset/network identity, units, scales, rates,
   time bases, signs, ranges, and rounding contracts from authoritative producers
   and consumers. Label assumptions; names and comments alone are not proof.
4. **Assign numeric records.** Give every source, conversion, calculation,
   comparison, aggregation, and boundary an ID. Link inputs and outputs. Include
   pure pass-through boundaries: an erroneous serializer need not do arithmetic.
5. **Propagate across calls.** Substitute input records into expressions and
   compare the derived result with the consumer's required record. Resolve
   helper implementations, overloads, defaults, and runtime library semantics.
   Review joins, branches, loop accumulators, database expressions, and fallback
   returns. Track every caller when a shared conversion changes.
6. **Check range separately.** Bound each intermediate in evaluation order, not
   only the final value. Cover overflow/panic, wrapping/saturation, underflow,
   loss of significance, divide-by-zero, narrowing, nonfinite values, and
   accumulation. A unit-correct expression can still halt a market actor.
7. **Falsify candidates.** Read the real bound checks and exact numeric type.
   Use a small counterexample and a nearby valid example. Test conservation,
   monotonicity, round trips, and split-versus-combined execution when relevant.
   Do not treat a copied formula as an integration test.
8. **Close coverage.** Every numeric record and boundary must be reviewed,
   explicitly not applicable with evidence, or blocked with the missing fact.
   Include all priority tiers; priority changes order, not the denominator.

## Required output

Use tables for multiple comparable records or findings. Include the snapshot,
scout reconciliation, units vocabulary, reviewed/total numeric records and
boundaries, concrete findings, rejected candidates, and exact gaps. Count from
the ledger, not estimates. If broad coverage is incomplete, report PARTIAL.

For each finding show the producer -> conversion -> consumer path, actual and
required numeric records, a violating input, the financial or operational
effect, and the strongest checked defense. Distinguish source proof, isolated
execution, and verified integration behavior. Do not claim global safety or
promise to find every bug.

When annotations are explicitly requested, prefer short unit/scale comments at
ambiguous boundaries. Keep analysis-only findings separate from proposed edits.
Use the repository's change and verification workflow before modifying code.
