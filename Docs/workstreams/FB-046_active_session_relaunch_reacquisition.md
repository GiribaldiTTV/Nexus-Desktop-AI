# FB-046 Active-Session Relaunch Reacquisition And Settled Re-Entry Proof

## Identity

- ID: `FB-046`
- Title: `Active-session relaunch reacquisition and settled re-entry proof`

## Record State

- `Promoted`

## Status

- `In Progress`

## Canonical Branch

- `feature/fb-046-active-session-relaunch-reacquisition`

## Current Phase

- Phase: `Hardening`

## Phase Status

- Repo State: `Active Branch`
- Current Active Branch: `feature/fb-046-active-session-relaunch-reacquisition`
- Current Active Canonical Workstream Doc: `Docs/workstreams/FB-046_active_session_relaunch_reacquisition.md`
- Latest Public Prerelease: `v1.6.9-prebeta`
- Latest Public Release Commit: `348fd55b944435e3cae80b97acd0bb857fd65d56`
- Latest Public Prerelease Publication: `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.9-prebeta`
- Latest Public Prerelease Title: `Pre-Beta v1.6.9`
- FB-044 and FB-045 are `Released / Closed` historical proof in `v1.6.9-prebeta`.
- Release debt is clear after publication, validation, and post-release canon closure.
- Active seam: `None.` H-1 is complete and validated. `Live Validation` is next.

## Branch Class

- `implementation`

## Blockers

None.

## Entry Basis

- `v1.6.9-prebeta` is published and validated on commit `348fd55b944435e3cae80b97acd0bb857fd65d56`.
- FB-044 and FB-045 are live released, and merged-unreleased release debt is clear.
- The code already contained the relaunch prompt, named relaunch signal, runtime-guard reacquisition loop, and shutdown-on-relaunch handling before FB-046 started.
- What was still missing was first-class proof that an accepted relaunch closes the active session, reacquires the single-instance guard, starts the replacement session, and returns that replacement session to `DESKTOP_OUTCOME|SETTLED|state=dormant`.

## Exit Criteria

- accepted relaunch is proven end to end across launcher, renderer, single-instance guard, and reusable validators
- the prior session fully releases before the replacement session owns the runtime
- replacement-session authoritative settled proof is explicit instead of inferred from nearby markers
- no overlap or dual ownership occurs during relaunch handoff
- the branch does not leave `Workstream` until FB-046 records `Backlog Completion State`

## Rollback Target

- `Workstream`

## Next Legal Phase

- `Live Validation`

## Purpose / Why It Matters

FB-046 exists to make accepted relaunch a complete runtime story instead of a partial one. The repo already knew how to ask for relaunch, signal the current session, and wait for the guard to free up. What it did not yet prove cleanly was that the replacement session became the new owner and made it all the way back to authoritative settled state.

## Scope

- bounded relaunch prompt / signal / guard reacquisition truth across `desktop/single_instance.py`, `desktop/orin_desktop_launcher.pyw`, and `desktop/orin_desktop_main.py`
- reusable validator work in `dev/orin_desktop_entrypoint_validation.py` and `dev/orin_boot_transition_verification.py`
- direct canon updates needed to promote FB-046 into active workstream truth and keep released-state carry-forward aligned
- for FB-046, `bounded` means the runtime lane stayed tightly scoped while still serving as the full currently implementable FB-046 backlog-completion pass, not the first fragment of a larger hidden FB-046 chain

## Non-Goals

- no `main.py` ownership rewrite
- no `Audio/` changes
- no `logs/` ownership changes
- no `jarvis_visual/` relocation or reorganization
- no installer or shortcut-registration redesign
- no broader boot-orchestrator implementation

## Planning-Loop Guardrail

Implementation Delta Class: `runtime/user-facing`
Docs-Only Workstream: `No`
Planning-Loop Bypass User Approval: `None`
Planning-Loop Bypass Reason: `None`

- FB-046 remains a real runtime/user-facing lane and must not collapse into release-only or planning-only narration.

## Slice Continuation Policy

Slice Continuation Default: `Same-branch backlog completion`
Backlog-Split User Approval: `None`
Backlog-Split Reason: `None`

- WS-1 is the first completed FB-046 slice, not a branch cap.
- Additional FB-046 slices would continue on this same branch if more implementable relaunch-reacquisition work remained.
- For the current FB-046 definition, that continuation rule is now satisfied: no additional implementable FB-046 runtime slices remain on this branch.

## Backlog Completion Status

