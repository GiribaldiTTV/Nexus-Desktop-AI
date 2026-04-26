# Branch Authority Record: feature/fb-047-active-session-relaunch-decline-preservation

## Branch Identity

- Branch: `feature/fb-047-active-session-relaunch-decline-preservation`
- Workstream: `FB-047`
- Branch Class: `implementation`

## Purpose / Why It Exists

This branch record owns FB-047 `Branch Readiness` while the backlog item remains `Registry-only` and before a promoted canonical workstream record exists.

This pass closes FB-046 post-release canon on the next legal `feature/` branch surface, advances latest public prerelease truth to `v1.6.10-prebeta`, clears merged-unreleased release debt, and admits the first bounded runtime/user-facing relaunch-decline preservation slice without promoting FB-047 before `Workstream`.

Historical traceability note: `feature/fb-046-post-merge-canon-sync` was a bounded repair-only post-merge canon-sync branch only and did not imply FB-046 or FB-047 Branch Readiness admission or active branch truth.
Historical traceability note: Branch Readiness is complete historical proof only. Active execution truth now lives in `Docs/workstreams/FB-047_active_session_relaunch_decline_preservation.md`.

## Current Phase

- Phase: `Branch Readiness`

## Phase Status

- Repo State: `Historical Traceability`
- Historical Branch: `feature/fb-047-active-session-relaunch-decline-preservation`
- Historical posture: `Branch Readiness completed before promotion; active execution truth moved to Docs/workstreams/FB-047_active_session_relaunch_decline_preservation.md.`
- Latest Public Prerelease: `v1.6.10-prebeta`
- Latest Public Release Commit: `36cf07495dc8e239b20b11afb5194355b77ffd8b`
- Latest Public Prerelease Publication: `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.10-prebeta`
- Latest Public Prerelease Title: `Pre-Beta v1.6.10`
- FB-046 is now `Released / Closed` historical proof in `v1.6.10-prebeta`.
- Merged-unreleased release debt is clear after publication, validation, and post-release canon closure.
- FB-047 Branch Readiness is complete historical proof, and active execution truth now lives in the promoted canonical workstream doc on this same branch.
- Active seam: `None.` This record is now preserved historical Branch Readiness truth.

## Branch Class

- `implementation`

## Blockers

None. Post-release closure prerequisites are satisfied, and the first bounded relaunch-decline preservation slice is admitted.

## Entry Basis

- `v1.6.10-prebeta` is published and validated at `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.10-prebeta` on target commit `36cf07495dc8e239b20b11afb5194355b77ffd8b`.
- FB-046 is live released, and release debt is clear after publication, validation, and post-release canon closure.
- Updated-main revalidation is green after FB-046 Release Readiness and live release validation.
- The current code already contains the relaunch prompt, the decline button path, and the incoming-launch early exit when the active session is kept, but the repo does not yet prove that declining replacement preserves the settled active session, keeps single-instance ownership with that session, and terminates the incoming launch truthfully without false replacement-session markers.
- A new `feature/` branch is the legal active surface because `main` is protected and no active implementation branch remains.

## Exit Criteria

- latest public prerelease truth advances to `v1.6.10-prebeta` in active canon
- FB-046 closes as released historical truth, and merged-unreleased release debt clears
- FB-047 owns a bounded runtime/user-facing slice on a normal `feature/` branch while remaining `Registry-only` during Branch Readiness
- the admitted slice records exact affected paths, validation coverage, rollback conditions, and same-branch backlog-completion posture
- Branch Readiness resolves without widening into `main.py`, `Audio/`, `logs/`, `jarvis_visual/`, installer work, or broader boot-orchestrator implementation

## Rollback Target

- `Branch Readiness`

## Next Legal Phase

- `Workstream`

## Branch Objective

- close FB-046 post-release canon on the next legal active branch surface
- admit the smallest runtime-bearing FB-047 slice that proves declined relaunch preserves the settled active session and truthfully terminates the incoming launch
- preserve selected-only Branch Readiness truth until promotion is warranted by actual Workstream execution

## Target End-State

- current-state canon shows FB-046 as `Released / Closed` historical proof in `v1.6.10-prebeta`
- FB-047 remains selected-only on this branch until `Workstream` begins
- `Workstream` can start on real relaunch-decline preservation proof instead of a vague future-planning label
- same-branch backlog completion remains the default unless only future-dependent blockers remain

## Backlog Completion Strategy

Branch Completion Goal: `Complete FB-047 on this same branch unless only future-dependent blockers remain after the remaining implementable relaunch-decline preservation work is exhausted.`
Known Future-Dependent Blockers: `None proven during Branch Readiness.`
Branch Closure Rule: `Do not leave Workstream after WS-1 while more implementable FB-047 work remains; exit Workstream only when Backlog Completion State becomes Implemented Complete or Implemented Complete Except Future Dependency.`

## Affected Surface Ownership

- `desktop/single_instance.py`: relaunch prompt outcome handling, harness-only decline path, and single-instance ownership truth at the conflict prompt boundary
- `desktop/orin_desktop_launcher.pyw`: truthful incoming-launch decline classification, active-session preservation breadcrumbs, and incoming-launch termination behavior
- `desktop/orin_desktop_main.py`: current-session relaunch-receipt absence and settled-session preservation breadcrumbs if minimal runtime proof needs an explicit renderer-side marker
- `dev/orin_desktop_entrypoint_validation.py`: reusable production-path proof owner for declined relaunch, preserved active-session ownership, and incoming-launch truthful exit
- `dev/orin_boot_transition_verification.py`: reusable explicit dev-boot proof owner if decline-path lifecycle truth must stay aligned across proof families

