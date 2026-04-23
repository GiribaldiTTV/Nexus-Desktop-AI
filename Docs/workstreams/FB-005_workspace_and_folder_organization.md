# FB-005 Workspace And Folder Organization

## Identity

- ID: `FB-005`
- Title: `Workspace and folder organization`

## Record State

- `Promoted`

## Status

- `Active`

## Release Stage

- `Slice-staged`

## Canonical Branch

- `feature/fb-005-workspace-path-planning`

## Current Phase

- Phase: `Hardening`

## Phase Status

- Current execution surface is `Active Branch`.
- `v1.6.5-prebeta` is live at `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.5-prebeta` on target commit `7c2933d6427feb08a1139ba7f5ba2393eb61f1e1`.
- FB-030 is Released / Closed in `v1.6.5-prebeta`, latest public prerelease truth is `v1.6.5-prebeta`, and merged-unreleased release debt is clear.
- FB-005 is promoted from selected-only / `Registry-only` into an active canonical workstream on `feature/fb-005-workspace-path-planning`.
- Workstream WS-1 is complete for the only currently admitted bounded path-sensitive slice.
- H-1 hardening is complete for that slice, and Live Validation is the next legal phase.
- Completed first slice: `desktop/orin_desktop_test.py` -> `dev/desktop/orin_desktop_test.py`.
- The moved dev-only harness now lives at `dev/desktop/orin_desktop_test.py`.
- Runtime entrypoints, launcher paths, audio paths, logs, visual assets, and user-facing desktop paths remain outside this admitted slice.
- Runtime-reachability proof remains unchanged: shipped entrypoints still route through `launch_orin_desktop.vbs` -> `desktop/orin_desktop_launcher.pyw` -> `desktop/orin_desktop_main.py`.
- The admitted Workstream chain ends after WS-1 for this pass because no WS-2 or later FB-005 slice is admitted yet; later slices remain explicit approval gates.
- No reverse runtime dependency on `dev/desktop/` or the moved harness was found.
- H-1 records one non-blocking dev-only residual risk: the harness still names historical visual file `jarvis_core_desktop.html` while the current desktop visual asset on disk is `orin_core_desktop.html`.

## Branch Class

- `implementation`

## Blockers

- None for the admitted WS-1 slice.
- Later workspace/path slices remain blocked until separately approved.

## Entry Basis

- `v1.6.5-prebeta` is published and validated at `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.5-prebeta` on commit `7c2933d6427feb08a1139ba7f5ba2393eb61f1e1`.
- Updated `main` is revalidated after release publication and release debt is clear.
- Historical closeouts already preserve completed FB-005 Step 3 and Step 4 slices, while Step 5 and broader workspace follow-through remain deferred and path-sensitive.
- Explicit path-sensitive approval is now recorded for one dev-only slice: `desktop/orin_desktop_test.py` -> `dev/desktop/orin_desktop_test.py`.
- That admitted slice is the smallest live path-owned move that advances FB-005 without touching production runtime entrypoints, launcher routing, audio paths, logs, visual assets, or user-facing desktop paths.

## Exit Criteria

- FB-005 is promoted from `Registry-only` to `Promoted`.
- The canonical workstream doc records the branch objective, target end-state, exact path ownership, migration limits, validation coverage, runtime reachability proof, and rollback conditions for the first bounded slice.
- Backlog, roadmap, workstreams index, and current released-lane carry-forward truth agree that FB-005 is now the active promoted lane.
- WS-1 moves `desktop/orin_desktop_test.py` to `dev/desktop/orin_desktop_test.py`, updates only required direct path references, preserves runtime non-reachability, and validates the moved harness from its new location.
- The canonical workstream doc records WS-1 execution results and the bounded-stop reason that ends the currently admitted chain after WS-1.

## Rollback Target

- `Branch Readiness`

## Next Legal Phase

- `Live Validation`

## Branch Objective

- Resume FB-005 through the smallest path-sensitive workspace slice that can be admitted without destabilizing current runtime or user-facing entrypoint ownership.
- Keep production runtime, launcher, audio, log-root, visual-asset, and user-facing path truth frozen while proving one dev-only harness move can be governed cleanly.
- Establish a reusable admission model for future FB-005 slices so later workspace work stays bounded, validated, and approval-gated.

## Target End-State

