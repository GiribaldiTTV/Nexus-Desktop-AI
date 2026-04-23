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

- Phase: `Branch Readiness`

## Phase Status

- Current execution surface is `Active Branch`.
- `v1.6.5-prebeta` is live at `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.5-prebeta` on target commit `7c2933d6427feb08a1139ba7f5ba2393eb61f1e1`.
- FB-030 is Released / Closed in `v1.6.5-prebeta`, latest public prerelease truth is `v1.6.5-prebeta`, and merged-unreleased release debt is clear.
- FB-005 is promoted from selected-only / `Registry-only` into an active canonical workstream on `feature/fb-005-workspace-path-planning`.
- Branch Readiness is complete and Workstream is admitted for one bounded path-sensitive slice only.
- Approved first slice: `desktop/orin_desktop_test.py` -> `dev/desktop/orin_desktop_test.py`.
- Runtime entrypoints, launcher paths, audio paths, logs, visual assets, and user-facing desktop paths remain outside this admitted slice.
- No workspace movement, file relocation, import rewiring, launcher-route change, log-root change, visual-asset move, or user-facing path change has started yet.

## Branch Class

- `implementation`

## Blockers

None.

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
- Workstream can begin with the admitted WS-1 slice `desktop/orin_desktop_test.py` -> `dev/desktop/orin_desktop_test.py` without widening scope by inertia.

## Rollback Target

- `Branch Readiness`

## Next Legal Phase

- `Workstream`

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
- update the moved harness only as needed to preserve its own path math, imports, and dev-only behavior from the new location
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
- confirm `desktop/orin_desktop_test.py` remains outside runtime entrypoint, launcher, audio, logs, visual-asset, and user-facing desktop shortcut ownership

## Branch Readiness Validation Results

- `python dev\orin_branch_governance_validation.py`: PASS, 1145 checks.
- `git diff --check`: PASS with line-ending normalization warnings only and no whitespace errors.
- Runtime reachability review: current shipped runtime path remains `launch_orin_desktop.vbs` -> `desktop/orin_desktop_launcher.pyw` -> `desktop/orin_desktop_main.py`, and the admitted slice does not own any part of that route.
- Path ownership review: admitted scope is limited to `desktop/orin_desktop_test.py` -> `dev/desktop/orin_desktop_test.py`, with launcher paths, runtime entrypoints, audio paths, logs, visual assets, and user-facing desktop paths explicitly outside the slice.
- Canon routing review: `Docs/Main.md`, `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, `Docs/workstreams/index.md`, and `Docs/branch_records/index.md` route FB-005 as the promoted active lane and do not leave it as selected-next / `Registry-only` current-state truth.
- Admission validation target: Branch Readiness is complete only if the approved slice, ownership limits, validation coverage, runtime reachability proof, and rollback conditions are durably recorded without widening scope.

## User Test Summary Strategy

- Branch Readiness and the admitted WS-1 slice are not user-facing by default.
- No desktop shortcut validation, desktop export, or manual User Test Summary handoff is required for Branch Readiness closeout.
- If a later FB-005 slice touches runtime entrypoints, launcher paths, logs, visual assets, audio paths, or another user-facing path, that later slice must classify shortcut applicability and User Test Summary requirements explicitly before Live Validation can advance.

## Later-Phase Expectations

- Workstream is admitted only for the approved WS-1 slice in this record.
- Later FB-005 slices require separate explicit path-sensitive approval; this branch must not widen from the admitted harness relocation into Step 5 or broader workspace cleanup by inertia.
- Hardening must pressure-test path ownership, reference sync, validation coverage, runtime non-reachability proof, and rollback posture for the admitted slice.
- Live Validation must classify shortcut and User Test Summary applicability from the actual implemented delta, not from FB-005 as a whole.

## Initial Workstream Seam Sequence

Seam 1: `desktop/orin_desktop_test.py` -> `dev/desktop/orin_desktop_test.py`

- Status: Admitted.
- Goal: relocate the dev-only desktop crash/test harness into the dev-owned tree without changing production runtime ownership.
- Scope: move one file, update only its direct path references, preserve current behavior, and keep root-relative asset resolution intact from the new location.
- Non-Includes: no runtime entrypoint changes, no launcher-path changes, no audio-path changes, no logs changes, no visual-asset moves, no user-facing desktop-path changes, and no broader workspace restructuring.

## Active Seam

Active seam: `WS-1 desktop/orin_desktop_test.py -> dev/desktop/orin_desktop_test.py`

- Admission status: approved and ready for Workstream execution.
- Exact path boundary: the slice begins at `desktop/orin_desktop_test.py` and ends at `dev/desktop/orin_desktop_test.py`.
- Runtime-reachability constraint: the slice must preserve the current shipped runtime path untouched.
- Widening constraint: any requirement to touch `main.py`, `launch_orin_desktop.vbs`, launcher routing, audio paths, logs, visual assets, or user-facing desktop paths invalidates the slice and routes back to Branch Readiness.

## Rollback Conditions

- rollback immediately if the moved harness requires production runtime path changes to function
- rollback immediately if the move requires launcher-target edits, root-entrypoint edits, audio-path edits, log-root edits, visual-asset moves, or user-facing desktop-path edits
- rollback immediately if direct reference sync reveals broader implicit coupling than the admitted slice allows
- rollback immediately if validation cannot prove the harness remains dev-only and outside shipped runtime reachability
