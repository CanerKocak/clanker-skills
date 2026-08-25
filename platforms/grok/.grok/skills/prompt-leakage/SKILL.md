---
name: prompt-leakage
description: >
  Strip transcript residue from comments, READMEs, and commit bodies. Use when
  writing comments, reviewing your own diff, the user says slop / leakage /
  prompt leakage, or before push. Always-on for any comment you are about to add.
---

# Prompt leakage

A comment or README aside is **transcript residue** when it exists so a model
(or the current chat) can remember *why we decided this*, not so a stranger
can run the code.

Different from ceremonial *code* (yagni-anti-ceremonial) and generic extra
comments (deslop).

## Test

Delete the line if any of these is true:

1. **Chat-motive** — names a user request, slash command, or "so Codex gets X".
2. **Restatement** — the next line's identifiers already say it.
3. **Theater** — parenthetical written to justify the change to the previous turn.

Keep it only if a stranger cannot recover the fact from names, types, or the
next line.

## Delete these

Chat-motive:

```sh
# Added because the reviewer asked for a defensive fallback.
run_with_fallback
```

The comment records the conversation, not a runtime fact.

Theater:

```md
- Retry through the legacy path. (This satisfies the original request.)
```

Restatement:

```sh
# Increment the retry count.
retry_count=$((retry_count + 1))
```

## Keep these

```md
The folder is named `agent-skills` because a global gitignore drops any `agents/` directory.
```

```sh
# fee_limit caps Energy burn. It is not ETH gas and does not pay bandwidth.
```

A stranger cannot get those facts from the identifiers alone.

## Do not

- Narrate ("now we link Codex so the two skills resolve").
- Paste the last message's acceptance criterion into a comment.
- Treat a comment you just wrote as documentation when you review your own diff.

## When reviewing

List each leftover line. Classify: `chat-motive` | `restatement` | `theater`.
Delete. Do not rewrite it longer.