Backlog Completion State: `Implemented Complete`
Remaining Implementable Work: `None`
Future-Dependent Blockers: `None`

- This branch now represents the full currently implementable FB-046 runtime/user-facing pass.
- Future relaunch or reacquisition issues should create a new backlog item or explicitly broaden FB-046 in source truth before more FB-046 slice work is claimed.

## Validation Contract

- run `python -m py_compile desktop\single_instance.py desktop\orin_desktop_launcher.pyw desktop\orin_desktop_main.py dev\orin_desktop_entrypoint_validation.py dev\orin_boot_transition_verification.py`
- run `python dev\orin_desktop_entrypoint_validation.py`
- run `python dev\orin_boot_transition_verification.py`
- run `python dev\orin_branch_governance_validation.py`
- run `git diff --check`
- preserve proof that default launch, repeated launch, and explicit dev-boot paths remain green while accepted relaunch becomes first-class replacement-session settled proof

## Artifact History

- `dev/orin_desktop_entrypoint_validation.py`
  - Classification: `Reusable`
  - Purpose: validates canonical production launch paths, repeated launch, accepted relaunch, and post-settled lifecycle classification
  - Reuse: continue extending this helper before creating another overlapping relaunch validator
- `dev/orin_boot_transition_verification.py`
  - Classification: `Reusable`
  - Purpose: proves explicit dev boot still converges on the same authoritative settled truth
  - Reuse: preserve this helper as the explicit dev-boot truth owner when relaunch or settled semantics change

## Admitted Implementation Slice

### WS-1 accepted relaunch replacement-session settled re-entry proof

- Status: `Complete / validated`
- Goal: prove and refine end-to-end accepted relaunch so a confirmed relaunch request closes the active session, reacquires the runtime guard, launches the replacement session, and returns that replacement session to `DESKTOP_OUTCOME|SETTLED|state=dormant`
- Exact Affected Paths:
  - `desktop/single_instance.py`
  - `desktop/orin_desktop_launcher.pyw`
  - `desktop/orin_desktop_main.py`
  - `dev/orin_desktop_entrypoint_validation.py`
  - `dev/orin_boot_transition_verification.py`
  - `Docs/workstreams/FB-046_active_session_relaunch_reacquisition.md`
  - `Docs/workstreams/index.md`
  - `Docs/feature_backlog.md`
  - `Docs/prebeta_roadmap.md`
  - `Docs/branch_records/index.md`
  - `Docs/workstreams/FB-044_boot_desktop_handoff_outcome_refinement.md`
  - `Docs/workstreams/FB-045_active_session_relaunch_outcome_refinement.md`

### WS-1 Implementation Results

- `desktop/single_instance.py` now exposes a harness-only auto-accept relaunch path so accepted relaunch can be exercised without dialog-click masking, and it emits an explicit replacement-session confirmation marker after successful reacquisition.
- `desktop/orin_desktop_launcher.pyw` now records replacement-session activation, replacement-session authoritative-settled success, and explicit guard release, so launcher truth no longer stops at reacquisition alone.
- `dev/orin_desktop_entrypoint_validation.py` now runs a real accepted-relaunch cycle across the VBS entrypoint, first session, replacement launcher, guard reacquisition, replacement-session settled proof, and no-dual-ownership checks.
- The accepted-relaunch scenario now accepts the truthful lifecycle outcomes after replacement-session settled: either clean termination or the already-valid post-settled recoverable lane.
- Existing green startup paths stayed green across VBS launch, direct `main.py` handoff, repeated launch, and explicit dev-boot verification.

### WS-1 Validation Results

- `python -m py_compile desktop\single_instance.py desktop\orin_desktop_launcher.pyw desktop\orin_desktop_main.py dev\orin_desktop_entrypoint_validation.py dev\orin_boot_transition_verification.py`: PASS
- `python dev\orin_desktop_entrypoint_validation.py`: PASS
  - report: `dev/logs/desktop_entrypoint_validation/reports/DesktopEntrypointValidationReport_20260426_084737.txt`
- `python dev\orin_boot_transition_verification.py`: PASS
  - report: `dev/logs/boot_transition_verification/reports/BootTransitionVerificationReport_20260426_084445.txt`

## Root Cause Analysis

The missing link was not relaunch signaling by itself. The repo already had that. The missing link was durable ownership proof across the handoff boundary. Before FB-046, the second launcher could wait for the guard and the first runtime could shut down, but the repo still did not record the replacement session as a first-class success surface with its own reacquire and settled proof.

## Relaunch Lifecycle Result

