import type {
  EngineInterface,
  ModelUsage,
  Register,
  SessionCompactResult,
  Timer,
} from 'claude-code'

import type { Baseline, CompactionRecord, PendingCompaction, SummaryUsage } from '../types'

const COMPACT_TOOL = 'mcp__context-manager__compact_context'
const STATUS_TOOL = 'mcp__context-manager__context_status'

// A self-compaction is worth its summary once the context has grown a quarter of
// the compaction window past its lowest reading since the last compaction: what
// no compaction removes (system prompt, tools) and what that one left.
const MIN_SHARE = 0.25
// A quarter of the compaction window, when that window cannot be read.
const QUARTER_FALLBACK = 100_000
const MAX_KEEP_CHARS = 4_000
const MAX_NEXT_STEP_CHARS = 2_000
// The compaction starts from a timer, outside the turn.complete hook that
// `$.command.run` refuses to run inside; a prompt the person queued meanwhile
// starts first and wins.
const RUN_DELAY_MS = 300
// The compaction window only moves with settings, so it is re-read now and then.
const WINDOW_TTL_MS = 5 * 60_000

const pending = { plugin: 'context-manager', key: 'pending' } as const
const last = { plugin: 'context-manager', key: 'last' } as const
const baseline = { plugin: 'context-manager', key: 'baseline' } as const

const UNMEASURED: Baseline = { tokens: null, isAwaitingRecord: false }

const STATUS_DESCRIPTION =
  "Report how full this conversation's context window is: tokens in use, the compaction " +
  'window and where auto-compaction fires, whether self-compaction is allowed yet, any ' +
  'queued self-compaction, and where the full transcript is on disk. Cheap and read-only; ' +
  'call it before starting a large chunk of work.'

const COMPACT_DESCRIPTION = [
  'Compact this conversation yourself, at a boundary you choose, instead of waiting for',
  'auto-compaction to cut in at an arbitrary point. Use it when one chunk of work is done and',
  'the next is about to start, and most of the current context (old tool output, finished',
  'sub-tasks, dead ends) is no longer needed. It runs when your current turn ends, not',
  'immediately: after calling it, close the turn in a sentence and start no new work. With',
  'next_step, a new turn then starts automatically with that instruction; without it, the',
  'session waits for the user. The full transcript stays on disk and the resume message says',
  'where, so details the summary drops can be searched for. Refused until the context has',
  'grown a quarter of the compaction window past its lowest point since the last compaction',
  '(from half the window at the latest), from a subagent, or while one is already queued.',
].join(' ')

const COMPACT_SCHEMA = {
  type: 'object',
  properties: {
    keep: {
      type: 'string',
      description:
        'What the summary must preserve, specifically: the goal, decisions and their reasons, ' +
        'files and commands that matter, open questions, and where the work stands. Passed to ' +
        'the summarizer as its instructions.',
    },
    next_step: {
      type: 'string',
      description:
        'Optional. The instruction to continue with right after compacting, written to ' +
        'yourself (e.g. "Implement the parser change in src/parse.ts as planned"). Omit it to ' +
        'stop and wait for the user instead.',
    },
  },
  required: ['keep'],
  additionalProperties: false,
}

type Status = {
  /** Input tokens of the last response, or the local estimate before there is one. */
  tokens: number | undefined
  isEstimate: boolean
  /** The lowest reading since the last compaction; null until the first response after it. */
  settled: number | null
  /** The model's own window. */
  modelWindow: number
  /** The window auto-compaction measures against (CLAUDE_CODE_AUTO_COMPACT_WINDOW and kin). */
  compactWindow: number | undefined
  threshold: number | undefined
  isAutoCompactOn: boolean | undefined
}

/** Where self-compaction starts, and the rule that put it there. */
type Floor = { tokens: number; why: string }

type WindowReading = {
  at: number
  compactWindow: number
  threshold: number | undefined
  isAutoCompactOn: boolean
}

/** A settled outcome; the token fields default to what the request recorded. */
type Outcome = Pick<CompactionRecord, 'outcome' | 'detail'> &
  Partial<Pick<CompactionRecord, 'tokensBefore' | 'summaryUsage'>>

// Module variables start over on a hot reload; what must survive one is in $.state.
let windowReading: WindowReading | undefined
let timer: Timer | undefined
// True while this mod's own /compact runs, when the session.compact hook keeps
// the engine's result in `observed` for attempt() to read.
let isCompacting = false
let observed: SessionCompactResult | undefined
// False from a compaction (or a reload) until a reading lands; meanwhile every
// tool call takes one.
let isBaselineKnown = false
// Baseline writes go one at a time, so a self-compaction's size after is
// recorded once and a reading cannot undo a compaction's reset.
let baselineQueue: Promise<unknown> = Promise.resolve()

