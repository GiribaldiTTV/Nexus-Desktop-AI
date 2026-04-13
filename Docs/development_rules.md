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

## Source-Of-Truth Ownership Model

Use this layered ownership model:

- backlog = identity and registry
- workstream docs = planning, execution, validation, and closure truth for promoted work
- roadmap = sequencing and release posture
- rebaselines and closeouts = epoch or milestone summaries
- incident patterns = generalized reusable lessons
- bugs = backlog-first, with promoted bug docs only when warranted
- User Test Summary = validation-contract layer owned by workstreams
- `Docs/Main.md` = routing authority aligned to merged truth

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

## Branch And Lane Governance

PR-readiness is not the default checkpoint after a clean slice.

Default checkpoint:

- branch-level lane evaluation

Stay inside the active grouped lane until one of these is true:

- the milestone threshold is satisfied
- a real blocker appears
- the next work crosses subsystem boundaries
- the user explicitly stops

After a lane is closed:

- the next workstream must start from updated `main` on a fresh branch

If a branch becomes:

- stale
- merged
- identical to `main`

Codex must call that out explicitly and recommend a fresh branch from updated `main`.

## Canon Freshness Rules

Supporting canon must stay aligned with live truth.

That means:

- directly supporting canon may be updated on the active implementation branch when that branch changes the truth
- after a release, Codex should normally validate updated `main`, select the next plausible workstream, create a fresh compliant branch for that workstream, and perform any required post-release canon sync at the start of that branch before implementation begins
- do not default to a standalone docs-only post-release branch when a plausible next workstream can already be selected safely from current truth
- standalone docs-only canon reconstruction is exception-only when no plausible safe next implementation lane can be selected yet, or when current canon drift is misleading enough that branch selection itself would be untrustworthy
- if a plausible next workstream exists, Codex must block standalone post-release docs execution and require fresh-branch selection first
- do not use canon sync as an excuse for broad unrelated documentation churn

Local docs overlays are reference material only until revalidated against updated `origin/main`.

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

Before handing a user-visible runtime, UI, or manual validation path back to the user, Codex must run that same path or the closest faithful equivalent when feasible.

For relevant desktop, runtime, user-facing, or operator-facing slices, if the implemented path can be launched and exercised through a real desktop session in the current environment, true interactive OS-level validation is the default continuation gate.

In that case:

- validator results remain baseline automated proof
- synthetic or headless harnesses remain stronger supporting proof
- a real interactive OS-level session is the required gate before Codex recommends normal continuation
- manual user handoff remains an additional operator layer, not a substitute for Codex's own feasible interactive validation

If Codex cannot self-run the same path reliably, it must say so explicitly and identify the remaining validation gap.

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

## Runtime Evidence And Logging

- logs are the source of truth for runtime behavior
- do not assume behavior without log or code evidence
- prefer structured markers over raw output
- preserve or cite the exact validator outputs, helper scripts or harnesses used, runtime logs reviewed, and any created fixtures, traces, or screenshots that materially support a continuation recommendation
- when interactive OS-level validation is required and feasible, preserve or cite the exact session evidence that shows the real path was exercised, such as runtime logs, screenshots, structured markers, traces, or durable validation reports
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
