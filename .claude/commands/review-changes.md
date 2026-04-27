---
description: Thorough multi-pass review of git changes using parallel specialist subagents
argument-hint: "[<git-ref> | PR#<number>]"
allowed-tools: ["Bash", "Read", "Grep", "Glob", "Agent"]
---

# /review-changes — Multi-pass review (subagent variant)

Review the changes in the current branch (or a specified ref / PR) thoroughly,
across multiple specialist passes run as parallel subagents. Each pass has its
own absolute bar and reports independently — there is no global finding quota.

**Argument:** $ARGUMENTS (optional). Forms:
- *(empty)* — review current branch vs `main`
- a git ref or range — review that diff (e.g. `HEAD~3..HEAD`, `feature/x`)
- `PR#123` or `123` — fetch and review GitHub PR #123 via `gh`

---

## The anti-anchor rule (READ THIS FIRST)

LLM reviewers have a strong prior toward producing 3-7 findings per review,
regardless of actual code quality. This produces two failure modes:

- **Floor inflation:** fabricating nits to reach ~3 on clean code
- **Ceiling truncation:** stopping at ~7 even when more real issues exist

This command exists to defeat that prior. The structure below — parallel
specialist subagents with independent counters — is the mechanism. **Do not
re-introduce the anchor when aggregating.** Specifically:

- Do not trim, merge, or re-rank findings to reach a "reasonable" total.
- Do not drop a pass's finding because another pass already found something
  similar — note the overlap, keep both.
- A pass reporting 0 findings is a valid, expected outcome. Do not push back.
- A pass reporting 20 findings is also valid. Do not summarize down to 7.
- The user has explicitly stated: a clean review does not lower the bar; a
  noisy review surfaces all issues even if there are many.

---

## Step 1 — Determine review scope

Run these and capture the diff that the passes will review:

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

## Step 2 — Launch all passes in parallel (single message, multiple Agent calls)

Use `subagent_type: "general-purpose"` for each pass below, except where a
named agent is specified. Pass each agent the full diff path
(`/tmp/review-diff.patch`) and the commit messages so it can read both
intent and content. Each pass prompt MUST start with the anti-anchor
preamble below, then the pass-specific bar and scope.

### Anti-anchor preamble (paste verbatim into every pass prompt)

```
You are one specialist pass in a multi-pass review. Other passes cover
other defect classes; do not worry about them. Your job is to find every
finding in YOUR lane that meets YOUR bar — no more, no fewer.

Hard rules:
- Report 0 findings if the diff has no issues in your lane. This is a
  valid, expected outcome. Do not invent issues to seem useful.
- Report 20+ findings if that's what's actually there. Do not stop at
  any "reasonable" count. There is no quota.
- Each finding must cite file:line and quote or describe the specific
  code. Vague findings ("consider improving error handling") are not
  findings — drop them.
- If you are unsure whether something meets the bar, include it and
  mark it `bar: borderline` with a one-line justification. Do not
  silently drop borderline items.
- Separate QUESTIONS from ISSUES. A question is "the diff doesn't
  explain why X" or "Y looks like it needs a follow-up change Z that
  isn't in this diff." Questions go in their own section, not mixed
  with issues.

Output format:
  ## <Pass name> — <N> issues, <M> questions

  ### Issues
  - **[file:line]** <one-line summary>
    <2-4 line explanation; quote the code; suggest the fix>
    bar: above | borderline

  ### Questions
  - **[file:line or "scope"]** <the question>
    <why this is unclear from the diff alone>

If you have 0 issues, write "### Issues\n_none_" — do not omit the
section. Same for questions.
```

### Pass A — Trust-boundary violations (ADR-002)

