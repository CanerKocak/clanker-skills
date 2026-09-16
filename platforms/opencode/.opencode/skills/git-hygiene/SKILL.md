---
name: git-hygiene
description: >
  Keep git history and review prose human-readable. Use when committing,
  branching, rewriting history, or writing issues and pull requests; when
  prose reads like agent slop; or when a host name leaks into durable text.
---

# Git hygiene

Git tracks history. A host only publishes it. Write every durable word so it
still makes sense if the host changes: branches, remotes, and reviews are
git concepts, and no host name belongs in commits, issues, or lasting docs.

## Commits

One idea per commit. Start the message with a verb and say what changes:

```sh
git commit -m "Shorten the retry backoff to five seconds"
```

Add a body only when the why is not obvious from the diff. Never record the
conversation: no mention of who asked, which agent ran, or what turn this
was. Read the message as a stranger: it should explain the change, not the
chat that produced it.

## Branches and history

Tidy private branches freely and leave published ones alone. Never rewrite a
branch someone else may have pulled. Rebase to keep your own work readable;
merge to record that two lines of work joined. Force-push only to a branch
you own, and say so when you do.

## Issues and pull requests

Write each one as an engineering task in plain words, not as a filled-in
form. Fixed sections (problem, acceptance, non-goals) turn every report into
the same grey text and teach readers to skim. Instead, say what is happening,
what should change, and what done looks like, in whatever shape fits the
thought. One issue holds one idea; a second idea gets its own issue.

Point at evidence a stranger can open: file paths, commands, measured
numbers with their conditions. Never link a private chat or paste a
transcript and call it context. If the reader needs the chat to understand
the issue, the issue is unfinished.

## Simple English

Short sentences. Common words. No jargon without an explanation on first
use. If a sentence needs a second reading, rewrite it before anyone else
has to.
