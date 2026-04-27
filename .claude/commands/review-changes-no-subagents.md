---
description: Thorough multi-pass review of git changes, run sequentially in one context (no subagents)
argument-hint: "[<git-ref> | PR#<number>]"
allowed-tools: ["Bash", "Read", "Grep", "Glob"]
---

# /review-changes-no-subagents — Multi-pass review (single-context variant)

Same review structure as `/review-changes`, but executed sequentially in
the current context instead of via parallel subagents. Use this variant
when you want lower token cost, or when you want to read each pass's
output incrementally as it's produced.

**Argument:** $ARGUMENTS (optional). Forms:
- *(empty)* — review current branch vs `main`
- a git ref or range — review that diff
- `PR#123` or `123` — fetch and review GitHub PR #123 via `gh`

---

## The anti-anchor rule (READ THIS FIRST — and re-read between passes)

LLM reviewers have a strong prior toward producing 3-7 findings per
review, regardless of actual code quality. This produces two failure
modes:

- **Floor inflation:** fabricating nits to reach ~3 on clean code
- **Ceiling truncation:** stopping at ~7 even when more real issues exist

The single-context variant is *more* susceptible to this anchor than
the subagent variant, because all passes share one running context and
can implicitly trade findings against each other. To compensate:

1. **Each pass is independent.** Do not adjust an earlier pass's output
   because a later pass found something. Once a pass's output is
   written, it is final.
2. **Each pass's count is independent.** Pass A finding 0 issues does
   not mean Pass B should find more to compensate. Pass A finding 12
   issues does not mean Pass B should find fewer.
3. **No global summary balancing.** When you produce the final summary,
   you must not have edited any pass's output to make the totals look
   "reasonable."
4. **Re-read this rule before starting each pass.** State out loud:
   "Starting Pass <X>. Anti-anchor rule re-read. This pass's count is
   whatever it is."

The user has explicitly stated: a clean review does not lower the bar;
a noisy review surfaces all issues even if there are many.

---

## Step 1 — Determine review scope

Capture the diff:

```
# If $ARGUMENTS starts with PR# or is a bare integer, fetch via gh:
#   gh pr diff <num> > /tmp/review-diff.patch
#   gh pr view <num> --json title,body,baseRefName,headRefName,commits
# Else if $ARGUMENTS is a non-empty ref/range:
#   git diff <ref> > /tmp/review-diff.patch
#   git log <ref> --oneline
# Else (no args):
#   git diff main...HEAD > /tmp/review-diff.patch
#   git log main..HEAD --oneline
#   git status
```

State the scope back to the user in one line, e.g.
"Reviewing 12 commits / 47 files changed on `feature/x` vs `main`."

If the diff is empty, stop and tell the user — do not invent a review.

---

## Step 2 — Run each pass, one at a time, in this exact order

Before each pass, do this preamble out loud to yourself in the response:

> Starting Pass <X>: <pass name>. Anti-anchor rule re-read. The count
> for this pass is whatever falls out of applying the bar — there is
> no target. Lane discipline: if a finding fits another pass's lane,
> defer to that pass.

Then do the pass, producing the full output block (Issues + Questions
sections, with `_none_` if empty), before moving to the next pass.

**Do not summarize during the run. Do not look back at a previous
pass's output to "rebalance."**

### Pass-finding format (use for every pass)

```
## Pass <X> — <name>: <N> issues, <M> questions

### Issues
- **[file:line]** <one-line summary>
  <2-4 line explanation; quote the code; suggest the fix>
  bar: above | borderline

### Questions
- **[file:line or "scope"]** <the question>
  <why this is unclear from the diff alone>
```

If 0 issues: write `### Issues\n_none_`. Same for questions. Do not
omit the section header.

### Pass A — Trust-boundary violations (ADR-002)

Lane: violations of the three-process trust boundary defined in
`docs/adr/ADR-002-three-process-security-model.md` and the Hard Rules
in AGENTS.md.

**Above the bar (report):**
- App or UA-side package importing Node-side packages (`blocknode`,
  `dht`, `nodeapi`, `leasevalidator`, `signedrecordstore`) or vice versa
- Private keys or signing functions appearing in Node-side packages
- Apps constructing CIDs, talking directly to the Node, or holding
  private keys
- Capability URLs or bearer-link sharing (forbidden per ADR-019/069)
- Stubbed crypto in production code paths (Hard Rule: real crypto from
  the start)
- Hand-edits to generated wire-format code

**Below the bar (do not report):**
- Style nits in trust-boundary-adjacent code
- Missing comments
- Refactor suggestions that don't fix a violation

### Pass B — Schema, CDDL, and wire-format integrity

Lane: CDDL is source of truth (Hard Rule). Schema types are exact.
Never renumber.

**Above the bar:**
- Wire struct fields hand-edited where they should be generated
- CDDL changes that don't match Go struct changes (or vice versa)
- Renumbered enum values, iota blocks, ADR sections, requirement IDs,
  or document section numbers
- Loosened schema constraints (string instead of fixed-size byte array,
  int instead of bounded uint) without a documented reason
- New wire format introduced without a corresponding `.cddl` file in
  the owning package

**Below the bar:**
- CDDL formatting style
- Naming preferences in schema fields

### Pass C — Design-vs-implementation drift

Lane: when `*_design.go` (the authoritative module spec, per AGENTS.md
"Design-as-Code") disagrees with the implementation in the same
package.