```
Lane: violations of the three-process trust boundary defined in
docs/adr/ADR-002-three-process-security-model.md and the Hard Rules
in AGENTS.md.

Above the bar (report):
- App or UA-side package importing Node-side packages (blocknode, dht,
  nodeapi, leasevalidator, signedrecordstore) or vice versa
- Private keys or signing functions appearing in Node-side packages
- Apps constructing CIDs, talking directly to the Node, or holding
  private keys
- Capability URLs or bearer-link sharing (forbidden per ADR-019/069)
- Stubbed crypto in production code paths (Hard Rule: real crypto
  from the start)
- Hand-edits to generated wire-format code

Below the bar (do not report):
- Style nits in trust-boundary-adjacent code
- Missing comments in trust-boundary code
- Refactor suggestions that don't fix a violation

Read the diff at /tmp/review-diff.patch. Cross-reference imports against
the package classification in AGENTS.md. Run
`make check-isolation` mentally if helpful (do not actually run it).
```

### Pass B — Schema, CDDL, and wire-format integrity

```
Lane: CDDL is source of truth (Hard Rule). Schema types are exact.
Never renumber.

Above the bar:
- Wire struct fields hand-edited where they should be generated
- CDDL changes that don't match Go struct changes (or vice versa)
- Renumbered enum values, iota blocks, ADR sections, requirement IDs,
  or document section numbers
- Loosened schema constraints (string instead of fixed-size byte
  array, int instead of bounded uint) without a documented reason
- New wire format introduced without a corresponding .cddl file in
  the owning package

Below the bar:
- Style of CDDL formatting
- Naming preferences in schema fields

Read the diff. Look for *.cddl, generated *.pb.go, struct changes in
wire-adjacent packages. Cross-reference DATA-DESIGN-GUIDELINES.md.
```

### Pass C — Design-vs-implementation drift

```
Lane: when *_design.go (the authoritative module spec, per AGENTS.md
"Design-as-Code") disagrees with the implementation in the same package.

Above the bar:
- Code implements an API shape that contradicts the design file
- Design file was not updated when the implementation diverged
  (per AGENTS.md: "When implementation conflicts with a DRAFT design
  file, update the design file and flag the change")
- New module added without a *_design.go file
- *_design.go contains `// OPEN:` markers that the implementation
  silently picked a default for, rather than resolving in the design

Below the bar:
- Design file phrasing nits
- Design file missing the optional `// Status:` line

