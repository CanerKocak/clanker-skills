/** A self-compaction the model asked for, waiting for its turn to end. */
export type PendingCompaction = {
  /** What the summary must preserve, passed to the summarizer. */
  keep: string
  /** The instruction the next turn starts with; null to wait for the user. */
  nextStep: string | null
  requestedAt: number
  tokensAtRequest: number | null
}

/** The input side of the summary request, as the API counted it. */
export type SummaryUsage = {
  /** Served by the prompt cache: the conversation's cached prefix, reused. */
  cacheRead: number
  /** Written to the prompt cache by the request. */
  cacheWrite: number
  /** Neither read from nor written to the cache. */
  uncached: number
}

/** How the last self-compaction ended. */
export type CompactionRecord = {
  at: number
  outcome: 'compacted' | 'skipped' | 'cancelled' | 'failed'
  tokensBefore: number | null
  /**
   * The context on the first response after the compaction: system prompt, tools,
   * summary and all. Null until then, and for good when another compaction came first.
   */
  tokensAfter: number | null
  /** Null when the engine made no summary request or reported no usage. */
  summaryUsage: SummaryUsage | null
  detail: string | null
}

/** The context's lowest reading since the last compaction: the next self-compaction counts from it. */
export type Baseline = {
  /** Null from a compaction until the first response after it. */
  tokens: number | null
  /** True while the last compaction was this mod's own and its record waits for its size after. */
  isAwaitingRecord: boolean
}

declare module 'claude-code' {
  interface PluginState {
    'context-manager': {
      pending: PendingCompaction | null
      last: CompactionRecord | null
      baseline: Baseline
    }
  }
}
