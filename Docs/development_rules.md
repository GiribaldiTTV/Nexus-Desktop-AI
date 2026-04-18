# Nexus Development Rules

## Core Principles

- Analyze first
- Validate live repo truth before making lane, branch, merge, or release recommendations
- One coherent approved change per revision
- Preserve architecture boundaries
- Logs, code, and merged docs are the source of truth for implemented behavior
- No silent scope expansion
- No silent backlog or policy drift

## Analysis-First Operating Posture

Codex is a full-scan analyst before it becomes an executor.

That means Codex must:

- scan broadly enough to understand the whole affected system
- validate current repo truth
- surface drift, risk, dependencies, and options
- only narrow scope after the analysis is complete and the user approves execution boundaries

Execution language such as:

- `minimal`
- `smallest safe slice`
- `narrow`
- `single patch`

belongs to execution planning after analysis, not to the initial investigative posture.

Short prompts, shorthand cues, or mode-only requests do not waive source-of-truth reading.

## Live-State Validation Gate

Before recommending the next move after a merge, release, or major lane transition, validate:

- current branch
- local `main` versus `origin/main`
- whether referenced PRs are actually merged
- whether referenced branches still exist
- latest public tag or release versus current `main`
- whether docs and canon reflect live repo truth

If prompt framing is stale, report the real state first and plan from that state.
If no legal branch may execute, report `No Active Branch` and the blocking repair path instead of inventing a later phase.

## Source-Of-Truth Ownership Model

Use this layered ownership model:

- backlog = identity and registry
- workstream docs = promoted-work feature-state, branch-local evidence, active seam references, artifact history, branch-local reuse notes, and closure history
- roadmap = sequencing and release posture
- rebaselines and closeouts = epoch or milestone summaries
- incident patterns = generalized reusable lessons
- bugs = backlog-first, with promoted bug docs only when warranted
- User Test Summary = validation-contract layer owned by workstreams
- phase governance = repo-wide execution, exact phase enum, blockers, branch classes, proof, timeout, seam, stop-loss, validation-helper, Governance Drift Audit, phase resolver, and desktop UI audit contract
- `Docs/Main.md` = routing authority aligned to merged truth

Use `Docs/phase_governance.md` for:

- named execution phases
- blocker rules and branch classes
- phase entry and exit rules
- rollback and next-legal-phase rules
- proof authority rules
- interactive timeout governance
- validation helper rules
- desktop UI audit rules
- truth-drift enforcement
- governed closeout stop-loss rules

Use these lifecycle fields:

- `Status` = delivery or work state
- `Record State` = canonical-record lifecycle

Allowed `Record State` values are:

- `Registry-only`
- `Promoted`
- `Closed`

Rules:

- if `Record State` is not `Registry-only`, `Canonical Workstream Doc` must exist
- closed workstream docs stay at stable paths
- backlog and roadmap must not continue carrying the full execution story once a canonical workstream doc exists
- workstream docs must not silently redefine repo-wide phase or proof-governance rules that belong to `Docs/phase_governance.md`

Record-state meaning:

- `Registry-only` = backlog identity exists, but no canonical workstream execution record is required yet
- `Promoted` = a canonical workstream doc is required and becomes the durable branch record that must stay current throughout the active lane
- `Closed` = the canonical workstream doc remains historical lane truth and must not be treated as active execution authority by inertia

## Required Startup Contract

Before planning, patching, reviewing, or recommending the next move, Codex must follow the canonical startup contract in `Docs/Main.md`.

That startup pass must make explicit:

- source-of-truth layer selection
- `Record State` when the task maps to a tracked item
- current branch truth and whether the branch is the correct execution base
- the canonical workstream doc when one exists
- the reuse baseline
- the next safe move

## Exact Prompt Contract And Phase Resolver

Every phase-sensitive execution prompt must include:

- `Mode`
- `Phase`
- `Workstream`
- `Branch`

Add these when relevant:

- `Branch Class`
- `Active Seam`
- `Validation Contract`
- `Timeout Contract`

If `Phase` is missing or is not one of the exact canonical phase names from `Docs/phase_governance.md`, execution is blocked and only truth-validation or analysis may continue.

