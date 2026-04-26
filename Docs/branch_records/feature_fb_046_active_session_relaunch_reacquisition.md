# Branch Authority Record: feature/fb-046-active-session-relaunch-reacquisition

## Branch Identity

- Branch: `feature/fb-046-active-session-relaunch-reacquisition`
- Workstream: `FB-046`
- Branch Class: `implementation`

## Purpose / Why It Exists

This branch record owns FB-046 `Branch Readiness` while the backlog item remains `Registry-only` and before a promoted canonical workstream record exists.

This pass closes FB-044 and FB-045 post-release canon on the next legal `feature/` branch surface, advances latest public prerelease truth to `v1.6.9-prebeta`, clears merged-unreleased release debt, and admits the first bounded runtime/user-facing relaunch-reacquisition slice without promoting FB-046 before `Workstream`.

Historical traceability note: `feature/fb-046-post-merge-canon-sync` was a bounded repair-only post-merge canon-sync branch only and did not imply FB-046 Branch Readiness admission or active branch truth.

## Current Phase

- Phase: `Branch Readiness`

## Phase Status

- Repo State: `Active Branch`
- Active Branch: `feature/fb-046-active-session-relaunch-reacquisition`
- Latest Public Prerelease: `v1.6.9-prebeta`
- Latest Public Release Commit: `348fd55b944435e3cae80b97acd0bb857fd65d56`
- Latest Public Prerelease Publication: `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.9-prebeta`
- Latest Public Prerelease Title: `Pre-Beta v1.6.9`
- FB-044 and FB-045 are now `Released / Closed` historical proof in `v1.6.9-prebeta`.
- Merged-unreleased release debt is clear after publication, validation, and post-release canon closure.
- FB-046 remains selected-only / `Registry-only` during this Branch Readiness pass.
- Active seam: `None.` Branch Readiness has admitted the first bounded FB-046 runtime/user-facing slice; `Workstream` is the next legal phase.

## Branch Class

- `implementation`

## Blockers

None. Post-release closure prerequisites are satisfied, and the first bounded relaunch-reacquisition slice is admitted.

## Entry Basis

- `v1.6.9-prebeta` is published and validated at `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.9-prebeta` on target commit `348fd55b944435e3cae80b97acd0bb857fd65d56`.
- FB-044 and FB-045 are live released, and release debt is clear after publication, validation, and post-release canon closure.
- Updated-main revalidation is green after the FB-045 blocker-clearing follow-through and the FB-046 canon-sync repair.
- The current code already contains the relaunch prompt, named relaunch signal, runtime-guard reacquisition loop, and shutdown-on-relaunch handling, but the repo does not yet prove replacement-session return to authoritative settled as a first-class runtime/user-facing success surface.
- A new `feature/` branch is the legal active surface because `main` is protected and no active implementation branch remains.

## Exit Criteria

- latest public prerelease truth advances to `v1.6.9-prebeta` in active canon
- FB-044 and FB-045 close as released historical truth, and merged-unreleased release debt clears
- FB-046 owns a bounded runtime/user-facing slice on a normal `feature/` branch while remaining `Registry-only` during Branch Readiness
- the admitted slice records exact affected paths, validation coverage, rollback conditions, and same-branch backlog-completion posture
- Branch Readiness resolves without widening into `main.py`, `Audio/`, `logs/`, `jarvis_visual/`, installer work, or broader boot-orchestrator implementation

## Rollback Target

- `Branch Readiness`

## Next Legal Phase

- `Workstream`

## Branch Objective

- close FB-044 and FB-045 post-release canon on the next legal active branch surface
- admit the smallest runtime-bearing FB-046 slice that proves accepted relaunch through replacement-session settled re-entry
- preserve selected-only Branch Readiness truth until promotion is warranted by actual Workstream execution

## Target End-State

- current-state canon shows FB-044 and FB-045 as `Released / Closed` historical proof in `v1.6.9-prebeta`
- FB-046 remains selected-only on this branch until Workstream begins
- Workstream can start on real relaunch-reacquisition proof instead of a vague future planning label
- same-branch backlog completion remains the default unless only future-dependent blockers remain

## Backlog Completion Strategy

Branch Completion Goal: `Complete FB-046 on this same branch unless only future-dependent blockers remain after the remaining implementable relaunch-reacquisition and settled re-entry work is exhausted.`
Known Future-Dependent Blockers: `None proven during Branch Readiness.`
Branch Closure Rule: `Do not leave Workstream after WS-1 while more implementable FB-046 work remains; exit Workstream only when Backlog Completion State becomes Implemented Complete or Implemented Complete Except Future Dependency.`

## Affected Surface Ownership

- `desktop/single_instance.py`: runtime guard ownership, replace prompt flow, relaunch signal, and reacquisition wait contract
- `desktop/orin_desktop_launcher.pyw`: production launcher relaunch request handling, runtime-guard reacquisition authority, and replacement-session launch supervision
- `desktop/orin_desktop_main.py`: renderer relaunch receipt, shutdown-on-relaunch handoff, and replacement-session settled breadcrumbs
- `dev/orin_desktop_entrypoint_validation.py`: reusable production-path proof owner for accepted relaunch and replacement-session settled re-entry
- `dev/orin_boot_transition_verification.py`: reusable explicit dev-boot proof owner when relaunch and settled re-entry semantics must stay aligned across proof families

