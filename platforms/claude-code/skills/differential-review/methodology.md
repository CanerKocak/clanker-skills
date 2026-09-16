# Running a differential review, phase by phase

Detailed phase-by-phase workflow for security-focused code review.

## Pre-Analysis: Baseline Context Building

**FIRST ACTION - Build complete baseline understanding:**

If `audit-context-building` skill is available:

```bash
# Checkout baseline commit
git checkout <baseline_commit>

# Invoke audit-context-building skill on baseline codebase
# Scope = entire relevant project (e.g., packages/contracts/contracts/ for Solidity, src/ for Rust, etc.)
audit-context-building --scope [entire project or main contract directory] --focus invariants,trust-boundaries,validation-patterns,call-graphs,state-flows

# Examples:
# For Solidity: audit-context-building --scope packages/contracts/contracts
# For Rust: audit-context-building --scope src
# For full repo: audit-context-building --scope .
```

**Capture from baseline analysis:**
- System-wide invariants (what must ALWAYS be true across all code)
- Trust boundaries and privilege levels (who can do what)
- Validation patterns (what gets checked where - defense-in-depth)
- Complete call graphs for critical functions (who calls what)
- State flow diagrams (how state changes)
- External dependencies and trust assumptions
- Current specifications, durable policy comments, tests, commit/PR rationale,
  acknowledged residual risks, and explicit non-goals

**Why this matters:**
- Understand what the code was SUPPOSED to do before changes
- Identify implicit security assumptions in baseline
- Detect when changes violate baseline invariants
- Know which patterns are system-wide vs local
- Catch when changes break defense-in-depth

**Store baseline context for reference during differential analysis.**

After baseline analysis, checkout back to head commit to analyze changes.

---

## Phase 0: Intake & Triage

**Extract changes:**
```bash
# For commit range
git diff <base>..<head> --stat
git log <base>..<head> --oneline

# For PR
gh pr view <number> --json files,additions,deletions

# Get all changed files
git diff <base>..<head> --name-only
```

**Assess codebase size:**
```bash
find . -name "*.sol" -o -name "*.rs" -o -name "*.go" -o -name "*.ts" | wc -l
```

**Classify complexity:**
- **SMALL**: <20 files → Deep analysis (read all deps)
- **MEDIUM**: 20-200 files → Focused analysis (1-hop deps)
- **LARGE**: 200+ files → Surgical (critical paths only)

**Assign review priority to each file:**
- **HIGH**: Auth, crypto, external calls, value transfer, validation removal
- **MEDIUM**: Business logic, state changes, new public APIs
- **LOW**: Comments, tests, UI, logging

Review priority determines analysis depth. It does not assign finding severity.

---

## Phase 1: Changed Code Analysis

For each changed file:

1. **Read both versions** (baseline and changed)

2. **Analyze each diff region:**
   ```
   BEFORE: [exact code]
   AFTER: [exact code]
   CHANGE: [behavioral impact]
   SECURITY: [implications]
   ```

3. **Git blame removed code:**
   ```bash
   # When was it added? Why?
   git log -S "removed_code" --all --oneline
   git blame <baseline> -- file.sol | grep "pattern"
   ```

   **Red flags:**
   - Removed code from "fix", "security", or "CVE" commits → highest review priority
   - Recently added (<1 month) then removed → elevated review priority

   These are investigation triggers, not severity verdicts. Establish the
   current contract, reachable trigger, and impact before assigning severity.

4. **Check for regressions (re-added code):**
   ```bash
   git log -S "added_code" --all -p
   ```

   Pattern: Code added → removed for security → re-added now = REGRESSION

5. **Micro-adversarial analysis** for each change:
   - What attack did removed code prevent?
   - What new surface does new code expose?
   - Can modified logic be bypassed?
   - Are checks weaker? Edge cases covered?

6. **Generate concrete attack scenarios:**
   ```
   SCENARIO: [attack goal]
   PRECONDITIONS: [required state]
   STEPS:
     1. [specific action]
     2. [expected outcome]
     3. [exploitation]
   WHY IT WORKS: [reference code change]
   IMPACT HYPOTHESIS: [specific harm + affected scope; severity is UNASSIGNED]
   ```

---

## Phase 2: Test Coverage Analysis

**Identify coverage gaps:**
```bash
# Production code changes (exclude tests)
git diff <range> --name-only | grep -v "test"

# Test changes
git diff <range> --name-only | grep "test"

# For each changed function, search for tests
grep -r "test.*functionName" test/ --include="*.sol" --include="*.js"
```

**Assurance rules:**
- NEW function + NO focused tests → lower evidence confidence and inspect deeply
- MODIFIED validation + UNCHANGED tests → require a focused test or document the exact gap
- Complex logic (>20 lines) + NO tests → raise review priority, not defect severity