**Above the bar:**
- Code implements an API shape that contradicts the design file
- Design file was not updated when implementation diverged (per
  AGENTS.md: "When implementation conflicts with a DRAFT design file,
  update the design file and flag the change")
- New module added without a `*_design.go` file
- `*_design.go` contains `// OPEN:` markers that the implementation
  silently picked a default for, rather than resolving in the design

**Below the bar:**
- Design file phrasing nits
- Missing optional `// Status:` line

For each changed `pkg/<x>/`, read `pkg/<x>/*_design.go` if present
before evaluating drift.

### Pass D — Crypto correctness

Lane: cryptographic correctness only. Use this exact bar (from
`.claude/agents/crypto-reviewer.md`):

**Above the bar:**
- Hardcoded keys, nonces, or IVs
- Nonce reuse or predictable nonce generation
- Use of deprecated or weak algorithms
- Missing constant-time comparison for secrets/MACs
- Incorrect key derivation (raw passwords as keys, insufficient rounds)
- Missing or incorrect authenticated encryption (encrypt without MAC)
- Improper random number generation (math/rand instead of crypto/rand)
- Secret material not zeroed after use
- Side-channel leaks in branching on secret data

**Below the bar:**
- Code style in crypto packages
- Crypto API ergonomics

### Pass E — Doc routing and architectural changes

Lane: facts landing in the wrong document; missing ADRs; broken
project-map routing.

**Above the bar:**
- Architectural change (new module, changed trust boundary, new wire
  format, new sharing model) without a corresponding ADR in
  `docs/adr/`. AGENTS.md states this is required.
- New user-visible capability without an entry in
  `plan/user-stories.md`
- New behavioral SHALL/MAY constraint without entry in
  `docs/requirements/requirements.md`
- Renamed module/package without updating every ADR that references it
  (AGENTS.md: "ADRs are current-tense and updated in place on rename")
- New fact added to a doc when `project-map.md` says it belongs
  elsewhere
- Internal name (`shell`, `social`, `useragent`, `node`) leaked into a
  user-facing surface, or user-facing name (*OurCloud*, *OurCloud
  Social*) used in an engineering artifact

**Below the bar:**
- Doc typos
- Wording preferences in existing prose

Read `project-map.md` and AGENTS.md "Hard rules" before starting.

### Pass F — General correctness and bugs

Lane: bugs that would cause incorrect behavior, data loss, panics, or
security holes — but NOT in any other pass's lane.

**Above the bar:**
- Race conditions on shared state
- Resource leaks (unclosed files, goroutines, contexts)
- Error swallowed without logging or propagation
- Off-by-one, nil deref, integer overflow, unbounded slice growth
- Logic that doesn't match the commit message's stated intent
- TOCTOU, unchecked authentication assumptions
- Panics in code paths reachable from untrusted input

**Below the bar:**
- Code style, naming, formatting
- "Could be more idiomatic"
- Performance micro-optimizations without a stated perf requirement

**Lane discipline:** if a finding fits Pass A (trust boundary) or
Pass D (crypto), defer to that pass and do not report it here.

### Pass G — Test integrity

Lane: tests that don't actually test what they claim, or missing tests
where the project's test policy requires them.

**Above the bar:**
- Test mocks crypto where AGENTS.md says "real crypto from the start"
- Test asserts a TODO placeholder that was never resolved (per the
  user's testing protocol, this is an OPEN bug, not a passing test)
- Production code change with no test change AND no integration-test
  coverage that exercises the change
- Test that passes regardless of the production behavior under test
  (tautological assertions)
- Integration test added to `tests/` but not wired into
  `make full-regression`
- New IPC surface with no test crossing the process boundary

**Below the bar:**
- Test naming preferences
- Test could be more concise

### Pass H — Intent and missing follow-ups (questions only)

This pass produces ONLY questions, not issues.

Read the commit messages, PR description (if any), and diff. For each
of these, ask a question:

- A change whose motivation is not explained by the diff or commit
  message ("why is X being changed at all?")
- A change that obviously implies a follow-up change that isn't in
  the diff ("if X moved to package Y, shouldn't Z also move?")
- A change that's half-done — e.g. new function added but no caller,
  flag added but never read, type defined but never used
- A change that conflicts with a recent commit on `main`, or with an
  ADR, in a way that suggests the author didn't see the conflict
- A reverted change — code that the diff puts back to a state an
  earlier commit moved away from, with no explanation

Output format:

```
## Pass H — Intent: <N> questions

### Questions
- **[file:line or "scope"]** <the question>
  <one or two lines: what is unclear, why it matters>
```

If 0 questions: `### Questions\n_none_`. No Issues section.

---

## Step 3 — Aggregate (DO NOT re-rank or trim)

Once every pass has produced its block, produce the final summary in
this exact shape:

```
# Review of <scope>

## Summary
- <total issues> issues across 7 issue-producing passes; <total questions> questions
- Passes with 0 findings: <list>
- Passes with 5+ findings: <list>

## Anti-anchor self-check
- Did any pass report exactly 3-7 findings? <yes/no>
  - If yes, re-read that pass's output and confirm the count is the
    natural count, not a stopping point. If you stopped early, add
    the missing findings now and update the count.
- Did you adjust any pass's output during aggregation? <must be no>
- Did you re-rank or merge findings across passes? <must be no>
```

The summary references the per-pass blocks already produced above — do
not duplicate or reformat them.

---

## Step 4 — Offer next actions

After the report, ask the user (do not assume):

- "Want me to fix any of these? Tell me which by number/lane."
- "Want me to dig into any of the questions before fixing?"

Do not start fixing without confirmation. The user's
`feedback_qa_mode.md` memory says information-gathering asks stay in
report-only mode.
