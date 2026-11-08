import type { On, SessionMessage, SessionUsage } from 'claude-code'
import { expect, mock, test } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'

const COMPACT = 'mcp__context-manager__compact_context'
const STATUS = 'mcp__context-manager__context_status'

type World = {
  /** The last response's input tokens: none from a compaction until the next response. */
  tokens: number | undefined
  registered: string[]
  commands: { command: string; args: string }[]
  compactions: { trigger: string; instructions: string }[]
  /** Set: /compact runs, but the engine compacts nothing, for this reason. */
  skipWith: string | undefined
  /** True: the host refuses to run /compact at all. */
  refusesCommand: boolean
  submitted: { text: string; context: readonly string[] }[]
  toasts: string[]
}

// A 1M-token model with a 450k compaction window, as CLAUDE_CODE_AUTO_COMPACT_WINDOW=450000 sets it.
function usageAt(tokens: number | undefined): SessionUsage {
  // The local estimate stands in for the breakdown's total while no response has come back.
  const total = tokens ?? 35_000

  return {
    startedAt: 0,
    context: {
      tokens,
      window: 1_000_000,
      percent: tokens === undefined ? undefined : Math.round(tokens / 10_000),
      breakdown: {
        rawMaxTokens: 450_000,
        maxTokens: 450_000,
        autoCompactThreshold: 418_500,
        isAutoCompactEnabled: true,
        totalTokens: total,
        percentage: Math.round((total / 450_000) * 100),
      },
    },
    rateLimits: [],
  } as unknown as SessionUsage
}

// The conversation as the engine hands it to a compaction, and what one leaves.
const row: SessionMessage = { role: 'user', text: 'Work on the parser.', toolUses: [] }
const summary: SessionMessage = { role: 'user', text: 'Summary of the conversation so far.', toolUses: [] }

// Nothing sits beneath the plugin in a test: these hooks stand for the engine.
function world($: Engine, on: On, tokens: number): World {
  const w: World = {
    tokens,
    registered: [],
    commands: [],
    compactions: [],
    skipWith: undefined,
    refusesCommand: false,
    submitted: [],
    toasts: [],
  }
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('tool.register', (_, e) => {
    w.registered.push(e.name)
    return { value: { tool: `mcp__context-manager__${e.name}` } }
  })
  // Any tool the mod does not answer itself, as core runs it.
  on('tool.call', () => ({ result: 'ok' }))
  on('session.id', () => ({ value: 'session-1' }))
  on('session.usage', () => ({ value: usageAt(w.tokens) }))
  on('ui.toast', (_, e) => {
    w.toasts.push(e.text)
    return { value: undefined }
  })
  // The engine's /compact: one compaction of the main conversation, raised as core raises it.
  on('command.run', async (_, e) => {
    w.commands.push({ command: e.command, args: e.args })
    if (w.refusesCommand) throw new Error('this host cannot run /compact')
    const result = await $.session.compact({ trigger: 'manual', instructions: e.args, messages: [row] })

    return { text: result.skip ?? 'Compacted' }
  })
  on('session.compact', (_, e) => {
    w.compactions.push({ trigger: e.trigger, instructions: e.instructions ?? '' })
    if (w.skipWith !== undefined) return { skip: w.skipWith }

    const before = w.tokens
    w.tokens = undefined
    // The result is the transcript afterwards, so it holds at least the summary. Its
    // 40k counts the rebuilt history alone, as core's does. The summary request
    // reused the cached conversation: 297.5k of its 300k input.
    return {
      messages: [summary],
      tokensBefore: before,
      tokensAfter: 40_000,
      usage: {
        input_tokens: 1_500,
        output_tokens: 2_000,
        cache_creation_input_tokens: 1_000,
        cache_read_input_tokens: 297_500,
      },
    }
  })
  on('prompt.submit', (_, e) => {
    w.submitted.push({ text: e.text, context: e.context ?? [] })
    return { text: e.text }
  })
  on('turn.start', (_, e) => ({ turnId: e.turnId }))
  on('turn.complete', (_, e) => ({ text: e.answer }))

  return w
}

const start = ($: Engine) => $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

// A prompt typed into the composer, as the engine raises one.
const typed = (text: string) => ({ text, wait: false, origin: { kind: 'composer' } }) as const

const endTurn = {
  answer: 'Done with this chunk.',
  durationMs: 1,
  isAborted: false,
  turnId: 'turn-1',
  reason: 'answer',
} as const

test('both tools are registered at session start', async ($, on) => {
  const w = world($, on, 50_000)
  mock.clock(on)
  await start($)

  expect(w.registered).toEqual(['context_status', 'compact_context'])
})

