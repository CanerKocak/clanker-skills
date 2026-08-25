# Report Generation (Phase 6)

Comprehensive markdown report structure and formatting guidelines.

---

## Report Structure

Generate markdown report with these mandatory sections:

### 0. Adjudication Ledger

List every candidate that could affect severity or the requested decision. Do
not count raw reviewer or tool findings as accepted findings.

```markdown
## Adjudication Ledger

| Candidate | Contract | Reachability | Policy/intent | Counterevidence | Runtime boundary | Disposition | Decision bridge |
|---|---|---|---|---|---|---|---|
| C-1 | ... | ... | ... | ... | ... | LIVE/POLICY/PARTIAL/... | contract citation or NONE |
```

Only `LIVE` and justified `RESIDUAL` entries are findings. Record `POLICY`
separately. Keep `PARTIAL` open. Decline `N/A`, `CEREMONIAL`, and `THEATER`.
Report `FOLLOW-UP` without expanding the active decision or patch.

The consolidating agent owns each disposition. Delegated severity, confidence,
repetition, automated authorship, a structural match, or a second inspection of
the same call chain is not adjudication.

### 1. Executive Summary

- Severity distribution table for accepted findings only
- Candidate disposition table (`POLICY`, `PARTIAL`, declined, follow-up)
- Risk assessment (CRITICAL/HIGH/MEDIUM/LOW)
- Final recommendation (APPROVE/REJECT/CONDITIONAL) only when the task asks for
  one and every blocker has an explicit decision-contract bridge
- Key metrics (test gaps, blast radius, red flags)

**Template:**
```markdown
# Executive Summary

| Severity | Count |
|----------|-------|
| 🔴 CRITICAL | X |
| 🟠 HIGH | Y |
| 🟡 MEDIUM | Z |
| 🟢 LOW | W |

| Candidate disposition | Count |
|---|---:|
| POLICY | A |
| PARTIAL/OPEN | B |
| DECLINED | C |
| FOLLOW-UP | D |

**Overall Risk:** CRITICAL/HIGH/MEDIUM/LOW
**Recommendation (when requested):** APPROVE/REJECT/CONDITIONAL

**Decision bridge for each blocker:**
- [finding] → [user instruction or governing contract]

**Key Metrics:**
- Files analyzed: X/Y (Z%)
- Test coverage gaps: N functions
- High blast radius changes: M functions
- Security regressions detected: P
```

---

### 2. What Changed

- Commit timeline with visual
- File summary table
- Lines changed stats

**Template:**
```markdown
## What Changed

**Commit Range:** `base..head`
**Commits:** X
**Timeline:** YYYY-MM-DD to YYYY-MM-DD

| File | +Lines | -Lines | Review Priority | Blast Radius |
|------|--------|--------|------|--------------|
| file1.sol | +50 | -20 | HIGH | VERY BROAD |
| file2.sol | +10 | -5 | MEDIUM | NARROW |

**Total:** +N, -M lines across K files
```

---

### 3. Accepted Critical and High Findings

For each HIGH/CRITICAL issue:

```markdown
### [SEVERITY] Title

**File**: path/to/file.ext:lineNumber
**Commit**: hash
**Blast Radius**: N verified reachable production callers (NARROW/MODERATE/BROAD/VERY BROAD)
**Test Coverage**: YES/NO/PARTIAL
**Adjudication**: LIVE/RESIDUAL
**Violated Contract**: [canonical contract and authority]
**Intent/Policy Evidence**: [evidence and why it does not govern]
**Strongest Counterevidence**: [best evidence against the finding]
**Decision Bridge**: [contract citation or NONE]

**Description**: [clear explanation]

**Historical Context**:
- Git blame: Added in commit X (date)
- Message: "[original commit message]"
- [Why this code existed]

**Attack Scenario**:
[Concrete exploitation steps from adversarial.md]

**Proof of Concept**:
```code demonstrating issue```

**Recommendation**:
[Specific fix with code, including canonical owner and non-interference proof
for state-machine/accounting changes]
```

**Example:**
```markdown
### 🔴 CRITICAL: Authorization Bypass in Withdraw

**File**: TokenVault.sol:156
**Commit**: abc123def
**Blast Radius**: 23 verified reachable production callers (BROAD)
**Test Coverage**: NO

**Description**:
Removed `require(msg.sender == owner)` check allows any user to withdraw funds.

**Historical Context**:
- Git blame: Added 2024-06-15 (commit def456)
- Message: "Add owner check per audit finding #45"
- Code existed to prevent unauthorized withdrawals

**Attack Scenario**:
1. Attacker calls `withdraw(1000 ether)`
2. No authorization check (removed)
3. 1000 ETH transferred to attacker
4. Protocol funds drained

**Proof of Concept**:
```solidity
// As any address
vault.withdraw(vault.balance());
// Success - funds stolen
```

**Recommendation**:
```solidity
function withdraw(uint256 amount) external {
+   require(msg.sender == owner, "Unauthorized");
    // ... rest of function
}
```
```

---

### 4. Test Coverage Analysis

- Coverage statistics
- Untested changes list
- Risk assessment

**Template:**
```markdown
## Test Coverage Analysis

**Coverage:** X% of changed code

**Untested Changes:**
| Function | Review Priority | Assurance Gap |
|----------|-----------------|---------------|
| functionA() | HIGH | No focused validation tests |
| functionB() | MEDIUM | Changed logic untested |

**Assurance Assessment:**
N high-priority functions lack focused tests. This lowers confidence and may
require more verification; it does not elevate defect severity or block a
decision without a verified finding and decision bridge.
```