const kTokens = (n: number): string => `${Math.round(n / 1000)}k`
const share = (n: number, of: number): string => `${Math.round((n / of) * 100)}%`
const describe = (error: unknown): string =>
  error instanceof Error ? error.message : String(error)

function serially<T>(work: () => Promise<T>): Promise<T> {
  const run = baselineQueue.then(work)
  baselineQueue = run.catch(() => undefined)

  return run
}

/** Takes a reading of the live context; resolves the lowest since the last compaction. */
function observe($: EngineInterface, tokens: number): Promise<number> {
  return serially(async () => {
    const stored = (await $.state.get(baseline)).value ?? UNMEASURED
    if (stored.tokens === null || tokens < stored.tokens) {
      await $.state.set(baseline, { tokens, isAwaitingRecord: false })
      if (stored.isAwaitingRecord) await recordAfter($, tokens)
    }
    isBaselineKnown = true

    return Math.min(stored.tokens ?? tokens, tokens)
  })
}

/** The first response after a self-compaction shows what it left; the engine's own figure counts the history alone. */
async function recordAfter($: EngineInterface, tokens: number): Promise<void> {
  const record = (await $.state.get(last)).value ?? null
  if (record?.outcome !== 'compacted') return

  await $.state.set(last, { ...record, tokensAfter: tokens })
  $.ui.toast(
    record.tokensBefore === null
      ? `Context after compaction: ~${kTokens(tokens)} tokens`
      : `Context after compaction: ~${kTokens(record.tokensBefore)} → ~${kTokens(tokens)} tokens`,
  )
}

/** A reading where no status is wanted; there is none to take until a response comes back. */
async function measure($: EngineInterface): Promise<void> {
  const tokens = (await $.session.usage({})).context.tokens
  if (tokens !== undefined) await observe($, tokens)
}

async function readStatus($: EngineInterface, isFresh = false): Promise<Status> {
  const now = await $.clock.now()
  const isStale =
    isFresh || windowReading === undefined || now - windowReading.at > WINDOW_TTL_MS
  const usage = await $.session.usage(isStale ? { breakdown: 'summary' } : {})
  const breakdown = usage.context.breakdown
  if (breakdown !== undefined) {
    windowReading = {
      at: now,
      compactWindow: breakdown.rawMaxTokens,
      threshold: breakdown.autoCompactThreshold,
      isAutoCompactOn: breakdown.isAutoCompactEnabled,
    }
  }
  const reading = usage.context.tokens
  const tokens = reading ?? breakdown?.totalTokens

  return {
    tokens,
    isEstimate: reading === undefined && tokens !== undefined,
    // Only a response's reading counts toward the floor, never the local estimate.
    settled:
      reading === undefined
        ? ((await $.state.get(baseline)).value ?? UNMEASURED).tokens
        : await observe($, reading),
    modelWindow: usage.context.window,
    compactWindow: windowReading?.compactWindow,
    threshold: windowReading?.threshold,
    isAutoCompactOn: windowReading?.isAutoCompactOn,
  }
}

function floorOf(status: Status): Floor | undefined {
  const settled = status.settled
  if (settled === null) return undefined
  const quarter =
    status.compactWindow === undefined
      ? QUARTER_FALLBACK
      : Math.round(status.compactWindow * MIN_SHARE)
  // A lowest reading taken mid-conversation (after a restart, or a load past the
  // start) sits above what any compaction leaves; half the window caps the wait.
  if (settled + quarter >= 2 * quarter) {
    return { tokens: 2 * quarter, why: 'half the compaction window, the latest it starts' }
  }

  return {
    tokens: settled + quarter,
    why: `a quarter of the compaction window past ~${kTokens(settled)}, the lowest reading since the last compaction`,
  }
}

function usageNote(status: Status): string | undefined {
  if (status.tokens === undefined) return undefined
  let note = `[context-manager] Context in use: ~${kTokens(status.tokens)} tokens`
  if (status.compactWindow !== undefined) {
    note += ` of a ${kTokens(status.compactWindow)} compaction window (${share(status.tokens, status.compactWindow)})`
  }
  if (status.threshold !== undefined) {
    note += `; auto-compaction fires near ${kTokens(status.threshold)}`
  }
  note += '.'
  const floor = floorOf(status)
  if (floor !== undefined && status.tokens >= floor.tokens) {
    note +=
      ' At a boundary between chunks of work, when most of this context is no longer needed, ' +
      `you can compact on your own terms with ${COMPACT_TOOL} (load it with ToolSearch first).`
  }

  return note
}

