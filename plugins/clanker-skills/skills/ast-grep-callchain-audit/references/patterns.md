# ast-grep patterns for call-chain audits

Use these as starting points. Adjust the language, syntax, and paths to the
repository. Always validate a match in source before calling it a finding.

## Definitions and calls

```bash
ast-grep run --pattern 'function $F($$$PARAMS) { $$$BODY }' --lang ts src
ast-grep run --pattern 'const $F = ($$$PARAMS) => $$$BODY' --lang ts src
ast-grep run --pattern '$F($$$ARGS)' --lang ts src
ast-grep run --pattern '$OBJ.$METHOD($$$ARGS)' --lang ts src
ast-grep run --pattern 'new $C($$$ARGS)' --lang ts src
```

For methods, include the surrounding class or use a narrower method pattern.
For TypeScript JSX, use `--lang tsx`. For JavaScript, use `--lang js` or
`--lang jsx`.

## Imports, exports, and wrappers

```bash
ast-grep run --pattern 'import { $$$NAMES } from $SOURCE' --lang ts src
ast-grep run --pattern 'export { $$$NAMES } from $SOURCE' --lang ts src
ast-grep run --pattern 'export function $F($$$PARAMS) { $$$BODY }' --lang ts src
ast-grep run --pattern 'return $F($$$ARGS)' --lang ts src
```

Pair these searches with `rg` for route tables, event names, dependency
injection, configuration, templates, and generated files.

## Wrong-helper and rail variants

Search the call shape first, then compare the argument that carries the rail,
network, unit, or authorization context:

```bash
ast-grep run --pattern 'get$HELPER($$$ARGS)' --lang ts frontend backend
ast-grep run --pattern '$OBJ.$HELPER($NETWORK, $$$ARGS)' --lang ts frontend backend
ast-grep run --pattern 'open($URL)' --lang ts frontend/src
```

Use literal searches for canonical names such as `getEtherscanTxUrl`,
`getTronscanTxUrl`, and `getSolscanTxUrl`, then verify every consumer.

## Dead-parameter triage

AST search can locate candidate definitions, but it cannot prove liveness by
itself. For each candidate:

1. inspect the body for reads and forwarding;
2. search all call sites, exports, overrides, and callback assignments;
3. inspect type declarations and framework registration;
4. run the configured type checker and unused-variable rule;
5. report the evidence and proposed signature change for user approval.

## Useful output modes

```bash
ast-grep run --pattern '$F($$$ARGS)' --lang ts --files-with-matches src
ast-grep run --pattern '$F($$$ARGS)' --lang ts --json=stream src
ast-grep run --pattern '$F($$$ARGS)' --lang ts --inspect summary src
```

`--files-with-matches` is a file inventory, not a call count. `--json=stream`
is useful for preserving match locations. Neither mode covers dynamic calls.