Accepted relaunch is now proven across the full lifecycle:

- session 1 reaches `DESKTOP_OUTCOME|SETTLED|state=dormant`
- session 2 detects the conflict, accepts relaunch, signals the live session, and waits
- session 1 receives the relaunch request, shuts down, exits, and releases the guard
- session 2 reacquires the single-instance guard, becomes the replacement session, reaches authoritative settled, and releases cleanly or truthfully classifies a post-settled recoverable exit

That keeps settled-state truth authoritative while making replacement-session ownership explicit instead of implied.

## H-1 Hardening Record

H-1 pressure-tested the completed FB-046 relaunch-reacquisition lane across fast and slow relaunch shutdown timing, replacement-session success-marker timing, single-instance guard exclusivity, clean-shutdown precedence, relaunch after recoverable post-settled exit, and rapid consecutive accepted relaunch cycles without widening beyond the admitted runtime/user-facing surfaces.

### Hardening Findings

- Slow accepted relaunch still releases the original session before the replacement session logs reacquisition or replacement-session activation.
- Replacement-session success markers do not appear on the original session, and they do not appear on the replacement session before the guard reacquire marker is present.
- The single-instance guard is now logged as released only after the launcher actually releases the runtime guard and relaunch signal handles.
- Relaunch after a recoverable post-settled exit remains green: startup truth stays anchored to authoritative settled, and a later accepted relaunch still reacquires the guard and returns the replacement session to settled.
- Rapid consecutive accepted relaunch cycles remain truthful: each successor session reacquires only after the previous session emits release, and no dual ownership or relaunch wait timeout appears.
- The main hidden coupling was in validator evidence attribution, not the runtime lane itself. Multi-session scenarios needed frozen per-session log identity so append timing could not make the validator compare the wrong session logs.

### Hardening Corrections

- `desktop/orin_desktop_main.py` now exposes a harness-only relaunch-shutdown delay hook so slow-shutdown timing can be exercised without changing production behavior.
- `desktop/orin_desktop_launcher.pyw` now emits `SINGLE_INSTANCE_RELEASED` only after the guard and relaunch signal resources have actually been released.
- `dev/orin_desktop_entrypoint_validation.py` now freezes per-session runtime-log attribution for multi-session relaunch scenarios and adds reusable coverage for:
  - accepted relaunch with slow shutdown
  - relaunch after recoverable post-settled exit
  - rapid consecutive accepted relaunch cycles
  - replacement-session success-marker timing
- No broader runtime correction was needed in `desktop/single_instance.py`; the relaunch ownership model itself held under the new pressure tests.

### H-1 Completion Decision

- H-1 Result: `Complete / green`
- Remaining implementable work inside FB-046: `None`
- Stop condition: phase boundary reached; Hardening is complete after H-1.

### H-1 Validation Results

- `python -m py_compile desktop\single_instance.py desktop\orin_desktop_launcher.pyw desktop\orin_desktop_main.py dev\orin_desktop_entrypoint_validation.py dev\orin_boot_transition_verification.py`: PASS
- `python dev\orin_desktop_entrypoint_validation.py`: PASS
  - report: `dev/logs/desktop_entrypoint_validation/reports/DesktopEntrypointValidationReport_20260426_095741.txt`
- `python dev\orin_boot_transition_verification.py`: PASS
  - report: `dev/logs/boot_transition_verification/reports/BootTransitionVerificationReport_20260426_095803.txt`
- `python dev\orin_branch_governance_validation.py`: PASS
- `git diff --check`: PASS

### H-1 Stability Notes

- Replacement-session success still remains downstream of authoritative reacquire and authoritative settled, never ahead of them.
- Clean shutdown still takes precedence when clean-exit markers are present, even on relaunch-capable sessions.
- Recoverable post-settled exit remains distinct from startup failure and can still be followed by a valid accepted relaunch cycle.
- The shipped VBS / launcher / renderer startup path, direct `main.py` desktop handoff proof, and explicit dev-boot proof all remain green after the added relaunch edge coverage.

## Active Seam

Active seam: `None.`

- H-1 is complete and validated.
- `Live Validation` is now the next legal phase.

## Seam Continuation Decision

Continue Decision: `Advance after H-1 because backlog completion is implemented complete and the next legal phase is Live Validation`
Next Active Seam: `None`
Stop Condition: `Reached Live Validation gate after H-1 completion`
Continuation Action: `Validate repo-truth alignment, real shortcut applicability, User Test Summary status, and relaunch lifecycle proof on the hardened branch without widening scope`
