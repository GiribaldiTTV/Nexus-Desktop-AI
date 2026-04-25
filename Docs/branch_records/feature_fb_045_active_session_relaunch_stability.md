# Branch Authority Record: feature/fb-045-active-session-relaunch-stability

## Branch Identity

- Branch: `feature/fb-045-active-session-relaunch-stability`
- Workstream: `FB-045`
- Branch Class: `implementation`

## Purpose / Why It Exists

This branch record owns FB-045 `Branch Readiness` while the backlog item remains `Registry-only` and before a promoted canonical workstream record exists.

This pass closes the merged-main FB-044 `Release Readiness` blocker into a new `feature/` branch instead of leaving release packaging blocked on analysis alone. FB-044 remains the merged-unreleased release-debt owner for `v1.6.9-prebeta`; FB-045 owns the blocker-clearing runtime/user-facing follow-through on the next legal branch surface.

Historical traceability note: Branch Readiness is complete historical proof only. Active execution truth now lives in `Docs/workstreams/FB-045_active_session_relaunch_outcome_refinement.md`.

## Current Phase

- Phase: `Branch Readiness`

## Phase Status

- Repo State: `Historical Traceability`
- Historical Branch: `feature/fb-045-active-session-relaunch-stability`
- Historical posture: `Branch Readiness completed before promotion; active execution truth moved to Docs/workstreams/FB-045_active_session_relaunch_outcome_refinement.md.`
- Latest Public Prerelease: `v1.6.8-prebeta`
- Latest Public Release Commit: `5e695af5fada05e4ad6b25731bce328ede8a09ee`
- Latest Public Prerelease Publication: `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.8-prebeta`
- Latest Public Prerelease Title: `Pre-Beta v1.6.8`
- FB-044 remains the merged-unreleased release-debt owner for `v1.6.9-prebeta`.
- Updated-main `Release Readiness` found a reproducible post-settled runtime failure in a disposable validation clone: the authoritative settled marker is observed, then the renderer exits `3221226505`, stderr reports `Failed to make current since context is marked as lost`, and the launcher records `STATUS|SUCCESS|LAUNCHER_RUNTIME|FAILURE_FLOW_COMPLETE`.
- The failing scenarios on updated-main were `vbs_default`, `vbs_fallback`, `main_default_handoff`, and `main_explicit_desktop_handoff`; all reached `DESKTOP_OUTCOME|SETTLED|state=dormant` before the bad exit.
- The same validator is green on the normal workspace branch baseline, so the blocker is currently classified as environment-sensitive post-settled runtime instability rather than a universal pre-settled cold-start failure.
- FB-045 remains selected-only / `Registry-only` during this Branch Readiness pass.
- Active seam: `None.` Branch Readiness has classified the blocker and admitted the first bounded FB-045 runtime/user-facing slice; `Workstream` is the next legal phase.

## Branch Class

- `implementation`

## Blockers

None. The merged-main release blocker is now owned by the admitted FB-045 slice rather than remaining an unresolved Branch Readiness blocker.

## Entry Basis

- `v1.6.8-prebeta` is published and validated at `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.8-prebeta` on target commit `5e695af5fada05e4ad6b25731bce328ede8a09ee`.
- FB-044 is merged on `main` and remains the release-debt owner for `v1.6.9-prebeta`.
- Updated-main `Release Readiness` revalidation proved the merged package is not clean enough to ship because post-settled runtime stability diverged across environments.
- A new `feature/` branch is the legal repair surface for that post-merge blocker because `main` is protected and `Release Readiness` is file-frozen.
- FB-045 is the selected-next runtime/user-facing successor lane, and the next smallest repo-grounded follow-through is the post-settled runtime stability / relaunch outcome boundary across launcher, renderer, and reusable validation proof.

## Exit Criteria

- FB-044 release-readiness failure is explicitly classified in active canon instead of living only in an analysis report.
- FB-045 owns a bounded blocker-clearing runtime/user-facing slice on a normal `feature/` branch.
- The admitted slice records exact affected paths, in-scope/out-of-scope limits, validation coverage, rollback conditions, and same-branch backlog-completion posture.
- Current-state canon preserves FB-044 as the merged-unreleased release-debt owner while also making the active FB-045 Branch Readiness branch explicit.
- Branch Readiness resolves without widening into `Audio/`, `logs/`, `jarvis_visual/`, installer changes, or broader future boot-orchestrator work.

## Rollback Target