const usageOf = (usage: ModelUsage): SummaryUsage => ({
  cacheRead: usage.cache_read_input_tokens,
  cacheWrite: usage.cache_creation_input_tokens,
  uncached: usage.input_tokens,
})

function cacheShare(usage: SummaryUsage): string | undefined {
  const input = usage.cacheRead + usage.cacheWrite + usage.uncached

  return input === 0 ? undefined : share(usage.cacheRead, input)
}

function compactedToast(before: number | undefined, usage: SummaryUsage | null): string {
  const cached = usage === null ? undefined : cacheShare(usage)

  return (
    `Context compacted${before === undefined ? '' : ` from ~${kTokens(before)} tokens`}` +
    (cached === undefined ? '' : ` (summary input ${cached} from cache)`)
  )
}

function recordText(record: CompactionRecord): string {
  const when = new Date(record.at).toISOString()
  if (record.outcome === 'compacted') {
    const size =
      record.tokensBefore === null
        ? ''
        : record.tokensAfter === null
          ? ` from ~${kTokens(record.tokensBefore)} tokens (size after not measured)`
          : ` ~${kTokens(record.tokensBefore)} → ~${kTokens(record.tokensAfter)} tokens`
    // A record an earlier version of this mod kept has no summaryUsage field.
    const usage = record.summaryUsage ?? null
    const cache =
      usage === null
        ? ''
        : `; the summary request read ~${kTokens(usage.cacheRead)} tokens from the prompt cache, ` +
          `wrote ~${kTokens(usage.cacheWrite)} and sent ~${kTokens(usage.uncached)} uncached`
    return `compacted${size} at ${when}${cache}`
  }

  return `${record.outcome} at ${when}${record.detail === null ? '' : ` (${record.detail})`}`
}

function statusText(
  status: Status,
  queued: PendingCompaction | null,
  done: CompactionRecord | null,
  sessionId: string,
): string {
  const lines = [
    status.tokens === undefined
      ? 'Context in use: unknown until the next model response.'
      : `Context in use: ~${kTokens(status.tokens)} tokens${status.isEstimate ? ' (local estimate)' : ''}.`,
  ]
  if (status.compactWindow === undefined) {
    lines.push(`Model window: ${kTokens(status.modelWindow)}; compaction window unknown.`)
  } else {
    const fires =
      status.isAutoCompactOn === false
        ? 'auto-compaction is off'
        : status.threshold === undefined
          ? 'auto-compaction is on'
          : `auto-compaction fires near ${kTokens(status.threshold)}`
    lines.push(
      `Compaction window: ${kTokens(status.compactWindow)} (${fires}); the model's own window is ${kTokens(status.modelWindow)}.`,
    )
  }
  const floor = floorOf(status)
  if (floor === undefined) {
    lines.push(
      'Self-compaction: not yet; what the last compaction left is read on the next response.',
    )
  } else {
    const isAllowed = status.tokens !== undefined && status.tokens >= floor.tokens
    lines.push(
      `Self-compaction is allowed from ~${kTokens(floor.tokens)} tokens (${floor.why}): ${isAllowed ? 'allowed now' : 'not yet'}.`,
    )
  }
  lines.push(
    queued === null
      ? 'Queued: nothing.'
      : `Queued: a compaction at the end of this turn${queued.nextStep === null ? '' : `, then: ${queued.nextStep}`}.`,
  )
  if (done !== null) lines.push(`Last self-compaction: ${recordText(done)}.`)
  lines.push(
    `Full transcript, including what compaction removed: ~/.claude/projects/*/${sessionId}.jsonl`,
  )

  return lines.join('\n')
}

function instructionsFor(request: PendingCompaction): string {
  const lines = [
    'The agent asked for this compaction itself, at a boundary between chunks of work.',
    `Preserve, with specifics: ${request.keep}`,
  ]
  if (request.nextStep !== null) {
    lines.push(`Right after it the agent continues with: ${request.nextStep}`)
  }

  return lines.join('\n')
}