## Expected Seam Families And Risk Classes

- accepted relaunch proof family; risk class: current proof may stop at prior-session shutdown instead of proving replacement-session completion
- runtime-guard reacquisition family; risk class: reacquisition may succeed or fail without durable proof on the replacement session
- replacement-session settled re-entry family; risk class: authoritative settled may remain first-start proof only instead of relaunch-completion proof
- validation alignment family; risk class: production-path and explicit dev-boot proof may drift on what counts as successful relaunch completion

## Planning-Loop Guardrail

Implementation Delta Class: `runtime/user-facing`
Docs-Only Workstream: `No`
Planning-Loop Bypass User Approval: `None`
Planning-Loop Bypass Reason: `None`

- FB-046 is an implementation branch and this Branch Readiness pass admits a real runtime-bearing slice instead of a planning-only continuation.

## Slice Continuation Policy

Slice Continuation Default: `Same-branch backlog completion`
Backlog-Split User Approval: `None`
Backlog-Split Reason: `None`

- WS-1 is the first admitted FB-046 slice, not a branch cap.
- Additional FB-046 slices should continue on this branch whenever they stay inside the same backlog item, branch class, scope family, and validation surface.
- A bounded stop condition or explicit USER-approved split is required before stopping the branch after only WS-1.

## Admitted Implementation Slice

- Slice ID: `WS-1 accepted relaunch replacement-session settled re-entry proof`
- Goal: prove and refine end-to-end accepted relaunch so a confirmed relaunch request closes the active session, reacquires the runtime guard, launches the replacement session, and returns that replacement session to `DESKTOP_OUTCOME|SETTLED|state=dormant`.
- Runtime/User-Facing Delta: relaunch stops being only an exit/request story and becomes a full replacement-session completion story with authoritative settled proof on the new session.
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
  - direct canon updates required to keep released-state truth and active FB-046 Branch Readiness truth aligned
- Out-Of-Scope Paths:
  - `main.py`
  - `Audio/`
  - `logs/`
  - `jarvis_visual/`
  - installer, packaging, or shortcut-registration redesign
  - broader boot-orchestrator implementation
  - unrelated tray, task, or runtime UX expansion
- Allowed Changes:
  - bounded relaunch prompt / signal / reacquisition handling needed to prove accepted replacement-session completion
  - bounded launcher / renderer breadcrumbs needed to show replacement-session return to authoritative settled
  - bounded validator changes needed to assert accepted relaunch completion without cleanup masking
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
- preserve proof that default launch, repeated launch, and explicit dev-boot paths remain green while accepted relaunch becomes a first-class replacement-session settled re-entry proof surface
- confirm accepted relaunch evidence proves replacement-session authoritative settled state instead of stopping at prior-session shutdown or reacquisition wait alone

## Rollback Conditions

- rollback if the already-green desktop shortcut / VBS / launcher / renderer startup path regresses before or at authoritative settled
- rollback if runtime-guard reacquisition or replacement-session settled proof becomes less truthful or depends on cleanup masking instead of real replacement-session evidence
- rollback if explicit dev-boot proof regresses or drifts away from the authoritative settled contract
- rollback if the slice widens into `main.py`, `Audio/`, `logs/`, `jarvis_visual/`, installer behavior, or broader orchestrator work

## User Test Summary Strategy

- Branch Readiness itself does not change runtime behavior, so no manual User Test Summary artifact is required for this pass.
- The admitted WS-1 slice is runtime/user-facing and touches the shipped relaunch path, so later Live Validation must classify real shortcut applicability and exact `## User Test Summary` status before green.
- Existing real shortcut proof remains a baseline, but it will not replace later FB-046 live proof if the admitted slice materially changes relaunch completion behavior.

## Later-Phase Expectations

- Workstream must begin with the admitted WS-1 accepted relaunch replacement-session settled re-entry proof slice and keep same-branch backlog completion as the default for any remaining FB-046 slices.
- Hardening must pressure-test fast and slow relaunch timing, reacquisition success versus timeout, repeated relaunch cycles, and hidden coupling around single-instance cleanup versus real replacement-session proof.
- Live Validation must classify real shortcut applicability, validate production-path and explicit dev-boot proof on the updated lane, and record exact User Test Summary status.
- PR Readiness must package FB-046 as a real runtime/user-facing relaunch-completion lane, not as a docs-only successor label.

## Initial Workstream Seam Sequence

Seam 1: `WS-1 accepted relaunch replacement-session settled re-entry proof`

- Goal: refine and prove the accepted relaunch path end-to-end so the replacement session returns to authoritative settled state.
- Scope: bounded relaunch prompt / signal / reacquisition / replacement-session settled proof across the admitted paths only.
- Non-Includes: no `main.py` ownership rewrite, no audio changes, no log-root changes, no visual-asset moves, no installer redesign, and no broader boot-orchestrator implementation.

## Active Seam

Active seam: `None.`

- Branch Readiness defines the admitted WS-1 slice but does not execute it.
- `Workstream` is now the next legal phase.