- `Branch Readiness`

## Next Legal Phase

- `Workstream`

## Branch Objective

- Close the FB-044 merged-main release-readiness blocker into a bounded implementation-bearing feature branch.
- Classify the post-settled runtime failure precisely enough that Workstream starts on the real blocker instead of a vague relaunch label.
- Admit the smallest FB-045 slice that can stabilize post-settled runtime outcome behavior without regressing the already-green desktop entry chain.

## Target End-State

- Repo current-state canon truthfully shows an active FB-045 Branch Readiness branch while FB-044 still owns merged-unreleased release debt.
- The post-settled runtime failure is named, scoped, and owned by an admitted slice.
- FB-045 can advance to `Workstream` on this same branch with a clear runtime/user-facing execution target.
- Same-branch backlog completion remains the default unless only future-dependent blockers remain.

## Backlog Completion Strategy

Branch Completion Goal: `Complete FB-045 on this same branch unless only future-dependent blockers remain after the remaining implementable post-settled runtime and relaunch-stability work is exhausted.`
Known Future-Dependent Blockers: `None proven during Branch Readiness.`
Branch Closure Rule: `Do not leave Workstream after WS-1 while more implementable FB-045 work remains; exit Workstream only when Backlog Completion State becomes Implemented Complete or Implemented Complete Except Future Dependency.`

## Affected Surface Ownership

- `desktop/orin_desktop_launcher.pyw`: production launcher-owned settled observation, post-settled process supervision, failure flow, and relaunch-boundary authority.
- `desktop/orin_desktop_main.py`: renderer-owned settled-state emission, active-session shutdown path, and any post-settled relaunch or crash-adjacent breadcrumbs.
- `dev/orin_desktop_entrypoint_validation.py`: reusable production-path proof owner for post-settled healthy vs failure outcomes.
- `dev/orin_boot_transition_verification.py`: reusable explicit dev-boot proof owner when post-settled outcome handling must stay aligned across proof families.

## Expected Seam Families And Risk Classes

- Post-settled runtime stability family; risk class: runtime/user-facing correctness after the authoritative settled marker is already observed.
- Active-session relaunch and rollback visibility family; risk class: launcher or validator may misclassify a settled session that later exits unexpectedly.
- Environment-variability family; risk class: disposable clone or alternate workspace paths may expose a failure not seen on the primary workspace.
- Validation alignment family; risk class: production-path and dev-boot proof helpers may drift apart on what counts as healthy post-settled completion.

## Failure Classification

- Primary class: `Post-settled runtime instability on the active-session relaunch / rollback boundary`
- Observed failure: authoritative settled is reached, then the renderer exits `3221226505` with GPU context-loss stderr and the launcher enters `FAILURE_FLOW_COMPLETE` instead of ending on clean shutdown markers.
- Current scope reading: the blocker sits after successful cold-start admission and after settled-state proof, so the next slice should focus on post-settled runtime supervision, relaunch/rollback outcome handling, and validator truth rather than reopening pre-settled entrypoint ownership.

## Planning-Loop Guardrail

Implementation Delta Class: `runtime/user-facing`
Docs-Only Workstream: `No`
Planning-Loop Bypass User Approval: `None`
Planning-Loop Bypass Reason: `None`

- FB-045 is an implementation branch and this Branch Readiness pass admits a real runtime-bearing slice instead of a planning-only continuation.

## Slice Continuation Policy

Slice Continuation Default: `Same-branch backlog completion`
Backlog-Split User Approval: `None`
Backlog-Split Reason: `None`

- WS-1 is the first admitted FB-045 slice, not a branch cap.
- Additional FB-045 slices should continue on this branch whenever they stay inside the same backlog item, branch class, scope family, and validation surface.
- A bounded stop condition or explicit USER-approved split is required before stopping the branch after only WS-1.

## Admitted Implementation Slice

- Slice ID: `WS-1 post-settled runtime stability refinement`
- Goal: stabilize and clarify the post-settled runtime outcome so a session that has already reached `DESKTOP_OUTCOME|SETTLED|state=dormant` does not fall into launcher failure flow without a truthful relaunch / rollback classification.
- Runtime/User-Facing Delta: startup still reaches the same settled state, but post-settled active-session behavior becomes more stable and more honestly classified across launcher supervision and reusable validation proof.
- Exact Affected Paths:
  - `desktop/orin_desktop_launcher.pyw`
  - `desktop/orin_desktop_main.py`
  - `dev/orin_desktop_entrypoint_validation.py`
  - `dev/orin_boot_transition_verification.py`
