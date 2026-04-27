# Branch Authority Record: feature/fb-048-active-session-relaunch-signal-failure-and-wait-timeout-truth

## Branch Identity

- Branch: `feature/fb-048-active-session-relaunch-signal-failure-and-wait-timeout-truth`
- Workstream: `FB-048`
- Branch Class: `implementation`

## Purpose / Why It Exists

This branch record owns FB-048 `Branch Readiness` while the backlog item remains `Registry-only` and before a promoted canonical workstream record exists.

This pass closes FB-047 post-release canon on the next legal `feature/` branch surface, advances latest public prerelease truth to `v1.6.11-prebeta`, clears merged-unreleased release debt, and admits the first bounded runtime/user-facing relaunch signal-failure and wait-timeout truth slice without promoting FB-048 before `Workstream`.

Historical traceability note: `feature/fb-046-post-merge-canon-sync` was a bounded repair-only post-merge canon-sync branch only and did not imply FB-046, FB-047, or FB-048 Branch Readiness admission or active branch truth.

## Current Phase

- Phase: `Branch Readiness`

## Phase Status

- Repo State: `Active Branch`
- Current Active Branch: `feature/fb-048-active-session-relaunch-signal-failure-and-wait-timeout-truth`
- Current Active Branch Authority Record: `Docs/branch_records/feature_fb_048_active_session_relaunch_signal_failure_and_wait_timeout_truth.md`
- Current Active Canonical Workstream Doc: `None`
- Latest Public Prerelease: `v1.6.11-prebeta`
- Latest Public Release Commit: `4ca70572fbc8033bc96fcd299dd309464e81393a`
- Latest Public Prerelease Publication: `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.11-prebeta`
- Latest Public Prerelease Title: `Pre-Beta v1.6.11`
- FB-047 is now `Released / Closed` historical proof in `v1.6.11-prebeta`.
- Merged-unreleased release debt is clear after publication, validation, and post-release canon closure.
- FB-048 remains `Registry-only`; Branch Readiness is the active phase on this branch; promotion is deferred until actual `Workstream` execution begins.
- Active seam: `None.` Branch Readiness is complete and WS-1 is admitted.

## Branch Class

- `implementation`

## Blockers

None. Post-release closure prerequisites are satisfied, updated-main release proof is already green, and the first bounded relaunch failure-path slice is admitted.

## Entry Basis

- `v1.6.11-prebeta` is published and validated at `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.11-prebeta` on target commit `4ca70572fbc8033bc96fcd299dd309464e81393a`.
- FB-047 is live released, and release debt is clear after publication, validation, and post-release canon closure.
- Updated-main revalidation is green after FB-047 Release Readiness and live release validation.
- Accepted relaunch success and declined relaunch preservation are already first-class proven surfaces on the released runtime family.
- What is still missing is equally truthful proof for the accepted incoming-launch failure lane: when relaunch signaling fails or the active session does not release before the reacquire wait deadline, the repo still needs explicit ownership and outcome truth instead of a generic failure-or-timeout story.
- A new `feature/` branch is the legal active surface because `main` is protected and no promoted implementation branch remains active after FB-047 release closure.

## Exit Criteria

- latest public prerelease truth advances to `v1.6.11-prebeta` in active canon
- FB-047 closes as released historical truth, and merged-unreleased release debt clears
- FB-048 owns a bounded runtime/user-facing slice on a normal `feature/` branch while remaining `Registry-only` during Branch Readiness
- the admitted slice records exact affected paths, validation coverage, rollback conditions, and same-branch backlog-completion posture
- Branch Readiness resolves without widening into `main.py`, `Audio/`, `logs/`, `jarvis_visual/`, installer work, or broader boot-orchestrator implementation

## Rollback Target

- `Branch Readiness`

## Next Legal Phase

- `Workstream`

## Branch Objective

- close FB-047 post-release canon on the next legal active branch surface
- admit the smallest runtime-bearing FB-048 slice that proves accepted relaunch failure paths stay truthful when signal delivery fails or the active session does not release before the reacquire wait deadline
- preserve selected-only Branch Readiness truth until promotion is warranted by actual Workstream execution

## Target End-State