Read the diff. For each changed pkg/<x>/, read pkg/<x>/*_design.go
if present and check for drift.
```

### Pass D — Crypto correctness

```
Lane: cryptographic correctness only. Use the project's crypto-reviewer
agent's bar (hardcoded keys, nonce reuse, weak algorithms, missing AEAD,
math/rand for crypto, side-channel branching on secrets, missing
constant-time compare, secrets not zeroed).

Read .claude/agents/crypto-reviewer.md for the full bar.

Above the bar: anything from that list.
Below the bar: code style in crypto packages.
```

(For Pass D specifically, set `subagent_type: "crypto-reviewer"` and
pass it the diff path and the changed crypto-relevant file list.)

### Pass E — Doc routing and architectural changes

```
Lane: facts landing in the wrong document, missing ADRs, broken
project-map.md routing.

Above the bar:
- Architectural change (new module, changed trust boundary, new wire
  format, new sharing model) without a corresponding ADR in
  docs/adr/. AGENTS.md states this is required.
- New user-visible capability without an entry in plan/user-stories.md
- New behavioral SHALL/MAY constraint without entry in
  docs/requirements/requirements.md
- Renamed module/package without updating every ADR that references it
  (AGENTS.md: "ADRs are current-tense and updated in place on rename")
- New fact added to a doc when project-map.md says it belongs elsewhere
- Internal name (shell, social, useragent, node) leaked into a
  user-facing surface, or user-facing name (OurCloud, OurCloud Social)
  used in an engineering artifact

Below the bar:
- Doc typos
- Wording preferences in existing prose

Read project-map.md and AGENTS.md "Hard rules" before starting.
```

### Pass F — General correctness and bugs

```
Lane: bugs that would cause incorrect behavior, data loss, panics, or
security holes — but NOT in any other pass's lane.

Above the bar:
- Race conditions on shared state
- Resource leaks (unclosed files, goroutines, contexts)
- Error swallowed without logging or propagation
- Off-by-one, nil deref, integer overflow, unbounded slice growth
- Logic that doesn't match the commit message's stated intent
- TOCTOU, unchecked authentication assumptions
- Panics in code paths reachable from untrusted input

Below the bar:
- Code style, naming, formatting
- "Could be more idiomatic"
- Performance micro-optimizations without a stated perf requirement

If a finding fits Pass A (trust boundary) or Pass D (crypto), defer to
that pass — do not report it here. Lane discipline matters.
```

### Pass G — Test integrity

```
Lane: tests that don't actually test what they claim, or missing tests
where the project's test policy requires them.

Above the bar:
- Test mocks crypto where AGENTS.md says "real crypto from the start"
- Test asserts a TODO placeholder that was never resolved (per the
  user's testing protocol, this is an OPEN bug, not a passing test)
- Production code change with no test change AND no integration-test
  coverage that exercises the change
- Test that passes regardless of the production behavior under test
  (tautological assertions)
- Integration test added to tests/ but not wired into
  make full-regression
- New IPC surface with no test crossing the process boundary

Below the bar:
- Test naming preferences
- Test could be more concise

Read AGENTS.md "Build & Test" and the user's CLAUDE.md "Testing
Protocol" before starting.
```

### Pass H — Intent and missing follow-ups (questions pass)

```
This pass produces ONLY questions, not issues. Its job is to surface
gaps in intent, not defects in code.

Read the commit messages, PR description (if any), and diff. For each
of these, ask a question:

- A change whose motivation is not explained by the diff or commit
  message ("why is X being changed at all?")
- A change that obviously implies a follow-up change that isn't in
  the diff ("if X moved to package Y, shouldn't Z also move?")
- A change that's half-done — e.g. new function added but no caller,
  flag added but never read, type defined but never used
- A change that conflicts with a recent commit on main, or with an
  ADR, in a way that suggests the author didn't see the conflict
- A reverted change — code that the diff puts back to a state an
  earlier commit moved away from, with no explanation

Output format:

  ## Pass H — Intent (<N> questions)

  ### Questions
  - **[file:line or "scope"]** <the question>
    <one or two lines: what is unclear, why it matters>

If you have 0 questions, write "### Questions\n_none_".

This pass produces NO issues section. Do not invent issues; the other
passes own that.
```

---

## Step 3 — Aggregate (DO NOT re-rank or trim)

Once all passes return, produce the final report in this exact shape:

```
# Review of <scope>

## Summary
- <total issues> issues across <N> passes; <total questions> questions
- Passes with 0 findings: <list>
- Passes with 5+ findings: <list>

## Issues by pass
<paste each pass's Issues section verbatim, in order A-G>

## Questions
<merge Pass H questions with any questions from passes A-G,
preserving file:line attribution>

## Anti-anchor self-check
- Did any pass report exactly 3-7 findings? <yes/no>
  - If yes, was that the natural count or did the pass stop early?
    (Re-read that pass's prompt — did it say "stop at N"? If not,
    trust the count.)
- Were any findings dropped during aggregation? <yes/no — must be no>
- Were findings re-ranked or merged across passes? <yes/no — must be no>
```

The self-check at the end is not theater — it's a reminder to YOU, the
aggregator, that you must not have re-introduced the anchor.

---

## Step 4 — Offer next actions

After the report, ask the user (do not assume):

- "Want me to fix any of these? Tell me which by number/lane."
- "Want me to dig into any of the questions before fixing?"

Do not start fixing without confirmation. The user's
`feedback_qa_mode.md` memory says information-gathering asks stay in
report-only mode.