- In-Scope Paths:
  - `desktop/orin_desktop_launcher.pyw`
  - `desktop/orin_desktop_main.py`
  - `dev/orin_desktop_entrypoint_validation.py`
  - `dev/orin_boot_transition_verification.py`
  - direct canon updates required to keep FB-044 release-debt truth and FB-045 Branch Readiness truth aligned
- Out-Of-Scope Paths:
  - `main.py`
  - `Audio/`
  - `logs/`
  - `jarvis_visual/`
  - installer, packaging, or shortcut-registration redesign
  - broader boot-orchestrator implementation
  - unrelated tray, task, or runtime UX expansion
- Allowed Changes:
  - bounded launcher / renderer coordination needed to classify or stabilize post-settled runtime outcome
  - bounded validator changes needed to prove healthy post-settled completion versus truthful rollback or failure flow
  - bounded dev-boot proof updates only when post-settled outcome truth must stay aligned across proof families
  - direct canon updates required to keep release-debt and active-branch truth correct
- Prohibited Changes:
  - no reopening pre-settled entrypoint ownership or cold-start fallback scope unless runtime proof forces it
  - no `main.py` ownership rewrite
  - no audio-path rewiring
  - no `logs/` ownership changes
  - no `jarvis_visual/` relocation or reorganization
  - no installer or shortcut-registration redesign
  - no broader boot-orchestrator buildout

## Validation Contract

- run `python dev\orin_desktop_entrypoint_validation.py` on the active branch baseline and keep the merged-main failure report as the blocker baseline reference
- run `python dev\orin_boot_transition_verification.py`
- run `python -m py_compile desktop\orin_desktop_launcher.pyw desktop\orin_desktop_main.py dev\orin_desktop_entrypoint_validation.py dev\orin_boot_transition_verification.py`
- run `python dev\orin_branch_governance_validation.py`
- run `git diff --check`
- preserve proof that the normal workspace route remains green while the merged-main disposable-clone blocker remains the classified problem to solve
- confirm production-path scenarios and explicit dev-boot proof continue to agree on the authoritative settled marker after any admitted runtime change

## Rollback Conditions

- rollback if the already-green primary-workspace desktop shortcut / VBS / launcher / renderer path regresses before or at settled
- rollback if explicit dev boot proof regresses or drifts away from the authoritative settled contract
- rollback if the slice widens into `main.py`, `Audio/`, `logs/`, `jarvis_visual/`, installer behavior, or broader orchestrator work
- rollback if post-settled failure handling becomes less truthful by hiding crashes behind false clean-shutdown or false relaunch-success markers

## User Test Summary Strategy

- Branch Readiness itself does not change runtime behavior, so no manual User Test Summary artifact is required for this pass.
- The admitted WS-1 slice is runtime/user-facing and touches post-settled production behavior, so later Live Validation must classify real shortcut applicability and exact `## User Test Summary` status before green.
- Existing real shortcut proof remains a baseline, but it will not replace later FB-045 live proof if the admitted slice changes post-settled behavior materially.

## Later-Phase Expectations

- Workstream must begin with the admitted WS-1 post-settled runtime stability refinement slice and keep same-branch backlog completion as the default for any remaining FB-045 slices.
- Hardening must pressure-test environment variability, exact post-settled signal timing, truthful rollback classification, and hidden coupling around launcher failure flow after settled.
- Live Validation must classify real shortcut applicability, validate production-path and dev-boot proof on the updated lane, and record exact User Test Summary status.
- PR Readiness must package FB-045 as a real runtime/user-facing blocker-clearing implementation lane, not as a release-only or docs-only repair.

## Initial Workstream Seam Sequence

Seam 1: `WS-1 post-settled runtime stability refinement`

- Goal: stabilize the runtime boundary after authoritative settled is observed and make healthy completion vs rollback/failure-flow classification explicit across launcher, renderer, and reusable validators.
- Scope: bounded launcher / renderer / validator refinement across the admitted paths only.
- Non-Includes: no `main.py` ownership rewrite, no audio changes, no log-root changes, no visual-asset moves, no installer redesign, and no broader boot-orchestrator implementation.

## Active Seam

Active seam: `None.`

- Branch Readiness defines the admitted WS-1 slice but does not execute it.
- `Workstream` is now the next legal phase.