Before answering “what phase are we in?” or “what’s next?”, run the phase resolver from `Docs/phase_governance.md` and return:

- `Current Phase`
- `Phase Status`
- `Branch Class`
- `Blockers`
- `Governance Drift Found`
- `Next Legal Phase`
- `Plan To Reach That Phase`

## Branch And Lane Governance

PR-readiness is not the default checkpoint after a clean slice.

Default checkpoint:

- branch-level lane evaluation

Stay inside the active grouped lane until one of these is true:

- the milestone threshold is satisfied
- a real blocker appears
- the next work crosses subsystem boundaries
- the user explicitly stops

After a lane is closed or merged:

- the next workstream must execute from updated `main` on a fresh branch
- the successor branch may be created during `PR Readiness`, but it remains reserved and may not be used for execution until the current branch merges and the successor branch is revalidated against updated `main`

If a branch becomes:

- stale
- merged
- identical to `main`

Codex must call that out explicitly and recommend a fresh branch from updated `main`.

Before any next branch may enter `Branch Readiness`, the repo-level admission gate from `Docs/phase_governance.md` must pass.

If the admission gate fails:

- repo state becomes `No Active Branch`
- no next implementation branch may begin
- the next safe move is blocker repair, not next-lane execution

For active promoted work, the canonical workstream doc is the single authoritative owner of:

- `Current Phase`
- `Phase Status`
- `Branch Class`
- `Blockers`
- `Entry Basis`
- `Exit Criteria`
- `Rollback Target`
- `Next Legal Phase`

Backlog, roadmap, and prompt text may reference phase state, but they must not override the workstream doc.

## Canon Freshness Rules

Supporting canon must stay aligned with live truth.

That means:

- directly supporting canon may be updated on the active implementation branch when that branch changes the truth
- no PR-ready without canon-ready:
  - a branch is not PR-ready if merging it would leave `main` canon-stale
- when a branch closes a workstream, changes released milestone posture, changes the current rebaseline, changes closeout-index routing, changes backlog or roadmap release posture, changes workstream-index release posture, or changes `Docs/Main.md` baseline routing, the required release-facing canon updates must already be on that branch before PR creation is allowed
- no PR-ready without successor branch created:
  - If post-merge truth will resolve to `No Active Branch` because `Release Debt` or another repo-level admission blocker remains open, successor-lane selection and reserved successor-branch creation are waived for that PR-readiness pass.
  - the next workstream must be selected from canon
  - that workstream must have canon-valid `Record State`
  - a fresh successor branch must already be created using an approved naming family such as `feature/<lane>`, `fix/<issue>`, or `docs/<lane>`
  - that successor branch must remain reserved until the current branch merges and the successor branch is revalidated against updated `main`
  - when that waiver applies, the branch must instead record `No Active Branch` plus the blocking admission item explicitly in merged current-state canon
- post-release canon repair is emergency-only:
  - use it only when canon drift already exists on updated `main` and could not be prevented before merge or release
- do not default to a standalone docs-only post-release branch for routine canon completion
- do not use canon sync as an excuse for broad unrelated documentation churn

Local docs overlays are reference material only until revalidated against updated `origin/main`.

Time-sensitive current-state claims must live only in designated current-state owners, or be part of the merge-target canon update set.

Allowed current-state owners are:

- backlog
- roadmap
- active workstream doc
- workstreams index
- closeout index
- current rebaseline or closeout file
- `Docs/Main.md` routing

Auxiliary guidance docs should be timeless by default.
If they carry live-current claims, they must either be updated as part of canon sync or stop owning current-state truth.

## Governance Drift Rule

If a branch exposes a governance weakness such as:

- a missing blocker
- a weak phase entry or exit rule
- a weak source-of-truth ownership rule
- stale prompt scaffolding or stale examples
- a missing validator requirement

that weakness must be classified as `Governance Drift`.

If governance drift is discovered:

- stop normal progression immediately
- either fix it inside the approved governance or docs boundary, or
- produce the exact required canon delta and wait for user confirmation

Do not defer known governance weaknesses silently to a later branch.

When a branch changes:

- repo-wide phase governance
- current-state owners
- prompt scaffolds
- active promoted workstream phase-state records

it must also run:

- `python dev/orin_branch_governance_validation.py`

and keep that validator green before calling the branch ready.

## Change Discipline

- one fix per revision means one coherent approved subproblem per revision
- minimal isolated changes means the minimal coherent change set needed to close that approved subproblem
- grouped workstreams are allowed during `pre-Beta` when they remain coherent by subsystem and end-state
- a grouped branch may carry multiple validated slices when they all belong to the same milestone
- unrelated ideas must still be split out even if they look convenient to batch

Use the smallest safe slice for:

- architecture clarification
- boundary-setting
- high-risk behavior or policy work

Use the smallest coherent slice for:

- lower-risk follow-through inside an already-approved milestone when a smaller fragment would leave the milestone incomplete

These are execution rules, not analysis-stop rules.

## Testing And Validation

Every revision must include:

- healthy-path verification
- failure or edge-case verification when relevant
- runtime log review
- crash log review when present
- artifact cleanup verification when relevant
- session cleanup verification when relevant

Interactive validation must also be time-budgeted.
Codex must not allow stalled validation runs, harnesses, or desktop exercises to sit indefinitely.

When the branch is in governed closeout recovery, `Docs/phase_governance.md` is the controlling timeout and stop-loss authority unless the active workstream doc explicitly documents a tighter contract.

When an interactive validation pass is relevant, it must use:

- a full-run hard timeout
- a no-progress watchdog timeout
- scenario and/or transition budgets where the flow has distinct multi-step seams
- an outer execution timeout that sits only slightly above the interactive harness hard cap rather than extending it by many additional minutes

For meaningful interactive desktop closeout work, helpers should also follow the repo-wide validation helper contract from `Docs/phase_governance.md`.
That means:

- marker-first proof by default
- explicit separation of gating and non-gating observations
- runtime helper support when it materially improves deterministic startup or runtime logging
- watchdog enforcement plus last-progress logging
- cleanup guarantees
- saved-state or source snapshots when write safety or no-write blocking behavior matters
- live re-resolution of windows, dialogs, overlays, and controls across close/open seams
- seam classification before product code is changed during validation hardening

When the approved boundary is a continuous `Hardening` pass on the current branch, Codex should keep iterating through seams without waiting for a new user prompt after every rerun unless:

- a blocker appears
- truth drift appears
- stop-loss is reached
- canon sync becomes required before the next rerun

Do not claim closeout-grade green status from a helper profile that only passed under one-off command-line overrides.
The helper's documented default profile must itself prove green before that branch can be treated as truly green.

If a timeout or freeze is detected, Codex must:

- abort cleanly rather than letting the run continue indefinitely
- perform the required session cleanup
- explicitly report the timeout or stall condition
- explicitly report the last confirmed meaningful progress point

For hardened desktop helpers, the working target is not just eventual completion.
The working target is also responsiveness:

- no-progress or transition waits should normally stay within `3s`
- normal seam or scenario completion should normally stay within `60s`
- if a helper keeps needing longer waits, patch the proof path or helper design rather than silently normalizing the delay

If the timeout contract in the active workstream doc and the live harness behavior drift apart, the workflow is blocked until that drift is reconciled in canon before continued execution is recommended.

After any validation run, test pass, runtime exercise, harness execution, or other operational step, Codex must also clean up what it created or opened during that session unless there is a deliberate reason to preserve it.

This is not satisfied by a best-effort attempt alone. Before handoff, Codex must explicitly verify that the cleanup actually happened for the apps, windows, dialogs, helper processes, temporary files, probe documents, and other session-scoped artifacts it opened, started, or created during the pass.

That includes, when relevant:

- closing programs, dialogs, or windows Codex opened
- stopping helper processes, harnesses, validators, or temporary runtimes Codex started
- deleting temporary files, temporary documents, scratch outputs, or probe files Codex created only for the pass
- restoring source files, settings, or local state Codex intentionally modified for the test
- confirming the machine or workspace is not left in a noisier or more invasive state than necessary for the user
- verifying that user-visible apps or windows opened for the pass, such as Notepad or File Explorer windows, are actually closed rather than assumed closed

If something created during the pass must remain on disk or stay open intentionally, Codex must say so explicitly and explain why it was preserved.