- current-state canon shows FB-047 as `Released / Closed` historical proof in `v1.6.11-prebeta`
- FB-048 remains selected-only on this branch until `Workstream` begins
- `Workstream` can start on real accepted-relaunch failure-path proof instead of a vague future-planning label
- same-branch backlog completion remains the default unless only future-dependent blockers remain

## Backlog Completion Strategy

Branch Completion Goal: `Complete FB-048 on this same branch unless only future-dependent blockers remain after the remaining implementable relaunch signal-failure and wait-timeout work is exhausted.`
Known Future-Dependent Blockers: `None proven during Branch Readiness.`
Branch Closure Rule: `Do not leave Workstream after WS-1 while more implementable FB-048 work remains; exit Workstream only when Backlog Completion State becomes Implemented Complete or Implemented Complete Except Future Dependency.`

## Affected Surface Ownership

- `desktop/single_instance.py`: accepted relaunch prompt outcome handling, relaunch signal delivery, single-instance wait semantics, and guard-ownership truth when signal delivery fails or release wait expires
- `desktop/orin_desktop_launcher.pyw`: truthful incoming-launch failure classification, explicit failure-path breadcrumbs, and correct ownership/result reporting when replacement never becomes active
- `desktop/orin_desktop_main.py`: active-session release or non-release breadcrumbs if minimal runtime proof needs an explicit renderer-side marker for the failure lane
- `dev/orin_desktop_entrypoint_validation.py`: reusable production-path proof owner for accepted relaunch failure, signal-failure, and wait-timeout truth without masking ownership with cleanup
- `dev/orin_boot_transition_verification.py`: reusable explicit dev-boot proof owner if accepted failure-path lifecycle truth must stay aligned across proof families

## Expected Seam Families And Risk Classes

- relaunch-signal delivery family; risk class: the incoming launch may request relaunch but fail to notify the active session, leaving ownership ambiguous
- reacquire wait-timeout family; risk class: the active session may receive a relaunch request but fail to release before the incoming launch gives up, and the repo may overclaim successor state anyway
- guard-ownership truth family; risk class: failure-path logs may leak release, reacquire, or replacement-session success markers even though ownership never transferred
- validation alignment family; risk class: accepted success, decline preservation, and accepted failure may drift into three different classification languages instead of one truthful lifecycle model

## Planning-Loop Guardrail

Implementation Delta Class: `runtime/user-facing`
Docs-Only Workstream: `No`
Planning-Loop Bypass User Approval: `None`
Planning-Loop Bypass Reason: `None`

- FB-048 is an implementation branch and this Branch Readiness pass admits a real runtime-bearing slice instead of a planning-only continuation.

## Slice Continuation Policy

Slice Continuation Default: `Same-branch backlog completion`
Backlog-Split User Approval: `None`
Backlog-Split Reason: `None`

- WS-1 is the first admitted FB-048 slice, not a branch cap.
- Additional FB-048 slices should continue on this branch whenever they stay inside the same backlog item, branch class, scope family, and validation surface.
- A bounded stop condition or explicit USER-approved split is required before stopping the branch after only WS-1.

## Admitted Implementation Slice

- Slice ID: `WS-1 accepted relaunch failure-path truthful outcome proof`
- Goal: prove and refine the accepted relaunch failure lane so relaunch-signal failure or reacquire wait-timeout produces explicit ownership-preserved failure truth without false guard-transfer, replacement-session activation, or replacement-session settled claims
- Runtime/User-Facing Delta: accepted relaunch failure stops collapsing into a generic failure or timeout story and becomes an explicit lifecycle result with truthful ownership and outcome markers
- Exact Affected Paths:
  - `desktop/single_instance.py`
  - `desktop/orin_desktop_launcher.pyw`
  - `desktop/orin_desktop_main.py`
  - `dev/orin_desktop_entrypoint_validation.py`
  - `dev/orin_boot_transition_verification.py`
- In-Scope Paths:
  - `desktop/single_instance.py`
  - `desktop/orin_desktop_launcher.pyw`
  - `desktop/orin_desktop_main.py`
  - `dev/orin_desktop_entrypoint_validation.py`
  - `dev/orin_boot_transition_verification.py`
  - direct canon updates required to keep released-state truth and active FB-048 Branch Readiness truth aligned
