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
- a distinct summary of validator results
- a distinct summary of synthetic or headless validation results and the supporting validation artifacts created or used
- a distinct summary of interactive OS-level execution results when that path is feasible
- any remaining simulated-only findings or reasoning-only gaps that still matter
- deeper branch-local validation or hardening findings when the slice changes runtime or user-visible behavior
- a detailed `## User Test Summary` manual checklist when the slice changes user-visible behavior, runtime interaction, UX flow, prompts, startup behavior, voice behavior, or another operator-facing path
- the updated canonical repo-level `UTS` artifact when the active workstream owns one and the slice makes that artifact relevant
- the exported or refreshed desktop `User Test Summary.txt` copy when the slice is a relevant desktop user-facing path, or an explicit explanation of why that export was skipped
- an explicit statement under `## User Test Summary` when no meaningful manual test exists and why
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

For desktop workstreams, response-level `## User Test Summary` output and the canonical repo-level `UTS` artifact are related but not interchangeable:

- the response section is the current handoff copy
- the workstream-owned repo artifact is the durable canonical record unless the workstream explicitly declares another repo path
- the desktop `User Test Summary.txt` file is the required user-facing exported copy when relevant, but it is not the default canonical repo record

When manual validation is relevant, `## User Test Summary` must be a real checklist rather than a recap.

It should include:

- setup or prerequisites
- exact user actions
- expected visible behavior
- failure signs to watch for
- branch-specific or slice-specific validation focus

For runtime or user-visible implementation slices, green validators alone do not authorize automatic continuation.

When a relevant desktop or runtime path can be launched and exercised through a real desktop session in the current environment, synthetic or headless validation does not authorize continuation on its own either.

Codex must also:

- run a deeper branch-local hardening pass against the implemented path
- add or create the smallest reliable validation infrastructure when meaningful blind spots remain
- preserve an evidence trail of the validators, harnesses, helper scripts, fixtures, runtime logs, traces, screenshots, or other validation artifacts actually used
- use synthetic or headless validators and harnesses as supporting proof rather than the final gate when a real desktop session is feasible
- launch and exercise the real desktop or runtime path through an interactive OS-level session when feasible
- explicitly distinguish validator results, synthetic or headless validation results, simulated reasoning, interactive OS-level execution results, and manual user-test handoff
- make an explicit next-step call between continue, harden, or corrective fix

If that interactive path is not feasible, Codex must explain why, use the strongest available non-interactive evidence, and state that the continuation judgment is limited by the missing interactive validation.

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