test('a small context is refused and nothing is queued', async ($, on) => {
  const w = world($, on, 60_000)
  const clock = mock.clock(on)
  await start($)

  const ran = await $.tool.call({ tool: COMPACT, keep: 'the plan' })
  expect(JSON.stringify(ran)).toMatch(/Not worth compacting yet: ~60k tokens in use/)
  // A quarter of the 450k window past the lowest reading so far, the session's start.
  expect(JSON.stringify(ran)).toMatch(/starts at ~173k/)

  await $.turn.complete(endTurn)
  await clock.advance(10_000)
  expect(w.commands).toEqual([])
})

test('a queued compaction runs /compact when the turn ends, then resumes with next_step', async ($, on) => {
  const w = world($, on, 300_000)
  const clock = mock.clock(on)
  await start($)

  const ran = await $.tool.call({
    tool: COMPACT,
    keep: 'goal X; edited a.ts and b.ts',
    next_step: 'write the tests for b.ts',
  })
  expect(JSON.stringify(ran)).toMatch(/Queued/)
  expect(w.commands).toEqual([])

  await $.turn.complete(endTurn)
  await clock.advance(1_000)

  expect(w.commands).toHaveLength(1)
  expect(w.commands[0]?.command).toBe('compact')
  expect(w.commands[0]?.args).toMatch(/Preserve, with specifics: goal X; edited a\.ts and b\.ts/)
  // The engine's compaction reaches core as the command raised it: nothing rewritten.
  expect(w.compactions).toEqual([{ trigger: 'manual', instructions: w.commands[0]?.args ?? '' }])
  expect(w.submitted).toHaveLength(1)
  expect(w.submitted[0]?.text).toMatch(/compacted at your request, from ~300k tokens\./)
  expect(w.submitted[0]?.text).toMatch(/Continue with: write the tests for b\.ts/)
  expect(w.submitted[0]?.text).toMatch(/\*\/session-1\.jsonl/)
  // Nothing is read on the fresh window yet, so the resumed turn is not nudged to compact again.
  expect(w.submitted[0]?.context.join('\n')).not.toMatch(/compact_context/)
  expect(w.toasts).toContain('Context compacted from ~300k tokens (summary input 99% from cache)')
})

test('without next_step it compacts and waits for the user', async ($, on) => {
  const w = world($, on, 300_000)
  const clock = mock.clock(on)
  await start($)

  await $.tool.call({ tool: COMPACT, keep: 'the plan' })
  await $.turn.complete(endTurn)
  await clock.advance(1_000)

  expect(w.compactions).toHaveLength(1)
  expect(w.submitted).toEqual([])
})