## Expected Seam Families And Risk Classes

- relaunch-decline prompt outcome family; risk class: incoming launch may still collapse into a generic already-running skip without proving why that exit is correct
- active-session preservation family; risk class: the settled active session may remain preserved in reality but unproven in durable repo evidence
- single-instance ownership family; risk class: the repo may not prove that the active session kept sole ownership while the incoming launch exited
- validation alignment family; risk class: accepted and declined relaunch paths may diverge on lifecycle truth or falsely share replacement-session success markers

## Planning-Loop Guardrail

Implementation Delta Class: `runtime/user-facing`
Docs-Only Workstream: `No`
Planning-Loop Bypass User Approval: `None`
Planning-Loop Bypass Reason: `None`

- FB-047 is an implementation branch and this Branch Readiness pass admits a real runtime-bearing slice instead of a planning-only continuation.

## Slice Continuation Policy

Slice Continuation Default: `Same-branch backlog completion`
Backlog-Split User Approval: `None`
Backlog-Split Reason: `None`

- WS-1 is the first admitted FB-047 slice, not a branch cap.
- Additional FB-047 slices should continue on this branch whenever they stay inside the same backlog item, branch class, scope family, and validation surface.
- A bounded stop condition or explicit USER-approved split is required before stopping the branch after only WS-1.

## Admitted Implementation Slice

- Slice ID: `WS-1 declined relaunch incoming-launch truthful exit proof`
- Goal: prove and refine end-to-end declined relaunch so declining replacement preserves the active settled session, keeps single-instance ownership with that session, and cleanly terminates the incoming launch without dual ownership or false replacement-session markers.
- Runtime/User-Facing Delta: relaunch decline stops being a generic already-running skip and becomes an explicit preserved-session / truthful incoming-launch termination story.
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
  - direct canon updates required to keep released-state truth and active FB-047 Branch Readiness truth aligned
- Out-Of-Scope Paths:
  - `main.py`
  - `Audio/`
  - `logs/`
  - `jarvis_visual/`
  - installer, packaging, or shortcut-registration redesign
  - broader boot-orchestrator implementation
  - unrelated tray, task, or runtime UX expansion
- Allowed Changes:
  - bounded relaunch-decline prompt / guard / incoming-launch classification handling needed to prove preserved-session truth
  - bounded launcher / renderer breadcrumbs needed to show that the active session remained the owner while the incoming launch exited
  - bounded validator changes needed to assert declined relaunch truth without cleanup masking
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
- preserve proof that default launch, accepted relaunch, repeated launch, and explicit dev-boot paths remain green while declined relaunch becomes a first-class preserved-session proof surface
- confirm the incoming launch terminates without false replacement-session success markers and that the active settled session remains the sole owner throughout the decline lane

## Rollback Conditions

- rollback if the already-green desktop shortcut / VBS / launcher / renderer startup path regresses before or at authoritative settled
- rollback if accepted relaunch proof regresses while proving decline-path preservation
- rollback if active-session preservation or single-instance ownership truth becomes less explicit or depends on cleanup masking instead of real evidence
- rollback if explicit dev-boot proof regresses or drifts away from the authoritative settled contract
- rollback if the slice widens into `main.py`, `Audio/`, `logs/`, `jarvis_visual/`, installer behavior, or broader orchestrator work

## User Test Summary Strategy

- Branch Readiness itself does not change runtime behavior, so no manual User Test Summary artifact is required for this pass.
- The admitted WS-1 slice is runtime/user-facing and touches the shipped relaunch path, so later Live Validation must classify real shortcut applicability and exact `## User Test Summary` status before green.
- Existing real shortcut proof remains a baseline, but it will not replace later FB-047 live proof if the admitted slice materially changes relaunch-decline behavior.

## Later-Phase Expectations

- Workstream must begin with the admitted WS-1 declined relaunch incoming-launch truthful exit proof slice and keep same-branch backlog completion as the default for any remaining FB-047 slices.
- Hardening must pressure-test rapid decline timing, repeated decline attempts, accepted-versus-declined relaunch cross-path truth, and hidden coupling around single-instance cleanup versus preserved-session proof.
- Live Validation must classify real shortcut applicability, validate production-path and explicit dev-boot proof on the updated lane, and record exact User Test Summary status.
- PR Readiness must package FB-047 as a real runtime/user-facing relaunch-decline preservation lane, not as a docs-only successor label.

## Initial Workstream Seam Sequence

Seam 1: `WS-1 declined relaunch incoming-launch truthful exit proof`

- Goal: refine and prove the declined relaunch path end to end so the active session remains the owner and the incoming launch exits truthfully.
- Scope: bounded prompt / ownership / incoming-launch termination proof across the admitted paths only.
- Non-Includes: no `main.py` ownership rewrite, no audio changes, no log-root changes, no visual-asset moves, no installer redesign, and no broader boot-orchestrator implementation.

## Active Seam

Active seam: `None.`

- Branch Readiness defines the admitted WS-1 slice but does not execute it.
- `Workstream` is now the next legal phase.