Test absence does not establish reachability, exploitability, impact, or a
contract violation. Keep `review priority`, `impact severity`, `reachability`,
and `evidence confidence` as separate fields.

---

## Phase 3: Blast Radius Analysis

**Build the reachable production call graph:**
```bash
# TypeScript example; adapt the language and roots to the repository.
ast-grep run --pattern 'functionName($$$ARGS)' --lang ts backend/src

# Text search is an orthogonal discovery pass for aliases, registration,
# configuration, templates, generated wiring, and other AST blind spots.
rg -n '\bfunctionName\b' backend/src
```

Invoke `ast-grep-callchain-audit` for executable-surface and call-chain work.
Reconcile definitions, imports, re-exports, aliases, callbacks, framework
registration, dynamic dispatch, generated/configuration wiring, tests, and
production callers. Count mechanically from the exact verified production
call-site set; a raw text-hit count is triage evidence only and cannot support
an exhaustive blast-radius claim.

**Classify blast radius:**
- 1-5 calls: NARROW
- 6-20 calls: MODERATE
- 21-50 calls: BROAD
- 50+ calls: VERY BROAD

Blast radius determines inspection scope and potential propagation. It does not
by itself determine defect impact or severity. Keep tests, administrative
surfaces, and unreachable or unresolved candidates separate from reachable
production callers.

**Priority matrix:**

| Change Review Priority | Blast Radius | Priority | Analysis Depth |
|-------------|--------------|----------|----------------|
| HIGH | VERY BROAD | P0 | Deep + all deps |
| HIGH | BROAD/MODERATE | P1 | Deep |
| HIGH | NARROW | P2 | Standard |
| MEDIUM | VERY BROAD/BROAD | P1 | Standard + callers |

---

## Phase 4: Deep Context Analysis

**If `audit-context-building` skill is available**, invoke it to help answer all the questions below for each HIGH-priority review function:

```bash
# Run audit-context-building on the changed function and its dependencies
audit-context-building --scope [file containing changed function] --focus flow-analysis,call-graphs,invariants,root-cause
```

**The audit-context-building skill will help you answer:**

1. **Map complete function flow:**
   - Entry conditions (preconditions, requires, modifiers)
   - State reads (which variables accessed)
   - State writes (which variables modified)
   - External calls (to contracts, APIs, system)
   - Return values and side effects

2. **Trace internal calls:**
   - List all functions called
   - Recursively map their flows
   - Build complete call graph

3. **Trace external calls:**
   - Identify trust boundaries crossed
   - List assumptions about external behavior
   - Check for reentrancy risks

4. **Identify invariants:**
   - What must ALWAYS be true?
   - What must NEVER happen?
   - Are invariants maintained after changes?

5. **Five Whys root cause:**
   - WHY was this code changed?
   - WHY did the original code exist?
   - WHY might this break?
   - WHY is this approach chosen?
   - WHY could this fail in production?

**If `audit-context-building` skill is NOT available**, manually perform the line-by-line analysis above using Read, Grep, and code tracing.

**Cross-cutting pattern detection:**
```bash
# Find repeated validation patterns
grep -r "require.*amount > 0" --include="*.sol" .
grep -r "onlyOwner" --include="*.sol" .

# Check if any removed in diff
git diff <range> | grep "^-.*require.*amount > 0"
```

**Flag if removal breaks defense-in-depth.**

---

## Phase 5.5 Handoff: Finding Promotion

After adversarial analysis and before report generation, run
`yagni-anti-ceremonial` for every candidate that could receive severity, enter
recommendations, or change payment, merge, deployment, production, or
acceptance. Use `fp-check` for disputed, delegated/automated, or complex
money/auth/state-machine claims.

The consolidating agent must record:

- falsifiable contract-violation claim;
- canonical contract and authority;
- exact trigger, predecessor state, and reachable transition;
- producers, writers, readers, and relevant runtime/deployment evidence;
- intent/policy/history evidence and strongest counterevidence;
- disposition: `LIVE`, `RESIDUAL`, `POLICY`, `N/A`, `FOLLOW-UP`,
  `CEREMONIAL`, `THEATER`, or `PARTIAL`;
- decision bridge when the result would change a nontechnical decision;
- canonical owner and non-interference proof before recommending a
  state-machine or accounting remedy.

No severity or blocking recommendation may cross this handoff with an
incomplete record. A second check of the same call chain verifies mechanics,
not the product contract.

---

**Next steps:**
- For HIGH-priority review changes, proceed to [adversarial.md](adversarial.md)
- For report generation, see [reporting.md](reporting.md)
