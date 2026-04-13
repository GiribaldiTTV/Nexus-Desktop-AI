# Nexus Codex Modes

## Purpose

This document defines the collaboration posture Codex should use while handling Nexus Desktop AI tasks.

It works with:

- `Docs/development_rules.md`
- `Docs/Main.md`
- `Docs/orin_task_template.md`

If those sources conflict, live repo truth and the higher-order governance docs win.

## Why Two Modes Exist

Nexus work benefits from two different postures:

- one for deep truth-mapping, drift analysis, and next-move determination
- one for carrying an approved task through execution and verification

The modes should not be confused.
Analysis mode exists to understand the whole system first.
Workflow mode exists to execute approved work without silent scope drift.

## Analysis Mode

### Goal

Map the real current state of the system before deciding what should happen next.

### When To Use It

Use Analysis mode when the user asks for:

- drift review
- post-release or post-merge review
- workstream planning
- readiness analysis
- sequencing analysis
- source-of-truth audit
- next-lane determination

### What Codex Should Do

In Analysis mode, Codex should:

- validate current repo truth first
- scan broadly enough to understand the whole affected system
- compare code, docs, branches, tags, and release facts where relevant
- identify factual drift, structural drift, and authority drift
- classify prior suggestions as carry-forward, defer, or discard
- determine the correct next workstream-level move

### Required Analysis Depth

Analysis mode should reason at:

- system level
- lane level
- workstream level
- document-ownership level

Do not narrow to the first apparent slice before full drift and dependency mapping is complete.

### What Codex Must Not Do

In Analysis mode, Codex must not:

- default into implementation
- assume PR, merge, release, or closure is the next move
- compress the task into the smallest possible pass before understanding the system
- treat local unmerged overlays as merged truth

### Expected Outputs

Analysis mode should usually return:

- validated current truth
- key drift findings
- structural assessment
- sequencing options
- one recommended next workstream move

## Workflow Mode

### Goal

Execute an approved task faithfully, verify it, and keep the resulting truth coherent.

### When To Use It

Use Workflow mode when the user has already approved:

- a docs-only pass
- a bounded patch
- a canon sync
- a workstream closure pass
- another clearly bounded execution task

### What Codex Should Do

In Workflow mode, Codex should:

- validate live repo truth before editing
- stay inside the approved execution boundary
- make the required changes
- verify the changed behavior or changed docs
- report any drift or remaining gaps honestly

### What Codex Must Not Do

In Workflow mode, Codex must not:

- silently widen scope
- silently start a new workstream
- silently create PR, merge, release, or closure output without current-truth justification
- treat a clean first slice as automatic branch readiness

### Expected Outputs

Workflow mode should usually return:

- changes applied
- validation performed
- remaining drift or known gaps
- whether the approved phase is complete

## Workstream And Branch Governance

### Grouped Workstreams

During `pre-Beta`, grouped workstreams are allowed when they remain coherent by subsystem and end-state.

That means:

- one branch may host multiple validated slices for one milestone
- grouped workstreams should not become grab-bags of unrelated ideas
- lane evaluation should stay milestone-driven rather than slice-driven

### Milestone Gate

Before treating a non-doc implementation branch as ready, Codex should be able to explain:

- the lane milestone target
- the minimum merge-ready threshold
- the milestone value statement
- the same-branch follow-through that still belongs inside the lane

### Worthwhile Milestone Gate

For a non-doc implementation branch, Codex should not recommend readiness until:

- the threshold is reached
- the branch is still worthwhile if squashed today
- the remaining obviously coupled slices are no longer required

### Release-Debt Gate

If `main` already contains merged unreleased non-doc implementation work beyond the latest public prerelease, treat that as release debt.

While release debt exists, the default next move is usually:

- release review
- release prep
- directly needed docs support

not another unrelated implementation lane.

### Fresh Branch Start After A Closed Workstream

After a workstream is merged and closed, the next workstream should start from updated `main` on a fresh branch.

If a branch is stale, merged, or identical to `main`, call it out explicitly and stop using it as the base for next-lane planning.

### Post-Release Canon Repair

Release-dependent truth sometimes changes after the code lane is already closed.

When that happens:

- carry the canon sync on the active lane when that lane is still open
- if the lane is already closed, normally validate updated `main`, select the next plausible workstream, create its fresh branch, and perform the post-release canon sync at the start of that branch before implementation begins
- do not default to a standalone docs-only post-release canon pass when a plausible next implementation lane can already be selected safely
- use a standalone docs-only canon pass only as an explicit exception when no plausible safe next implementation lane can yet be selected, or when current canon drift makes branch selection itself untrustworthy

## Shared Rules Across Both Modes

- analyze before changing anything
- verify exact behavior or doc alignment before editing
- preserve architecture boundaries
- call out source-of-truth conflicts explicitly
- backlog owns identity
- roadmap owns sequencing
- workstream docs own promoted-work execution and closure truth
- User Test Summary belongs to workstream-owned validation
- incident patterns are generalized knowledge, not case history

## Live-State Readiness Sanity Check

Before generating any readiness, PR, merge, or release recommendation, validate:

- current branch truth
- branch merge state
- tag or release state
- dirty worktree risk
- whether the prompt framing is stale

If the framing is stale, report the real state instead of producing a hypothetical package.

## Prompt Hygiene

When a canonical workstream or rebaseline doc exists, prompts should prefer that canonical doc over a stack of superseded slice docs.

This does not mean shrinking analysis depth.
It means reducing duplicated prompt inputs once authority is clear.

## Practical Rule Of Thumb

If the user is asking:

- what is true now
- what drift exists
- what should happen next
- whether the current branch is still the right base

start in Analysis mode.

If the user is asking:

- execute this approved docs-only phase
- implement this approved patch
- carry this approved workstream closure or canon sync

use Workflow mode.
