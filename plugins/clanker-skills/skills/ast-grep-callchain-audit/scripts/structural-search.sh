#!/usr/bin/env bash
set -euo pipefail

if command -v ast-grep >/dev/null 2>&1; then
  ast_grep_bin="$(command -v ast-grep)"
elif command -v sg >/dev/null 2>&1; then
  ast_grep_bin="$(command -v sg)"
else
  echo "ast-grep is not installed. Install it with: brew install ast-grep" >&2
  exit 127
fi

if (($# < 2)); then
  echo "usage: $0 <language> <pattern> [path ...]" >&2
  echo "example: $0 ts 'api.post(\$PATH, \$BODY)' frontend/src" >&2
  exit 2
fi

language="$1"
pattern="$2"
shift 2

if (($# == 0)); then
  set -- .
fi

exec "$ast_grep_bin" run --lang "$language" --pattern "$pattern" "$@"