function resumeText(nextStep: string, sessionId: string, before: number | undefined): string {
  const size = before === undefined ? '' : `, from ~${kTokens(before)} tokens`

  return [
    `The conversation was compacted at your request${size}. Continue with: ${nextStep}`,
    '',
    `Everything from before the compaction is still on disk at ~/.claude/projects/*/${sessionId}.jsonl ` +
      '(one JSON object per line). If the summary lacks a detail you need, search that file ' +
      'instead of guessing.',
  ].join('\n')
}

async function queuedRequest($: EngineInterface): Promise<PendingCompaction | null> {
  return (await $.state.get(pending)).value ?? null
}

async function settle(
  $: EngineInterface,
  request: PendingCompaction,
  outcome: Outcome,
): Promise<void> {
  await $.state.set(pending, null)
  await $.state.set(last, {
    tokensBefore: request.tokensAtRequest,
    tokensAfter: null,
    summaryUsage: null,
    ...outcome,
    at: await $.clock.now(),
  })
}

function schedule($: EngineInterface): void {
  timer?.cancel()
  timer = $.clock.after(RUN_DELAY_MS, () => {
    attempt($).catch((error: unknown) => {
      $.ui.toast(`context-manager: ${describe(error)}`)
    })
  })
}

async function attempt($: EngineInterface): Promise<void> {
  if (isCompacting) return
  const request = await queuedRequest($)
  if (request === null) return

  let resume: string | undefined
  isCompacting = true
  observed = undefined
  try {
    resume = await compactFor($, request)
  } finally {
    isCompacting = false
    observed = undefined
  }
  // Submitted once the flag is down, so the turn it starts is an ordinary one.
  if (resume !== undefined) {
    await $.prompt.submit({ text: resume }).catch((error: unknown) => {
      $.ui.toast(`Compacted, but the next turn could not start: ${describe(error)}`)
    })
  }
}

