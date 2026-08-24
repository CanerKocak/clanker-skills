<div align="center">
  <img src=".github/assets/social-preview.png" alt="Clanker Skills — evidence-first OpenAI Codex skills for code review, security audits, data quality, PDF reporting, and frontend UI" width="100%">

  <h1>Clanker Skills</h1>

  <p><strong>Map reality. Change the owner. Prove the outcome.</strong></p>

  <p>
    <a href="https://github.com/CanerKocak/clanker-skills/actions/workflows/validate.yml"><img src="https://github.com/CanerKocak/clanker-skills/actions/workflows/validate.yml/badge.svg" alt="Repository validation status"></a>
    <img src="https://img.shields.io/badge/skills-16-D7FF64?style=flat-square&labelColor=101310" alt="16 bundled skills">
    <img src="https://img.shields.io/badge/OpenAI_Codex-plugin-D7FF64?style=flat-square&labelColor=101310" alt="OpenAI Codex plugin">
  </p>
</div>

Clanker Skills is a curated OpenAI Codex plugin for evidence-first software
engineering. Its 16 agent skills cover code review, call-chain analysis,
semantic blast radius, security audits, data quality, PDF reporting, prompt
hygiene, and frontend UI quality. The workflows are designed for tasks where
a successful command is not enough: each conclusion should name its evidence,
its boundary, and a way to prove it wrong.

> [!NOTE]
> This is a community-maintained project and is not an official OpenAI project.

## Install in Codex

Add the GitHub repository as a Codex plugin marketplace, then install its one
plugin:

~~~bash
codex plugin marketplace add CanerKocak/clanker-skills --ref main
codex plugin add clanker-skills@clanker-skills
~~~

Start a new Codex task after installation. Skills can activate automatically
from their descriptions, or you can invoke one explicitly:

~~~text
$edit-the-chain map the owner and blast radius before changing this API
$differential-review review this branch against main for security regressions
$analyze-data-quality determine whether this export is safe to publish
~~~

