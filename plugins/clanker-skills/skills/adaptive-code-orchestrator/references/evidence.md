# Evidence snapshot: adaptive agent orchestration

Research cutoff: 2026-08-20. This is a design evidence ledger, not a claim that
one architecture dominates every task. Many 2025–2026 results are preprints or
first-party reports; their limitations remain part of the evidence.

## Core findings

### Match the topology to the task

- [Capable language models can outgrow the benefits of collaboration](https://www.nature.com/articles/s42256-026-01268-y)
  evaluates 260 matched-compute configurations over six benchmarks, five
  architectures, and three model families. Mean multi-agent improvement was
  zero; relative performance ranged from +80.8% on decomposable financial
  reasoning to -70% on sequential planning. Every tested multi-agent topology
  was worse than the single-agent SWE-bench Verified baseline by 1.3–12.8%.
  Central verification contained error propagation better than independent
  aggregation. The authors' capability threshold is a useful selector, not a
  universal constant. This paper was published in Nature Machine Intelligence
  in July 2026.
- [Scaling LLM-Driven Multi-Agent Systems](https://arxiv.org/abs/2607.27942)
  reports that performance on terminal system-engineering tasks peaked at
  intermediate workflow complexity, then degraded with timeouts and consistency
  problems. Accuracy gains came with approximately linear cost and only above a
  model-capability floor. This is a July 2026 preprint with a narrow evaluation.
- [MultiAgentBench](https://aclanthology.org/2025.acl-long.421/) compares star,
  chain, tree, and graph coordination. Topology and model interacted with the
  scenario; no structure established universal dominance. Cognitive planning
  improved milestone achievement by 3% in that benchmark.

Design consequence: default to the simplest topology. Expand only for a task
property—independence, evidence volume, latency, or orthogonal risk—not because
more workers are available.

### Diversity beats homogeneous count

- [Understanding Agent Scaling via Diversity](https://arxiv.org/abs/2602.03794)
  finds strong diminishing returns for homogeneous agents and reports that two
  diverse agents can match or exceed sixteen homogeneous agents. Its tests use
  smaller open models and reasoning benchmarks rather than repository work.
- [Multi-Agent Teams Hold Experts Back](https://arxiv.org/abs/2602.01011)
  finds that unconstrained teams can average away known expertise, with losses
  up to 37.6%. The setting is equal-status team reasoning, but it directly warns
  against consensus-weighted integration.
- [The Cost of Consensus](https://arxiv.org/abs/2605.00914) reports high modal
  conformity and cases where debate discarded a correct initial minority
  answer. Its agents and tasks are narrower than coding systems.
- [Debate or Vote](https://arxiv.org/abs/2508.17536) finds that majority voting
  explains most measured gains attributed to multi-agent debate across seven
  NLP benchmarks; debate alone does not increase expected correctness without
  targeted corrective intervention.
- [More Agents Is All You Need](https://openreview.net/forum?id=bgzUSZ8aeg)
  reports large ensemble gains on static, independently sampled tasks, but cost
  grows roughly linearly and debate sometimes disrupted coherent code. These
  answer-votable benchmarks lack shared repository state and therefore do not
  contradict the coding regressions above.

Design consequence: vary hypotheses, evidence channels, models, tools, or
surfaces. Preserve minority findings and use executable evidence instead of a
vote.

### Communication and hierarchy need constraints

- [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657)
  derives 14 failure modes in system design, inter-agent alignment, and task
  verification from more than 1,600 traces across seven frameworks.
- [AgentPrune](https://arxiv.org/abs/2410.02506) removes redundant spatial and
  temporal communication edges while retaining comparable performance across
  six benchmarks, reducing tokens by 28.1–72.8%. Its learned pruning mechanism
  is not a direct coding-work recipe, but supports sparse communication.
- [Magentic-One](https://www.microsoft.com/en-us/research/publication/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/)
  uses an orchestrator with a stable task ledger and an iterative progress
  ledger over specialized agents. The system result does not isolate the causal
  contribution of its hierarchy.
- Anthropic's [AI Organizations](https://alignment.anthropic.com/2026/ai-organizations/)
  study finds that multi-agent organizations can improve task utility while
  losing system-level ethical constraints as specialists narrow onto delegated
  goals. The simulated organization setting is not a code benchmark, but it
  supports retaining security, money-flow, and architectural invariants at the
  lead level.

Design consequence: one lead owns contract, state, integration, and acceptance.
Workers return compact evidence deltas. Hierarchy must correspond to real
subtrees, not status relaying.

### Broad research benefits more than ordinary coding

- Anthropic's [multi-agent research system report](https://www.anthropic.com/engineering/multi-agent-research-system)
  reports a 90.2% internal improvement over a single lead model on a
  breadth-first research evaluation and up to 90% latency reduction from
  parallel search. It also reports about 15 times chat token usage and warns
  that coding usually has fewer parallelizable tasks. These are first-party,
  non-peer-reviewed measurements.
- Anthropic's [Automated Weak-to-Strong Researcher](https://alignment.anthropic.com/2026/automated-w2s-researcher/)
  uses parallel agents in isolated sandboxes with shared findings and objective
  evaluation. Directed, diverse research seeds outperformed identical prompts;
  the report also identifies entropy collapse. It is a costly, specialized
  research system rather than a general coding benchmark.

Design consequence: two to four sealed scouts are a sensible initial breadth
wave when independent domains exist. Larger waves require a genuinely broad
frontier, enough budget, and an objective evaluator.

### Allocate compute adaptively

- [Scaling LLM Test-Time Compute Optimally](https://openreview.net/forum?id=4FWAwZtd2n)
  finds difficulty-aware allocation more than four times as compute-efficient
  as a fixed best-of-N policy in its math setting. Easy coherent problems
  favored sequential refinement, medium and harder problems favored a mixture
  of parallel search and local refinement, and the hardest bin did not improve
  meaningfully under tested policies.
- [RMoA](https://aclanthology.org/2025.findings-acl.342/) reports that three
  agents gave its best accuracy/compute balance while four or five sometimes
  degraded results; adaptive residual-based stopping reduced compute. These are
  static reasoning tasks, not repository edits.

Design consequence: fixed breadth and fixed depth are both weak defaults. Add
compute only when the preceding step exposes a decision-changing proof gap.

## Software-engineering evidence

### Simplicity is a serious baseline

- [Agentless](https://arxiv.org/abs/2407.01489) uses a fixed localization,
  repair, and patch-validation pipeline and reported 32% on SWE-bench Lite at
  low cost, outperforming contemporary open-source agents in that evaluation.
- [SWE-agent](https://arxiv.org/abs/2405.15793) shows that an agent-computer
  interface for navigation, editing, and execution materially changes coding
  performance. Tool and runtime design can matter as much as organizational
  metaphor.
- [CodePlan](https://arxiv.org/abs/2309.12499) models repository edits as an
  adaptive dependency plan. On multi-file migration tasks its planning approach
  passed validity checks on five of six repositories while no-planning
  baselines passed none.

Design consequence: SOLO remains the burden-of-proof default; repository-scale
work should add dependency planning before adding workers.

### Breadth creates candidates; evidence must select them

- [MASAI](https://arxiv.org/abs/2406.11638) decomposes issue resolution into
  bounded roles. Its multiple-patch ablation increased oracle success, but the
  LLM selector could not reliably choose the correct patch. Options are not
  reliability without a good arbiter.
- [SWE-Search](https://arxiv.org/abs/2410.20285) reports gains from search depth,
  value estimation, and iterative refinement across several models. This
  supports selective depth for ambiguous valuable tasks, not mandatory search.
- [CAID](https://arxiv.org/abs/2603.21489) uses a central manager, dependency
  DAG, isolated workspaces, and test-gated integration. It reports gains over
  single-agent baselines on PaperBench and Commit0 while documenting the
  interference costs of shared concurrent edits. It is a 2026 preprint.

Design consequence: parallel reconnaissance may share a read-only tree;
parallel writers need isolated worktrees and topological integration.

### Context and review are fallible

- [Do AGENTS.md Files Help AI Coding Agents?](https://arxiv.org/abs/2602.11988)
  finds no significant success improvement from context files across its tested
  settings, with 20–23% more cost and steps; generated files reduced success in
  five of eight settings. Repository instructions should preserve concise,
  non-discoverable invariants rather than duplicate the codebase.
- [SWE-ContextBench](https://arxiv.org/abs/2602.08316) finds that correctly
  retrieved compact prior experience can improve accuracy and reduce cost,
  while unfiltered or wrong experience has limited or negative value.
- [c-CRAB](https://arxiv.org/abs/2603.23448) evaluates review agents against
  held-out executable tests and finds that tested agents collectively solved
  only about 40% of tasks. Review comments are hypotheses, not proof.
- [Adversarial Review](https://arxiv.org/abs/2608.18167) reports that a coder,
  reviewer, and critic-of-review topology beat larger baselines on its coding
  and review evaluations when disagreement had to cite evidence. It is a very
  recent August 2026 preprint, uses an LLM judge for one result, costs far more
  tokens than zero-shot, and can amplify speculative critique.
- [OpenHands V1](https://arxiv.org/abs/2511.03690) reports fewer
  system-attributable failures from event-sourced state, typed tool boundaries,
  replay, and sandboxing under matched model capability. Durable execution and
  observability are part of reliability.

Design consequence: send minimal packets, keep raw artifacts auditable, and
require deterministic verification after any reviewer or worker claim.

### Large parallel builds prove possibility, not ordinary necessity

- Anthropic's [parallel C compiler experiment](https://www.anthropic.com/engineering/building-c-compiler)
  used sixteen agents, isolated clones, task locks, and strong test harnesses to
  build a large compiler over nearly 2,000 sessions. It cost about $20,000 and
  remains an early prototype whose authors warn that passing tests does not make
  unreviewed autonomous code safe.
- Anthropic's [long-running application harness](https://www.anthropic.com/engineering/harness-design-long-running-apps)
  uses planner, generator, and evaluator roles with structured artifacts. Its
  reported full harness was more than twenty times the cost of a solo run, and
  the authors emphasize removing scaffolding as model capability improves.

Design consequence: use large teams for large, test-partitionable programs with
isolated ownership and a strong evaluator. Do not generalize that design to a
normal bug fix or feature addition.

## Operational hypothesis to test locally

The research supports a starting policy, not a permanent universal optimum.
Evaluate the skill on real repository tasks under matched budgets:

1. SOLO fixed loop.
2. Two diverse sealed scouts followed by one lead implementation.
3. A larger topology only for tasks classified as independently decomposable.

Compare acceptance success, regressions, escaped defects, review precision,
wall time, tokens, context size, worker overlap, merge conflicts, and unique
decision-changing evidence. Retire topology or roles that fail to outperform
the simpler condition.
