# Evidence contract

## Verified

Use `verified` only when all applicable conditions hold:

- the intended repository and revision are identified;
- the changed-root set and impact-graph version match the candidate under
  review;
- the compiler, type checker, or language server is healthy for each relevant language;
- the query covered every known representation of the relationship;
- the result limit and traversal depth did not truncate the set;
- an independent method checked dynamic or string-based edges;
- source evidence supports every reported item.

## Partial

Use `partial` when useful evidence exists but any condition above is not met.

State the exact limitation beside the conclusion. Examples include an unavailable LSP server, an unsupported template language, unresolved dynamic dispatch, generated code, or a traversal limit.

## Completeness check

Try to disprove the result with a method that has different failure modes.

Examples:

- Compare LSP or compiler references with ast-grep call expressions.
- Compare symbol dependents with imports, exports, route registries, and string identifiers.
- Compare inferred test targets with test names, fixtures, and package scripts.
- Compare a state transition map with database writes, queue workers, retries, and recovery jobs.

A second query through the same tool does not provide an independent check.

When specialist skills contribute to the graph, preserve their evidence class:

- ast-grep-callchain-audit supplies structural edges;
- call-chain-invariants supplies product-surface applicability;
- compiler or LSP evidence supplies symbol and type relationships;
- text search supplies dynamic, string, registry, and generated-edge candidates.

Merging these into one graph is stronger than presenting each as an independent
complete inventory. Agreement between contributors does not erase a shared blind
spot; reconcile the edge against source or runtime evidence.
