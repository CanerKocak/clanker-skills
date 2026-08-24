# Native semantic workflow

## 1. Establish scope

Record the repository, revision, languages, packages, and generated-code boundaries.
Confirm the relevant compiler, type checker, or language server is available.

## 2. Establish identity

Resolve each important name to a canonical definition. Use LSP when available,
`ast-grep` for structural definitions, and `rg` for exact identifiers or files.
Inspect every plausible same-name candidate before selecting one.

## 3. Map relationships

Use `ast-grep` and language tooling to map imports, exports, callers, callees,
implementations, overrides, callbacks, types, and parameter flow. Continue
through downstream boundaries that can observe the proposed change.

## 4. Inspect source

Read narrow source windows around verified definitions, call sites, state
transitions, and tests. Expand only when the open evidence gap requires it.

## 5. Check string and generated edges

Use `rg` for route names, events, queues, RPC methods, SQL, configuration keys,
dependency-injection tokens, templates, reflection, and generated registries.

## 6. Verify

Run the relevant compiler or type checker, linting, and focused tests. Compare
their results with the structural and textual inventory. Resolve discrepancies
from source evidence before reporting completion.