/** Runs /compact for the request and settles it; resolves the resume prompt, if any. */
async function compactFor(
  $: EngineInterface,
  request: PendingCompaction,
): Promise<string | undefined> {
  // The engine's own /compact, as if typed: `$.session.compact` is not available
  // where a host runs the session (the desktop app, an SDK), and the command
  // waits for the session to be idle on its own.
  const ran = await $.command.run({ command: 'compact', args: instructionsFor(request) }).then(
    result => ({ isDone: true as const, result }),
    (error: unknown) => ({ isDone: false as const, error }),
  )
  if (!ran.isDone) {
    await settle($, request, { outcome: 'failed', detail: describe(ran.error) })
    $.ui.toast(`Self-compaction failed: ${describe(ran.error)}`)
    return undefined
  }
  const result = observed
  if (result === undefined || result.skip !== undefined) {
    const why = result?.skip ?? ran.result.text ?? '/compact compacted nothing'
    await settle($, request, { outcome: 'skipped', detail: why })
    $.ui.toast(`Self-compaction skipped: ${why}`)
    return undefined
  }

  // The size after waits for the first response's reading (recordAfter).
  const before = result.tokensBefore ?? request.tokensAtRequest ?? undefined
  const summaryUsage = result.usage === undefined ? null : usageOf(result.usage)
  await settle($, request, {
    outcome: 'compacted',
    tokensBefore: before ?? null,
    summaryUsage,
    detail: null,
  })
  $.ui.toast(compactedToast(before, summaryUsage))

  return request.nextStep === null
    ? undefined
    : resumeText(request.nextStep, await $.session.id(), before)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.tool.register({
      name: 'context_status',
      description: STATUS_DESCRIPTION,
      inputSchema: { type: 'object', properties: {}, additionalProperties: false },
    })
    await $.tool.register({
      name: 'compact_context',
      description: COMPACT_DESCRIPTION,
      inputSchema: COMPACT_SCHEMA,
    })
    // A request queued before a reload lost its timer with the old code.
    if ((await queuedRequest($)) !== null) schedule($)

    return next(e)
  })

  on('prompt.submit', async ($, e, next) => {
    if (e.command !== undefined || e.isMeta === true) return next(e)
    const note = usageNote(await readStatus($))

    return next(note === undefined ? e : { ...e, context: [...(e.context ?? []), note] })
  }).catch(($, e, next) => next(e))

  on('tool.call', { tool: STATUS_TOOL }, async $ => {
    const status = await readStatus($, true)
    const text = statusText(
      status,
      await queuedRequest($),
      (await $.state.get(last)).value ?? null,
      await $.session.id(),
    )

    return { result: text }
  }).catch(() => ({ deny: 'context-manager could not read the context window just now.' }))

  on('tool.call', { tool: COMPACT_TOOL }, async ($, e) => {
    const input = e as unknown as Record<string, unknown>
    if (typeof input.agentId === 'string') {
      return { deny: 'Only the main conversation can compact itself; a subagent cannot.' }
    }
    const keep = typeof input.keep === 'string' ? input.keep.trim() : ''
    if (keep === '') return { deny: 'Give `keep`: what the summary must preserve.' }
    if (keep.length > MAX_KEEP_CHARS) {
      return { deny: `\`keep\` is ${keep.length} characters; keep it under ${MAX_KEEP_CHARS}.` }
    }
    const nextStep = typeof input.next_step === 'string' ? input.next_step.trim() : ''
    if (nextStep.length > MAX_NEXT_STEP_CHARS) {
      return {
        deny: `\`next_step\` is ${nextStep.length} characters; keep it under ${MAX_NEXT_STEP_CHARS}.`,
      }
    }
    if ((await queuedRequest($)) !== null) {
      return { deny: 'A self-compaction is already queued for the end of this turn. Close the turn.' }
    }

    const status = await readStatus($, true)
    const floor = floorOf(status)
    if (status.tokens === undefined || floor === undefined) {
      return {
        deny:
          'Not worth compacting yet: the context has not been read since the last compaction. ' +
          'Keep working; auto-compaction still guards the limit.',
      }
    }
    if (status.tokens < floor.tokens) {
      return {
        deny:
          `Not worth compacting yet: ~${kTokens(status.tokens)} tokens in use, and self-compaction ` +
          `starts at ~${kTokens(floor.tokens)} (${floor.why}). Keep working; auto-compaction ` +
          'still guards the limit.',
      }
    }

    await $.state.set(pending, {
      keep,
      nextStep: nextStep === '' ? null : nextStep,
      requestedAt: await $.clock.now(),
      tokensAtRequest: status.tokens,
    })
    $.ui.toast('Context will be compacted when this turn ends')

    return {
      result:
        nextStep === ''
          ? 'Queued: the conversation is compacted when this turn ends, keeping what you listed; ' +
            'the session then waits for the user. Close this turn now with a one-line note for the ' +
            'user, and start no new work.'
          : 'Queued: the conversation is compacted when this turn ends, keeping what you listed; ' +
            'a new turn then starts with your next_step. Close this turn now in one line, and start ' +
            'no new work.',
    }
  }).catch(() => ({ deny: 'context-manager failed; nothing was queued.' }))

  // The first response after a compaction shows what it left, so every tool call
  // takes a reading until one lands, before the turn's own work adds to it.
  on('tool.call', async ($, e, next) => {
    if (!isBaselineKnown && e.agentId === undefined) await measure($)

    return next(e)
  }).catch(($, e, next) => next(e))

  // Watches the engine's compaction on the way up, its input passed on as
  // received, so the summary request is the engine's own, cache prefix and all.
  on('session.compact', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId !== undefined || e.trigger === 'precompute') return result
    const isOwn = isCompacting
    if (isOwn) observed = result
    // Any compaction of the main conversation moves the floor, this mod's or not:
    // the next one counts from what this one left.
    if (result.skip === undefined) {
      isBaselineKnown = false
      await serially(() => $.state.set(baseline, { tokens: null, isAwaitingRecord: isOwn }))
    }

    return result
  }).catch(($, e, next) => next(e))

  on('turn.complete', async ($, e, next) => {
    const done = await next(e)
    // Our own /compact can run as a turn of its own; attempt() settles that one.
    if (e.agentId !== undefined || isCompacting) return done
    const request = await queuedRequest($)
    if (request === null) return done

    if (e.reason !== 'answer') {
      timer?.cancel()
      await settle($, request, {
        outcome: 'cancelled',
        detail: `the turn ended with ${e.reason}`,
      })
      $.ui.toast('Self-compaction cancelled: the turn did not finish normally')
      return done
    }
    schedule($)

    return done
  }).catch(($, e, next) => next(e))

  // A prompt that starts a turn before the queued compaction ran wins: the
  // request was made for a moment that has passed.
  on('turn.start', async ($, e, next) => {
    if (e.agentId === undefined && !isCompacting) {
      const request = await queuedRequest($)
      if (request !== null) {
        timer?.cancel()
        await settle($, request, {
          outcome: 'cancelled',
          detail: 'a new turn started before it ran',
        })
        $.ui.toast('Self-compaction cancelled: a new turn started first')
      }
    }

    return next(e)
  }).catch(($, e, next) => next(e))
}