- Out-Of-Scope Paths:
  - `main.py`
  - `Audio/`
  - `logs/`
  - `jarvis_visual/`
  - installer, packaging, or shortcut-registration redesign
  - broader boot-orchestrator implementation
  - unrelated tray, task, or runtime UX expansion
- Allowed Changes:
  - bounded relaunch-signal failure and wait-timeout classification work needed to prove truthful accepted-failure outcomes
  - bounded launcher / renderer breadcrumbs needed to prove whether the active session kept ownership or released too late
  - bounded validator changes needed to assert accepted-failure truth without cleanup masking
  - direct canon updates required to keep released-state and Branch Readiness truth correct
- Prohibited Changes:
  - no `main.py` ownership rewrite
  - no `Audio/` rewiring
  - no `logs/` ownership changes
  - no `jarvis_visual/` relocation or reorganization
  - no installer or shortcut-registration redesign
  - no broader boot-orchestrator buildout

## Validation Contract

- run `python dev\orin_desktop_entrypoint_validation.py`
- run `python dev\orin_boot_transition_verification.py`
- run `python -m py_compile desktop\single_instance.py desktop\orin_desktop_launcher.pyw desktop\orin_desktop_main.py dev\orin_desktop_entrypoint_validation.py dev\orin_boot_transition_verification.py`
- run `python dev\orin_branch_governance_validation.py`
- run `git diff --check`
- preserve proof that default launch, accepted relaunch success, declined relaunch preservation, repeated launch, and explicit dev-boot paths remain green while accepted relaunch failure becomes first-class truthful outcome proof
- confirm relaunch-signal failure and reacquire wait-timeout do not emit false replacement-session activation, settled, guard-release, or guard-reacquire claims

## Rollback Conditions

- rollback if the already-green desktop shortcut / VBS / launcher / renderer startup path regresses before or at authoritative settled
- rollback if accepted relaunch success proof regresses while proving the accepted failure lane
- rollback if declined relaunch preservation proof regresses while proving the accepted failure lane
- rollback if failure-path ownership truth becomes less explicit or depends on cleanup masking instead of real evidence
- rollback if explicit dev-boot proof regresses or drifts away from the authoritative settled contract
- rollback if the slice widens into `main.py`, `Audio/`, `logs/`, `jarvis_visual/`, installer behavior, or broader orchestrator work

## User Test Summary Strategy

- Branch Readiness itself does not change runtime behavior, so no manual User Test Summary artifact is required for this pass.
- The admitted WS-1 slice is runtime/user-facing and touches the shipped relaunch path, so later Live Validation must classify real shortcut applicability and exact `## User Test Summary` status before green.
- Existing real shortcut proof remains a baseline, but it will not replace later FB-048 live proof if the admitted slice materially changes accepted-relaunch failure behavior.

## Later-Phase Expectations

- Workstream must begin with the admitted WS-1 accepted relaunch failure-path truthful outcome proof slice and keep same-branch backlog completion as the default for any remaining FB-048 slices.
- Hardening must pressure-test relaunch-signal delivery failure, reacquire wait-timeout timing, mixed success/failure relaunch sequences, and hidden coupling around single-instance release versus timeout classification.
- Live Validation must classify real shortcut applicability, validate production-path and explicit dev-boot proof on the updated lane, and record exact User Test Summary status.
- PR Readiness must package FB-048 as a real runtime/user-facing relaunch signal-failure and wait-timeout truth lane, not as a planning-only successor label.

## Initial Workstream Seam Sequence

Seam 1: `WS-1 accepted relaunch failure-path truthful outcome proof`

- Goal: refine and prove the accepted relaunch failure path end to end so signal-failure or wait-timeout outcomes preserve truthful ownership and explicit result markers.
- Scope: bounded prompt / signal / wait / ownership proof across the admitted paths only.
- Non-Includes: no `main.py` ownership rewrite, no audio changes, no log-root changes, no visual-asset moves, no installer redesign, and no broader boot-orchestrator implementation.

## Active Seam

Active seam: `None.`

- Branch Readiness defines the admitted WS-1 slice but does not execute it.
- `Workstream` is now the next legal phase.