- FB-005 has a canonical workstream record instead of living only as a selected-only backlog item plus branch record.
- The first admitted slice is explicitly bounded to the dev-only desktop test harness move from `desktop/` to `dev/desktop/`.
- Future workspace/path slices remain blocked until separately approved; this branch does not silently widen into Step 5, runtime-root moves, or launcher-path restructuring.

## Expected Seam Families And Risk Classes

- Dev-only harness relocation family; risk class: workspace/path ownership, because the first admitted slice moves one non-runtime file into the dev-owned tree and must not accidentally widen beyond that boundary.
- Reference-sync and path-truth family; risk class: validation/governance, because the move is only safe if direct references, planning truth, and ownership records all point to the same new path.
- Runtime non-reachability proof family; risk class: launcher/runtime protection, because the admitted slice is legal only if shipped entrypoints, launcher routing, and user-facing desktop paths remain untouched.
- Rollback and containment family; risk class: implementation safety, because any need to touch runtime entrypoints, audio paths, logs, visual assets, or broader workspace structure invalidates this slice and routes work back to Branch Readiness.
- Future slice admission family; risk class: scope-control, because later FB-005 moves must stay separately approval-gated and must not piggyback on this dev-only harness relocation.

## Approved Workspace/Path Slice

- Slice ID: `WS-1 dev-only desktop test harness relocation`
- Approved Move: `desktop/orin_desktop_test.py` -> `dev/desktop/orin_desktop_test.py`
- Path Ownership Class: dev-only harness and validation-support surface
- Runtime Reachability Proof:
- current shipped runtime path remains `launch_orin_desktop.vbs` -> `desktop/orin_desktop_launcher.pyw` -> `desktop/orin_desktop_main.py`
- `desktop/orin_desktop_test.py` is not part of the shipped runtime path, not a launcher target, and not a user-facing desktop shortcut entrypoint
- current direct references are limited to the file itself and planning/reference docs

## In-Scope Paths

- `desktop/orin_desktop_test.py`
- `dev/desktop/orin_desktop_test.py`
- direct path references to the moved harness in branch-local canon, validation notes, and workspace-layout truth

## Out-Of-Scope Paths

- `main.py`
- `launch_orin_desktop.vbs`
- `desktop/orin_desktop_launcher.pyw`
- `desktop/orin_desktop_main.py`
- `desktop/desktop_renderer.py`
- `Audio/orin_voice.py`
- `Audio/orin_error_voice.py`
- `assistant_personas.py`
- `jarvis_visual/`
- `logs/`
- user-facing desktop shortcuts or equivalent entry surfaces

## Allowed Changes

- move the single admitted harness file from `desktop/` to `dev/desktop/`
- update the moved harness only as needed to preserve repo-root path math, imports, and dev-only behavior from the new location
- update exact path references in branch-local canon and workspace-layout planning surfaces
- add minimal path-ownership notes and validation evidence needed to prove the move

## Prohibited Changes

- no move of `main.py`
- no move or edit of `launch_orin_desktop.vbs`
- no launcher target change
- no production runtime import rewiring
- no `Audio/` movement or audio-path normalization
- no `jarvis_visual/` move or asset reorganization
- no `logs/` reorganization or log-root change
- no user-facing desktop shortcut or launcher-route change
- no broader Step 5 or top-level entrypoint restructuring

## Validation Contract

- run `python dev\orin_branch_governance_validation.py`
- run `git diff --check`
- confirm `Docs/Main.md` routes this promoted FB-005 workstream record
- confirm `Docs/feature_backlog.md` marks FB-005 as `Promoted`, `Active`, cites this canonical workstream doc, and no longer leaves FB-005 as selected-next / `Registry-only`
- confirm `Docs/prebeta_roadmap.md` records FB-005 as the current active workstream and no longer represents FB-005 as selected-next planning-only
- confirm `Docs/workstreams/index.md` lists this record under Active
- confirm `Docs/branch_records/index.md` no longer leaves `feature/fb-005-workspace-path-planning` as an active branch-authority owner after promotion
- confirm current runtime entrypoint truth still routes through `launch_orin_desktop.vbs` -> `desktop/orin_desktop_launcher.pyw` -> `desktop/orin_desktop_main.py`
- confirm `dev/desktop/orin_desktop_test.py` remains outside runtime entrypoint, launcher, audio, logs, visual-asset, and user-facing desktop shortcut ownership

## WS-1 Execution Results

