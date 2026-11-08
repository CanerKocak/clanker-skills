# Context manager for Claude Code

Context manager lets Claude see how full its context window is. It also lets
Claude compact the conversation at a point it chooses. Without it, Claude Code
compacts only when the limit forces it, which can happen in the middle of a
task.

This plugin works in Claude Code only. Codex and DeepSeek Harness do not load
it.

## What it adds

For each prompt you send, except slash commands, the plugin adds one line that
states the context use:

~~~text
[context-manager] Context in use: ~124k tokens of a 450k compaction window (28%); auto-compaction fires near 417k.
~~~

The compaction window is the size that automatic compaction measures against.
Once the context reaches the start point described below, the line also tells
Claude that it can compact.

The plugin also gives Claude two tools:

| Tool | What it does | Input |
| --- | --- | --- |
| `context_status` | Reports the tokens in use, the compaction window, and where automatic compaction starts. Also reports whether Claude may compact now, any queued compaction, the last result, and the path of the full transcript. Changes nothing. | None |
| `compact_context` | Queues a compaction for the end of the current turn. | `keep` (required, at most 4,000 characters): what the summary must preserve.<br>`next_step` (optional, at most 2,000 characters): what Claude does right after. |

## How a self-compaction runs

1. Claude calls `compact_context` with `keep` and, to continue afterward,
   `next_step`.
2. The plugin queues the request and tells Claude to end its turn.
3. When the turn ends, the plugin runs the built-in `/compact` command. It
   passes `keep` to the summarizer as instructions.
4. If Claude gave `next_step`, the plugin starts a new turn with that
   instruction. The new turn also names the file that holds the full
   transcript. Without `next_step`, the session waits for you.

The plugin shows a short notice at each stage. After the first response that
follows a compaction, it reports the new context size.

## When Claude may compact

Claude cannot compact at any time. The plugin refuses a request until the
context reaches a start point.

The start point is the lowest context size reported since the last compaction,
plus a quarter of the compaction window. It never exceeds half of the window.
If the plugin cannot read the window, it counts a quarter as 100k tokens. For
example, with a 450k window and a lowest size of 95k, Claude may compact from
about 208k tokens.

| Case | Result |
| --- | --- |
| The context is below the start point. | The call is refused. The reply gives the current numbers. |
| No response has arrived since the last compaction. | The call is refused until one arrives. |
| A subagent makes the call. | The call is refused. Only the main conversation can compact itself. |
| A compaction is already queued. | The call is refused. |
| `keep` is empty or too long, or `next_step` is too long. | The call is refused. |
| The turn ends in any way except a normal answer, such as an interruption. | The queued compaction is cancelled. |
| You send a prompt before the compaction starts. | The queued compaction is cancelled. Your prompt runs first. |
| `/compact` fails or compacts nothing. | The plugin reports it. No new turn starts. |

## Prompt cache

After the session starts, the plugin does not change the system prompt, the
tool list, or earlier messages. It adds its line to each new prompt. The
summary request is the built-in `/compact` request, so the API can serve the
conversation from the prompt cache.

One measured compaction, with Claude Code 2.1.317 in the Claude desktop app:

| Measure | Value |
| --- | --- |
| Context before the compaction | ~241k tokens |
| Context at the first response after it | ~95k tokens |
| Summary input read from the prompt cache | ~241k tokens |
| Summary input written to the prompt cache | under 1k tokens |
| Summary input sent uncached | ~4k tokens |

This is one measurement. Results vary with the conversation and with cache
timing.

## Install

Add the marketplace, then install the plugin:

~~~bash
claude plugin marketplace add CanerKocak/clanker-skills
claude plugin install context-manager@clanker-skills
~~~

In a Claude Code terminal session, one line does both:

~~~text
/plugin install context-manager --marketplace CanerKocak/clanker-skills
~~~

Answer `y` when Claude Code asks to add the marketplace, then choose a scope.
In the Claude desktop app, click + next to the prompt box, choose Plugins, add
the marketplace `CanerKocak/clanker-skills`, then add the plugin. Start a new
Claude Code session after installation.

To update:

~~~bash
claude plugin marketplace update clanker-skills
claude plugin update context-manager@clanker-skills
~~~

## Settings

The plugin has no settings of its own. It reads the compaction window that
Claude Code uses. To change that window, set `CLAUDE_CODE_AUTO_COMPACT_WINDOW`
in the `env` block of `~/.claude/settings.json`:

~~~json
{
  "env": { "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "450000" }
}
~~~

## Boundaries

| Boundary | Detail |
| --- | --- |
| Host | Claude Code only. |
| Version | Built and tested with Claude Code 2.1.317. Other versions are untested. |
| Tested | 16 unit tests, and one live compaction in the Claude desktop app. A terminal session is untested. |
| Timing | A compaction runs after the turn ends, never during it. |
| Summary | Claude Code writes the summary. `keep` guides it, but the summary can still drop a detail. The full transcript stays on disk at `~/.claude/projects/*/<session id>.jsonl`. |
| Scope | Only the main conversation can compact itself. A subagent cannot. |

## Develop

Run both checks from the repository root:

~~~bash
claude plugin validate plugins/context-manager
claude plugin test plugins/context-manager
~~~

The 16 tests cover registration, the start point, queuing, cancellation, the
resume prompt, subagents, the size report, and the usage line.
`types/index.d.ts` declares the session state that the plugin keeps: `pending`,
`last`, and `baseline`.

## Licensing

Licensing follows the repository. See
[Provenance and licensing](../../README.md#provenance-and-licensing).