The package follows OpenAI's current
[plugin structure](https://developers.openai.com/plugins/build/plugins): one
<code>.codex-plugin/plugin.json</code> manifest, one <code>skills/</code> tree,
and a repo-scoped marketplace catalog.

<details>
<summary><strong>Install the skills without the plugin marketplace</strong></summary>

Codex also discovers standalone user skills under <code>~/.agents/skills</code>
and supports symlinked packages. This installer leaves every existing
destination untouched:

~~~bash
git clone https://github.com/CanerKocak/clanker-skills.git "${HOME}/clanker-skills"
mkdir -p "${HOME}/.agents/skills"

repo_dir="${HOME}/clanker-skills"
skills_dir="${repo_dir}/plugins/clanker-skills/skills"
for skill_dir in "${skills_dir}"/*; do
  [ -f "${skill_dir}/SKILL.md" ] || continue
  destination="${HOME}/.agents/skills/$(basename "${skill_dir}")"
  if [ -e "${destination}" ] || [ -L "${destination}" ]; then
    printf 'skip %s (already exists)\n' "${destination}"
    continue
  fi
  ln -s "${skill_dir}" "${destination}"
done
~~~

</details>

## Why these workflows exist

Most engineering failures in agent-driven work are not syntax failures. They
come from editing the wrong owner, missing another caller, trusting a partial
dataset, promoting a weak suspicion into a security finding, or declaring a
document complete without looking at the rendered artifact.

Clanker Skills adds four recurring controls:

- **Ownership before edits.** Map the real oracle, call chain, and reachable
  product surfaces before changing a shared contract.
- **Independent evidence.** Reconcile compiler or language-server evidence
  with AST and text searches instead of treating one heuristic as exhaustive.
- **Frozen inputs before publishing.** Separate business context, analytical
  validation, security findings, report rendering, and visual QA.
- **Restraint before ceremony.** Reject speculative guards, recovery rails,
  generic UI patterns, and prose that only narrates the work session.

## Workflow map

~~~mermaid
flowchart TD
    A[Request] --> C{Workstream}
    A -.->|uncertain or high-risk| B[adaptive-code-orchestrator]
    B --> C
    C -->|non-trivial code change| D[edit-the-chain]
    D --> E[semantic-blast-radius]
    E --> F[ast-grep-callchain-audit]
    E --> G[call-chain-invariants]
    F --> H[Smallest correct change]
    G --> H
    H -.->|security-focused diff| I[differential-review]
    H --> J[thermo-nuclear-code-quality-review]
    I -.->|guard or fallback proposed| K[yagni-anti-ceremonial]
    C -->|Data| L{Business context complete?}
    L -->|No| M[gather-business-context]
    L -->|Yes| N[analyze-data-quality]
    M --> N
    C -->|Audit PDF| O[pdf-findings-schema]
    O --> P[pdf-security-audit-report]
    P --> Q{Rendering path}
    Q -->|Typst| R[pdf-typst-report]
    Q -->|Other renderer| S[pdf-visual-qa]
    R --> S
    C -->|Frontend| T[uncodixfy]
~~~

This is a routing map, not a mandate to invoke every skill. Small, local work
should stay small.

## Skill catalog

### Change safety and code review

| Skill | Use it for | Core contract |
|---|---|---|
| [<code>adaptive-code-orchestrator</code>](plugins/clanker-skills/skills/adaptive-code-orchestrator/SKILL.md) | Uncertain, cross-cutting, or high-risk repository work. | Chooses solo work, bounded reconnaissance, dependency waves, or independent review according to the evidence gap. |
| [<code>edit-the-chain</code>](plugins/clanker-skills/skills/edit-the-chain/SKILL.md) | Any non-trivial edit that needs owner and impact mapping. | Classifies the requested route as a short path, awkward parkour, or the wrong oracle; then binds review to the exact final candidate. |
| [<code>semantic-blast-radius</code>](plugins/clanker-skills/skills/semantic-blast-radius/SKILL.md) | Shared APIs, types, helpers, state machines, or public contracts. | Builds one canonical cross-file impact graph from compiler or LSP evidence plus independent AST and text searches. |
| [<code>ast-grep-callchain-audit</code>](plugins/clanker-skills/skills/ast-grep-callchain-audit/SKILL.md) | Structural definitions, calls, imports, parameters, and variants. | Contributes AST-backed call-chain edges and counterexamples; a structural match remains a candidate until verified. |
| [<code>call-chain-invariants</code>](plugins/clanker-skills/skills/call-chain-invariants/SKILL.md) | Similar-looking product surfaces with uncertain shared behavior. | Classifies each reachable surface as applying, different-contract, not applicable, or unknown before completeness is claimed. |
| [<code>differential-review</code>](plugins/clanker-skills/skills/differential-review/SKILL.md) | Security-focused review of a commit, branch, diff, or pull request. | Uses history, blast radius, coverage, and adversarial analysis while requiring evidence before promoting a finding. |
| [<code>yagni-anti-ceremonial</code>](plugins/clanker-skills/skills/yagni-anti-ceremonial/SKILL.md) | Proposed guards, fallbacks, compatibility rails, or recovery paths. | Separates live contract requirements from residual risk, policy, follow-up work, ceremony, and theater. |
| [<code>thermo-nuclear-code-quality-review</code>](plugins/clanker-skills/skills/thermo-nuclear-code-quality-review/SKILL.md) | The final source candidate before delivery. | Runs two distinct coherence passes: ownership and boundary integrity, then simplification and hidden-coupling pressure. |

### Data and business context

| Skill | Use it for | Core contract |
|---|---|---|
| [<code>gather-business-context</code>](plugins/clanker-skills/skills/gather-business-context/SKILL.md) | Missing definitions, source authority, ownership, recent changes, or decision framing. | Retrieves only the context needed downstream, preserves source conflicts, and does not disguise retrieval as analysis. |
| [<code>analyze-data-quality</code>](plugins/clanker-skills/skills/analyze-data-quality/SKILL.md) | Tables, financial equations, dashboards, query results, or analytical evidence. | Establishes grain and checks completeness, uniqueness, validity, consistency, integrity, freshness, distributions, and reconciliation boundaries. |

### Security reporting and PDFs

| Skill | Use it for | Core contract |
|---|---|---|
| [<code>pdf-findings-schema</code>](plugins/clanker-skills/skills/pdf-findings-schema/SKILL.md) | Freezing security findings before layout work begins. | Defines the canonical JSON source so rendering cannot invent findings, evidence, status, or severity. |
| [<code>pdf-security-audit-report</code>](plugins/clanker-skills/skills/pdf-security-audit-report/SKILL.md) | Turning frozen findings into a security assessment booklet. | Builds the report structure from validated data and keeps severity and remediation claims traceable to evidence. |
| [<code>pdf-typst-report</code>](plugins/clanker-skills/skills/pdf-typst-report/SKILL.md) | Stable typesetting for long technical or security reports. | Provides a Typst-first report path and hands the rendered result to the visual quality gate. |
| [<code>pdf-visual-qa</code>](plugins/clanker-skills/skills/pdf-visual-qa/SKILL.md) | Any generated PDF approaching delivery. | Renders pages to pixels and rejects clipping, overlap, overflow, weak contrast, and other visible defects. |

### Interface and durable prose

| Skill | Use it for | Core contract |
|---|---|---|
| [<code>uncodixfy</code>](plugins/clanker-skills/skills/uncodixfy/SKILL.md) | Generating or revising frontend HTML, CSS, React, or product UI. | Rejects generic AI-dashboard aesthetics in favor of restrained, product-specific hierarchy, spacing, motion, and color. |
| [<code>prompt-leakage</code>](plugins/clanker-skills/skills/prompt-leakage/SKILL.md) | Comments, READMEs, instructions, review text, and commit messages. | Removes chat motives, restatements, and reviewer theater while preserving information a stranger cannot infer. |

## Make routing automatic

After installation, add the repository's single
[evidence-first routing block](docs/global-routing.md) to your global
<code>~/.codex/AGENTS.md</code>. It tells Codex which skill owns each workflow
and, just as importantly, when not to invoke adjacent skills.

## Repository structure

~~~text
.agents/plugins/marketplace.json           Repo marketplace catalog
.github/assets/social-preview.png          Repository brand card
plugins/clanker-skills/
├── .codex-plugin/plugin.json              Plugin identity and UI metadata
└── skills/<name>/
    ├── SKILL.md                            Trigger and workflow contract
    ├── agents/openai.yaml                 Codex display metadata
    └── references|scripts|templates|...   Package-owned resources
scripts/validate_repository.py             Dependency-free integrity check
~~~

There is one canonical copy of every skill. Package resources move with their
<code>SKILL.md</code>; scripts, references, templates, images, and licenses are
part of the contract rather than optional decoration.

## Verification

Run the same dependency-free check used by GitHub Actions:

~~~bash
python3 scripts/validate_repository.py
~~~

It verifies the exact 16-skill inventory, frontmatter names, Codex UI metadata,
explicit default prompts, plugin and marketplace wiring, local Markdown links,
third-party provenance, and the exact 1280×640 social-preview contract. The
check fails closed when a package moves or a new skill appears without being
added to the reviewed inventory.

## Runtime boundaries

- <code>ast-grep-callchain-audit</code> expects the non-deprecated
  <code>ast-grep</code> binary.
- The PDF report path may call a separately installed <code>pdf</code> base
  skill for ReportLab operations. Typst is optional and used only when selected.
- <code>edit-the-chain</code> can run its bundled review harness through
  <code>codex exec</code>.
- Some conditional workflows name companion skills that are not bundled here.
  Missing companions must be reported as a boundary, never simulated.

## Provenance and licensing

<code>uncodixfy</code> retains its upstream MIT License and is recorded in
[<code>THIRD_PARTY_NOTICES.md</code>](THIRD_PARTY_NOTICES.md). The repository
does not currently grant a blanket license for the remaining material. Public
access alone is not permission to copy, modify, or redistribute those packages;
a repository-wide license remains an explicit maintainer decision.

## Contributing and security

Read [<code>CONTRIBUTING.md</code>](CONTRIBUTING.md) before changing a package.
For unsafe execution or exploitable workflow behavior, follow
[<code>SECURITY.md</code>](SECURITY.md) and use private vulnerability reporting.
Use public issues for reproducible bugs and focused skill proposals.

---

Built for engineers who want agents to show their work—and know where their
evidence stops.