- Moved `desktop/orin_desktop_test.py` to `dev/desktop/orin_desktop_test.py`.
- Updated local path resolution in the moved harness so repo-root imports and `jarvis_visual/jarvis_core_desktop.html` resolution still work from `dev/desktop/`.
- Updated direct current-path references in `Docs/workspace_layout_plan.md`.
- Preserved runtime entrypoints, launcher paths, audio paths, logs, visual assets, and user-facing desktop paths exactly as-is.
- Bounded-stop decision: stopping after WS-1 is legal here because the canonical FB-005 seam chain admits only WS-1; no WS-2 is admitted, and later workspace/path slices remain explicit approval gates rather than implied continuation.

## Branch Readiness Validation Results

- `python dev\orin_branch_governance_validation.py`: PASS, 1145 checks.
- `git diff --check`: PASS with line-ending normalization warnings only and no whitespace errors.
- `python -m py_compile dev\desktop\orin_desktop_test.py`: PASS.
- `python dev\desktop\orin_desktop_test.py`: PASS for bounded validation; the harness initializes from `dev/desktop/`, prints its expected banner, and exits only at the intentional `RuntimeError(\"Jarvis test crash triggered intentionally\")`.
- Runtime reachability review: current shipped runtime path remains `launch_orin_desktop.vbs` -> `desktop/orin_desktop_launcher.pyw` -> `desktop/orin_desktop_main.py`, and the admitted slice does not own any part of that route.
- Path ownership review: admitted scope is limited to `desktop/orin_desktop_test.py` -> `dev/desktop/orin_desktop_test.py`, with launcher paths, runtime entrypoints, audio paths, logs, visual assets, and user-facing desktop paths explicitly outside the slice.
- Canon routing review: `Docs/Main.md`, `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, `Docs/workstreams/index.md`, and `Docs/branch_records/index.md` route FB-005 as the promoted active lane and do not leave it as selected-next / `Registry-only` current-state truth.
- Harness execution target: the moved dev-only harness must still initialize from `dev/desktop/` and fail only at its intentional crash point, not from import or asset-resolution breakage.

## User Test Summary Strategy

- Branch Readiness and the admitted WS-1 slice are not user-facing by default.
- No desktop shortcut validation, desktop export, or manual User Test Summary handoff is required for Branch Readiness closeout.
- If a later FB-005 slice touches runtime entrypoints, launcher paths, logs, visual assets, audio paths, or another user-facing path, that later slice must classify shortcut applicability and User Test Summary requirements explicitly before Live Validation can advance.

## Later-Phase Expectations

- Workstream is admitted only for the approved WS-1 slice in this record.
- Completing WS-1 is the legal end of the currently admitted chain; no WS-2 exists yet.
- Later FB-005 slices require separate explicit path-sensitive approval; this branch must not widen from the admitted harness relocation into Step 5 or broader workspace cleanup by inertia.
- Hardening must pressure-test path ownership, reference sync, validation coverage, runtime non-reachability proof, and rollback posture for the admitted slice.
- Live Validation must classify shortcut and User Test Summary applicability from the actual implemented delta, not from FB-005 as a whole.

## Initial Workstream Seam Sequence

Seam 1: `desktop/orin_desktop_test.py` -> `dev/desktop/orin_desktop_test.py`

- Status: Complete.
- Goal: relocate the dev-only desktop crash/test harness into the dev-owned tree without changing production runtime ownership.
- Scope: move one file, update only its direct path references, preserve current behavior, and keep root-relative asset resolution intact from the new location.
- Non-Includes: no runtime entrypoint changes, no launcher-path changes, no audio-path changes, no logs changes, no visual-asset moves, no user-facing desktop-path changes, and no broader workspace restructuring.

## Active Seam

Active seam: `None.`

- WS-1 `desktop/orin_desktop_test.py` -> `dev/desktop/orin_desktop_test.py` is complete.
- Bounded-stop authority: no WS-2 is admitted in this workstream record, so stopping after WS-1 is the legal end of the current admitted chain rather than a single-seam drift.
- H-1 hardening is complete for the admitted slice.
- Next legal phase is `Live Validation`.

## Seam Continuation Decision

Continue Decision: `Stop at the Workstream phase boundary.`
Next Active Seam: `None.`
Stop Condition: `WS-1 desktop/orin_desktop_test.py -> dev/desktop/orin_desktop_test.py` is the only admitted FB-005 seam in the current canonical workstream record; no WS-2 or later workspace/path slice is admitted.
Continuation Action: `Advance to Hardening for the completed WS-1 slice and do not begin any later FB-005 workspace/path move until a separate explicit approval admits it.`

## Rollback Conditions

- rollback immediately if the moved harness requires production runtime path changes to function
- rollback immediately if the move requires launcher-target edits, root-entrypoint edits, audio-path edits, log-root edits, visual-asset moves, or user-facing desktop-path edits
- rollback immediately if direct reference sync reveals broader implicit coupling than the admitted slice allows
- rollback immediately if validation cannot prove the harness remains dev-only and outside shipped runtime reachability

## H-1 Hardening Record

H-1 pressure-tests whether the completed WS-1 slice is coherent enough to move into Live Validation without widening the branch into another workspace/path move, runtime path edit, launcher edit, audio edit, logs edit, visual-asset move, or user-facing desktop-path change.

### Hardening Findings

- Governance Gap: current-state canon still reflected Workstream-complete / Hardening-next truth after the admitted WS-1 slice had already finished. H-1 corrects current-state canon to Hardening-complete / Live-Validation-next truth.
- Path Ownership Pressure Test: PASS. No reverse dependency from runtime entrypoints, launcher paths, audio paths, logs, visual assets, or user-facing desktop paths into `dev/desktop/` or `dev/desktop/orin_desktop_test.py` was found.
- Reference Integrity And Path-Math Pressure Test: PASS with one non-blocking dev-only residual risk. The moved harness now resolves repo-root imports correctly from `dev/desktop/`, but it still names historical file `jarvis_core_desktop.html` while the current desktop asset on disk is `jarvis_visual/orin_core_desktop.html`. Because the harness intentionally crashes and production paths do not consume that reference, H-1 records this as a dev-only residual risk rather than a production coupling issue.
- Runtime Non-Reachability Pressure Test: PASS. Production entrypoint truth remains `launch_orin_desktop.vbs` -> `desktop/orin_desktop_launcher.pyw` -> `desktop/orin_desktop_main.py`, and no production path now references the moved harness.
- Rollback Viability Pressure Test: PASS. The implementation delta remains a single-file rename plus local path-math update and direct path-truth docs updates. Rolling back the slice stays bounded and does not require launcher, runtime, audio, logs, or visual-asset rewiring.
- Hidden Coupling Pressure Test: PASS. The remaining coupling is intentional one-way dev-harness consumption of runtime modules; no reverse runtime or launcher ownership leaked into `dev/desktop/`.
- Bounded-Stop Enforceability: PASS after correction. The workstream doc now carries the formal `## Seam Continuation Decision` block, so stopping after WS-1 is explicitly authorized by scope rather than left as implied prose.
- Scope Check: H-1 adds docs/canon evidence and phase-state repair only. No new runtime, launcher, audio, logs, visual-asset, or user-facing desktop-path implementation was introduced by this pass.