test('a /compact that compacts nothing is reported as skipped, with no resume', async ($, on) => {
  const w = world($, on, 300_000)
  w.skipWith = 'Not enough messages to compact.'
  const clock = mock.clock(on)
  await start($)

  await $.tool.call({ tool: COMPACT, keep: 'k', next_step: 'n' })
  await $.turn.complete(endTurn)
  await clock.advance(1_000)

  expect(w.submitted).toEqual([])
  expect(w.toasts).toContain('Self-compaction skipped: Not enough messages to compact.')
  const text = JSON.stringify(await $.tool.call({ tool: STATUS }))
  expect(text).toMatch(/Last self-compaction: skipped at [^(]*\(Not enough messages to compact\.\)/)
  expect(text).toMatch(/Queued: nothing\./)
})

test('a host that refuses /compact is reported once, not retried', async ($, on) => {
  const w = world($, on, 300_000)
  w.refusesCommand = true
  const clock = mock.clock(on)
  await start($)

  await $.tool.call({ tool: COMPACT, keep: 'k', next_step: 'n' })
  await $.turn.complete(endTurn)
  await clock.advance(10_000)

  expect(w.commands).toHaveLength(1)
  expect(w.submitted).toEqual([])
  expect(w.toasts.some(toast => toast.startsWith('Self-compaction failed:'))).toBe(true)
})

test('context_status reports the size after and how much of the summary request the cache served', async ($, on) => {
  const w = world($, on, 300_000)
  const clock = mock.clock(on)
  await start($)

  await $.tool.call({ tool: COMPACT, keep: 'k' })
  await $.turn.complete(endTurn)
  await clock.advance(1_000)
  // The first response after: system prompt, tools, summary and what the engine attached back.
  w.tokens = 100_000
  const text = JSON.stringify(await $.tool.call({ tool: STATUS }))

  expect(text).toMatch(
    /Last self-compaction: compacted ~300k → ~100k tokens at [^;]*; the summary request read ~298k tokens from the prompt cache, wrote ~1k and sent ~2k uncached/,
  )
})

test('after a self-compaction the floor counts from what it left', async ($, on) => {
  const w = world($, on, 300_000)
  const clock = mock.clock(on)
  await start($)

  await $.tool.call({ tool: COMPACT, keep: 'k' })
  await $.turn.complete(endTurn)
  await clock.advance(1_000)
  // Any tool call reads the first response after, not the engine's history-only 40k.
  w.tokens = 100_000
  await $.tool.call({ tool: 'Read', file_path: '/a.ts' })
  expect(w.toasts).toContain('Context after compaction: ~300k → ~100k tokens')

  w.tokens = 127_000
  await $.prompt.submit(typed('next question'))
  expect(w.submitted.at(-1)?.context.join('\n')).not.toMatch(/compact_context/)
  const early = JSON.stringify(await $.tool.call({ tool: COMPACT, keep: 'k' }))
  expect(early).toMatch(
    /starts at ~213k \(a quarter of the compaction window past ~100k, the lowest reading since the last compaction\)/,
  )

  w.tokens = 220_000
  expect(JSON.stringify(await $.tool.call({ tool: COMPACT, keep: 'k' }))).toMatch(/Queued/)
})

test('a compaction the mod did not start passes through untouched and moves the floor', async ($, on) => {
  const w = world($, on, 300_000)
  mock.clock(on)
  await start($)

  const result = await $.session.compact({ trigger: 'manual', instructions: 'mine', messages: [row] })
  expect(result.skip).toBeUndefined()
  expect(w.compactions).toEqual([{ trigger: 'manual', instructions: 'mine' }])

  w.tokens = 100_000
  const text = JSON.stringify(await $.tool.call({ tool: STATUS }))
  expect(text).toMatch(/allowed from ~213k tokens/)
  expect(text).not.toMatch(/Last self-compaction/)
  expect(w.toasts).toEqual([])
})

test('a new turn starting first cancels the request', async ($, on) => {
  const w = world($, on, 300_000)
  const clock = mock.clock(on)
  await start($)

  await $.tool.call({ tool: COMPACT, keep: 'k', next_step: 'n' })
  await $.turn.complete(endTurn)
  await $.turn.start({ text: 'one more question', turnId: 'turn-2' })
  await clock.advance(10_000)

  expect(w.commands).toEqual([])
  expect(w.submitted).toEqual([])
  expect(w.toasts).toContain('Self-compaction cancelled: a new turn started first')
})

test('an interrupted turn cancels the request', async ($, on) => {
  const w = world($, on, 300_000)
  const clock = mock.clock(on)
  await start($)

  await $.tool.call({ tool: COMPACT, keep: 'k', next_step: 'n' })
  await $.turn.complete({ ...endTurn, isAborted: true, reason: 'aborted' })
  await clock.advance(10_000)

  expect(w.commands).toEqual([])
  expect(w.toasts).toContain('Self-compaction cancelled: the turn did not finish normally')
})

test('a second request in the same turn is refused', async ($, on) => {
  world($, on, 300_000)
  mock.clock(on)
  await start($)

  await $.tool.call({ tool: COMPACT, keep: 'k' })
  const again = await $.tool.call({ tool: COMPACT, keep: 'k' })

  expect(JSON.stringify(again)).toMatch(/already queued/)
})

test('a subagent cannot compact the main conversation', async ($, on) => {
  world($, on, 300_000)
  mock.clock(on)
  await start($)

  const ran = await $.tool.call({ tool: COMPACT, keep: 'k', agentId: 'agent-1' })

  expect(JSON.stringify(ran)).toMatch(/Only the main conversation/)
})

test('each prompt carries the usage note, with the nudge once compaction is allowed', async ($, on) => {
  const w = world($, on, 300_000)
  mock.clock(on)
  await start($)

  await $.prompt.submit(typed('hello'))
  const note = w.submitted[0]?.context.join('\n') ?? ''

  expect(note).toMatch(
    /Context in use: ~300k tokens of a 450k compaction window \(67%\); auto-compaction fires near 419k\./,
  )
  expect(note).toMatch(/mcp__context-manager__compact_context \(load it with ToolSearch first\)/)
})

test('a small context gets the numbers without the nudge', async ($, on) => {
  const w = world($, on, 60_000)
  mock.clock(on)
  await start($)

  await $.prompt.submit(typed('hello'))
  const note = w.submitted[0]?.context.join('\n') ?? ''

  expect(note).toMatch(/Context in use: ~60k tokens/)
  expect(note).not.toMatch(/compact_context/)
})

test('context_status reports the window, the floor and the transcript', async ($, on) => {
  world($, on, 300_000)
  mock.clock(on)
  await start($)

  const text = JSON.stringify(await $.tool.call({ tool: STATUS }))

  expect(text).toMatch(/Context in use: ~300k tokens\./)
  expect(text).toMatch(/Compaction window: 450k \(auto-compaction fires near 419k\)/)
  // First read at 300k, past what any compaction leaves: half the window caps the floor.
  expect(text).toMatch(/allowed from ~225k tokens \(half the compaction window, the latest it starts\): allowed now/)
  expect(text).toMatch(/Queued: nothing\./)
  expect(text).toMatch(/\*\/session-1\.jsonl/)
})