Before handing a user-visible runtime, UI, or manual validation path back to the user, Codex must run that same path or the closest faithful equivalent when feasible.

For relevant desktop, runtime, user-facing, or operator-facing slices, if the implemented path can be launched and exercised through a real desktop session in the current environment, true interactive OS-level validation is the default continuation gate.

In that case:

- validator results remain baseline automated proof
- synthetic or headless harnesses remain stronger supporting proof
- a real interactive OS-level session is the required gate before Codex recommends normal continuation
- manual user handoff remains an additional operator layer, not a substitute for Codex's own feasible interactive validation

If Codex cannot self-run the same path reliably, it must say so explicitly and identify the remaining validation gap.

When a slice materially changes user-facing desktop UI, Codex must also plan a post-green live launched-process UI audit before closeout.
That audit is a closeout-quality check, not a screenshot requirement for every seam iteration.

For runtime, UI, startup, prompt, voice, or other operator-facing implementation slices, green validators are necessary but not sufficient on their own.

Before continuing to the next implementation slice on the same branch, Codex must also perform a deeper branch-local validation and hardening pass that:

- pressure-tests the implemented path and its likely failure modes
- checks integration seams and branch-local regressions beyond the happy path
- adds or creates the smallest reliable validation infrastructure on-branch when the current suite leaves meaningful blind spots
- uses supporting validation artifacts when needed, such as validators, harnesses, fixtures, scripted helpers, trace capture, screenshots, runtime logs, or reproducible sample inputs
- uses synthetic or headless validators and harnesses as supporting evidence rather than the final continuation gate when a real desktop session is feasible
- launches and exercises the real desktop or runtime path through an interactive OS-level session when feasible rather than stopping at simulated reasoning or headless proof
- preserves evidence of what was run, what passed or failed, and where the supporting artifacts live
- explicitly distinguishes:
  - validator results
  - synthetic or headless validation results
  - simulated reasoning or inspection findings
  - interactive OS-level execution results
  - manual user-test handoff that still remains
- explicitly decides whether the correct next move is:
  - continue implementation
  - pause for internal hardening or validation
  - or fix a specific defect first

Validator-green status plus simulated reasoning, recap-style summary, or synthetic/headless harness results is not enough when the implemented desktop or runtime path can be exercised through a real interactive OS-level session.

When Codex recommends continuing implementation after a user-visible slice, it must be able to explain why the current validation and hardening depth is already sufficient for that continuation.

If the current validation surface is too thin to support that explanation, Codex must first add the smallest reliable validation infrastructure on-branch and re-run the validation pass before continuing.

If a real interactive OS-level session is not feasible, Codex must say so explicitly, explain why, cite the strongest available non-interactive evidence, and state that the continuation recommendation is limited by the missing interactive gate.

When a slice changes user-visible behavior, runtime interaction, UX flow, prompts, startup behavior, voice behavior, or any manual operator-facing path, Codex must include a true manual validation checklist under `## User Test Summary` by default.

That checklist must include:

- setup or prerequisites
- exact user actions
- expected visible behavior
- failure signs to watch for
- branch-specific or slice-specific validation focus

A recap-style summary is not sufficient when manual validation is relevant.

If no meaningful manual test exists for the change, Codex must say so explicitly under `## User Test Summary` and explain why manual validation is not materially relevant for that slice.

For active desktop workstreams, the default canonical repo-level `UTS` artifact is the `## User Test Summary` section in the relevant canonical workstream doc unless that doc explicitly declares a different repo path.

When that artifact exists and supporting docs are in scope on the active branch, Codex must update it as part of the same slice by default.

Response-only `## User Test Summary` output does not satisfy the workstream-owned validation layer when the canonical repo artifact remains stale.

For desktop user-facing slices, Codex must also export or refresh the convenience copy at:

- `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt`

unless it explicitly explains why the desktop export is not relevant or is being intentionally skipped.

The ownership hierarchy is:

- workstream doc `## User Test Summary` section = canonical repo source of truth
- desktop `User Test Summary.txt` = required user-facing exported copy when relevant
- response-level `## User Test Summary` = current handoff text only

If Codex does not update the canonical repo-level `UTS` artifact, it must say explicitly why. Valid reasons are limited to:

- no meaningful manual test exists for the slice
- no canonical workstream doc exists yet for the active lane
- the user explicitly restricted the pass so the relevant artifact could not be updated
- the relevant closed workstream doc already says that no separate ongoing `UTS` artifact remains

If Codex does not export or refresh the desktop `User Test Summary.txt` copy for a relevant desktop slice, it must also say explicitly why.

Returned evidence such as `UTS`, screenshots, interactive reports, PR review comments, or release-review findings may satisfy exit criteria, but they must never auto-advance phase by implication.

Required sequence:

1. digest the evidence
2. update the authority record
3. reevaluate blockers
4. only then advance phase

## Runtime Evidence And Logging

- logs are the source of truth for runtime behavior
- do not assume behavior without log or code evidence
- prefer structured markers over raw output
- preserve or cite the exact validator outputs, helper scripts or harnesses used, runtime logs reviewed, and any created fixtures, traces, or screenshots that materially support a continuation recommendation
- when interactive OS-level validation is required and feasible, preserve or cite the exact session evidence that shows the real path was exercised, such as runtime logs, screenshots, structured markers, traces, or durable validation reports
- when meaningful desktop UI changed and a live launched-process UI audit was required, preserve or cite the audit manifest and the key captured windows as part of the final closeout evidence
- when the user wants to visually validate those screenshots inside the Codex client, do not rely on local-file image embeds as the default delivery path; keep the original audit captures on disk and use the client-compatible preview path documented in `Docs/codex_user_guide.md`
- the default client-compatible preview path is: preserve the original live capture on disk, generate a smaller derivative from that real file, and send one small inline PNG `data:` image at a time until render reliability is confirmed
- do not claim live-style validation without evidence or a specific explanation of what path was actually exercised

### Root Logs Governance

- `C:/Jarvis/logs` and `C:/Jarvis/logs/crash` remain reserved for approved live launcher and runtime truth surfaces only
- launcher-owned historical state is not a root-owned live logs surface
- normal runtime historical state resolves under `%LOCALAPPDATA%/Nexus Desktop AI/state/jarvis_history_v1.jsonl`
- dev, test, worker, and toolkit evidence must write under `C:/Jarvis/dev/logs/<lane>/...`
- no new dev or worker evidence roots may be introduced under `C:/Jarvis/logs` without explicit approval

### Dev-Only Startup Snapshot Harness

For startup-state debugging, Codex may use the env-gated startup snapshot harness when it is the smallest reliable evidence path.

Rules:

- the harness must remain opt-in through `JARVIS_HARNESS_STARTUP_SNAPSHOT_DIR`
- snapshot output must write to an explicitly chosen dev evidence path, not root logs
- the harness is internal debugging infrastructure only
- if the harness is not needed for the active task, leave it disabled

## Historical Intelligence Rules

Cross-run intelligence must stay contract-defined in repo docs before implementation changes begin.

That contract must define:

- schema and versioning
- run identity
- failure fingerprint rules
- provenance labeling
- retention and reset behavior
- corruption and fallback behavior

Historical intelligence must remain explainable and deterministic rather than becoming a second hidden truth source.

## Documentation And Carry-Forward Review

Important architecture, orchestration, planning, and validation decisions should live in repo docs rather than only in chat history.

For every post-merge, post-release, or next-lane review, classify prior recommendations as:

- carry forward
- defer
- discard

Never treat prior suggestions as automatic scope.

For every `PR Readiness` pass, also run the formal Governance Drift Audit from `Docs/phase_governance.md`.
If that audit finds required canon strengthening, do not silently merge past it.

Use `Docs/Main.md` as the routing index for the merged canon.

## Backlog Governance

`Docs/feature_backlog.md` is a controlled registry layer.

Codex may:

- propose backlog changes
- draft exact backlog markdown for approval
- carry approved state changes during an explicitly authorized docs pass

Codex may not:

- silently add backlog items
- silently change priority or status outside approved work
- silently mark work complete because a branch merely looks clean

## Relationship To `Docs/orin_task_template.md`

`Docs/orin_task_template.md` remains the per-task execution scaffold.

This document defines repo-wide rules.
The task template defines the structure of a specific request.