### Hardening Corrections

- Current-state canon is updated from Workstream-complete / Hardening-next wording to Hardening-complete / Live-Validation-next wording.
- The slice now explicitly records the non-blocking dev-only residual risk around historical visual filename `jarvis_core_desktop.html` so later validation does not overclaim visual-asset correctness.
- No helper, validator, runtime, launcher, audio, logs, visual-asset, release, or User Test Summary artifact was added during H-1.

### H-1 Completion Decision

- H-1 Result: Complete / green.
- User-facing impact: none. This pass changes docs/canon only.
- Next legal phase: Live Validation.
- Stop condition: phase boundary reached; Hardening is complete after H-1.

### H-1 Validation Results

- `python dev\orin_branch_governance_validation.py`: PASS, 1138 checks.
- `git diff --check`: PASS with line-ending normalization warnings only and no whitespace errors.
- `python -m py_compile dev\desktop\orin_desktop_test.py`: PASS.
- `python dev\desktop\orin_desktop_test.py`: PASS for bounded validation; the harness initializes from `dev/desktop/`, prints its expected banner, and exits only at the intentional `RuntimeError(\"Jarvis test crash triggered intentionally\")`.
- Reverse-coupling scan: PASS; no `dev/desktop`, `from dev`, or `import dev` reference appears in `main.py`, `launch_orin_desktop.vbs`, `desktop/`, `Audio/`, or `assistant_personas.py`.
- Asset-path integrity scan: recorded residual dev-only risk; `jarvis_visual/jarvis_core_desktop.html` does not exist while `jarvis_visual/orin_core_desktop.html` does.