---

### 5. Blast Radius Analysis

- High-impact functions table
- Dependency graph
- Impact quantification

**Template:**
```markdown
## Blast Radius Analysis

**High-Impact Changes:**
| Function | Callers | Review Priority | Analysis Priority |
|----------|---------|------|----------|
| transfer() | 89 | HIGH | P0 |
| validate() | 45 | MEDIUM | P1 |
```

---

### 6. Historical Context

- Security-related removals
- Regression risks
- Commit message red flags

**Template:**
```markdown
## Historical Context

**Security-Related Removals:**
- Line 45: `require` removed (added 2024-03 for CVE-2024-1234)
- Line 78: Validation removed (added 2023-12 "security hardening")

**Regression Risks:**
- Code pattern removed in commit X, re-added in commit Y
```

---

### 7. Policy, Open Candidates, and Recommendations

Separate these categories before recommending changes:

- `POLICY`: documented current behavior and acknowledged exposure; no defect or
  automatic fix. Record reconsideration only if requested.
- `PARTIAL`: exact missing proof and the smallest read-only step that could
  resolve it; no fix recommendation.
- Declined candidates: concise falsification reason.
- Accepted `LIVE`/`RESIDUAL` findings: smallest authorized remedy.

- Immediate actions (blocking)
- Before production (tracking)
- Technical debt (future)

**Template:**
```markdown
## Recommendations

### Immediate (Blocking)
- [ ] Fix accepted CRITICAL issue in TokenVault.sol:156 — decision bridge: [contract]

### Before Production
- [ ] Resolve PARTIAL auth boundary by obtaining [specific evidence]
- [ ] Load test blast radius functions

### Technical Debt
- [ ] Refactor validation pattern consistency
```

A test gap alone is not an immediate blocker. A technical exposure does not
become a payment, merge, deployment, production, or acceptance condition unless
the report cites the governing decision contract. Never invent an approval
role or written-acceptance requirement.

---

### 8. Analysis Methodology

- Strategy used (DEEP/FOCUSED/SURGICAL)
- Files analyzed
- Coverage estimate
- Techniques applied
- Limitations
- Confidence level

**Template:**
```markdown
## Analysis Methodology

**Strategy:** FOCUSED (80 files, medium codebase)

**Analysis Scope:**
- Files reviewed: 45/80 (56%)
- HIGH review priority: 100% coverage
- MEDIUM RISK: 60% coverage
- LOW RISK: Excluded

**Techniques:**
- Git blame on all removals
- Blast radius calculation
- Test coverage analysis
- Adversarial modeling for HIGH-priority review surfaces

**Limitations:**
- Did not analyze external dependencies
- Limited to 1-hop caller analysis

**Confidence:** HIGH for analyzed scope, MEDIUM overall
```

---

### 9. Appendices

- Commit reference table
- Key definitions
- Contact info

---

## Formatting Guidelines

**Tables:** Use markdown tables for structured data

**Code blocks:** Always include syntax highlighting
```solidity
// Solidity code
```
```rust
// Rust code
```

**Status indicators:**
- ✅ Complete
- ⚠️ Warning
- ❌ Failed/Blocked

**Severity:**
- 🔴 CRITICAL
- 🟠 HIGH
- 🟡 MEDIUM
- 🟢 LOW

**Before/After comparisons:**
```markdown
**BEFORE:**
```code
old code
```

**AFTER:**
```code
new code
```
```

**Line number references:** Always include
- Format: `file.sol:L123`
- Link to commit: `file.sol:L123 (commit abc123)`

---

## File Output (When Requested)

Create a persistent report only when the user requests an artifact or an active
governing workflow explicitly requires one and the current request authorizes
the write. Otherwise deliver the complete review in chat. Do not invent a file
requirement from this skill.

**Priority order for output:**
1. User-specified path
2. Current authorized project directory
3. Chat, if no destination is authorized or the write fails

**Filename format:**
```
<PROJECT>_DIFFERENTIAL_REVIEW_<DATE>.md

Example: VeChain_Stargate_DIFFERENTIAL_REVIEW_2025-12-26.md
```

---

## User Notification Template

After generating a requested report file:

```markdown
Report generated successfully!

📄 File: [filename]
📁 Location: [path]
📏 Size: XX KB
⏱️ Review Time: ~X hours

Summary:
- X accepted findings (Y critical, Z high)
- A policies, B partial/open candidates, C declined candidates
- Final recommendation: APPROVE/REJECT/CONDITIONAL
- Confidence: HIGH/MEDIUM/LOW

Next steps:
- Review findings in detail
- Address findings explicitly marked merge-blocking by their cited decision bridge
- Consider chaining with issue-writer for stakeholder report
```

---

## Integration with issue-writer

After generating differential review, transform accepted findings and the
adjudication ledger into an audit report:

```bash
issue-writer --input DIFFERENTIAL_REVIEW_REPORT.md --format audit-report
```

This creates polished documentation for non-technical stakeholders.

---

## Error Handling

If an authorized file write fails, do not silently choose a different external
destination. Report the failure, provide the complete result in chat, and ask
for a new destination only when a persistent artifact is still required.
