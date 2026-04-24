# FB-042 Desktop Entrypoint Runtime Refinement

## Identity

- ID: `FB-042`
- Title: `Desktop entrypoint runtime refinement`

## Record State

- `Promoted`

## Status

- `Active`

## Canonical Branch

- `feature/fb-042-desktop-entrypoint-runtime-refinement`

## Current Phase

- Phase: `Workstream`

## Phase Status

- FB-042 is now the active promoted implementation workstream on `feature/fb-042-desktop-entrypoint-runtime-refinement`.
- Branch Readiness is complete and durable on this branch.
- Latest public prerelease truth is `v1.6.6-prebeta`.
- `v1.6.6-prebeta` is live at `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.6-prebeta` on target commit `deeaa691a79dd01897f6aed82f087970db7019b3`.
- FB-005 is Released / Closed in `v1.6.6-prebeta`, and release debt is clear in canon.
- WS-1 desktop shortcut launch-path runtime refinement is admitted and active.
- The admitted WS-1 slice is runtime-bearing and user-facing because it targets the real Windows-facing desktop shortcut / VBS / launcher / runtime path.
- Broader `main.py` reshaping and broader workspace follow-through are explicitly deferred; they are not admitted by inertia on this branch.
- The historical FB-042 branch-authority record is preserved for traceability only and no longer owns active execution truth.

## Branch Class

- `implementation`

## Blockers

None.

## Entry Basis

- `v1.6.6-prebeta` is published and validated, and FB-005 release debt is clear.
- Repo audit showed the recent train had become planning/governance/repair heavy with too little runtime or user-facing progress.
- FB-042 was originally framed too broadly as a planning-only Step 5 / broader-workspace lane, which risked creating another non-runtime branch.
- The current shipped user-facing desktop path is already concrete and reusable: `launch_orin_desktop.vbs` -> `desktop/orin_desktop_launcher.pyw` -> `desktop/orin_desktop_main.py`.
- Existing reusable validation already covers this path through `dev/orin_desktop_entrypoint_validation.py` and the released FB-038 user-facing desktop shortcut evidence.
- Reorienting FB-042 to start on the real desktop launch path is the smallest safe correction that creates actual product-facing movement without widening into broader workspace reshaping immediately.

## Exit Criteria

- FB-042 is promoted and routed through this canonical workstream doc.
- The branch name, backlog, roadmap, workstreams index, branch-record index, and carry-forward truth all agree on the runtime-bearing FB-042 lane.
- WS-1 is admitted with exact owned paths, non-goals, validation coverage, rollback conditions, and user-facing shortcut contract.
- The admitted slice touches the real desktop entrypoint/runtime/user-facing launch path and does not collapse back into a docs-only or planning-only Workstream.
- Broader `main.py` reshaping and broader workspace follow-through stay explicitly out of scope unless a later bounded seam admits them.

## Rollback Target

- `Branch Readiness`

## Next Legal Phase

- `Workstream`

## Branch Objective

- Convert FB-042 from a vague planning-only Step 5 bucket into a real runtime-bearing desktop entrypoint implementation lane.
- Start on the shipped desktop launch path that users actually touch instead of bundling root reshaping, broader workspace movement, and runtime behavior into one oversized planning identity.
- Reuse the existing desktop entrypoint validation baseline and historical FB-038 shortcut evidence so follow-through begins from real product behavior rather than from new governance scaffolding.

## Target End-State

- FB-042 owns a bounded desktop entrypoint runtime lane with a truthful canonical workstream record.
- WS-1 is explicitly constrained to the current Windows-facing shortcut / VBS / launcher / runtime chain.
- Later `main.py` reshaping or broader workspace follow-through remains separate and explicit instead of silently piggybacking on the first runtime slice.

## Scope

- desktop user-facing launch-path refinement for the current shipped entry chain
- current Windows-facing shortcut / VBS / launcher / runtime handoff behavior
- direct validation and proof for entrypoint readiness, startup markers, tray/overlay routing, and user-facing shortcut applicability
- canon updates required to keep this branch truthful as a promoted runtime-bearing implementation lane

## Non-Goals

- no `main.py` reshaping in WS-1
- no broader workspace or root-ownership reorganization in WS-1
- no audio-path changes
- no `logs/` ownership changes
- no visual-asset relocation
- no installer or packaging redesign
- no expansion into unrelated tray/task/action authoring work already released in FB-038

## Expected Seam Families And Risk Classes

- Desktop shortcut / VBS launch-path family; risk class: user-facing entrypoint and Windows-facing launch behavior
- Launcher/runtime handoff family; risk class: startup sequencing, process ownership, and regression on the shipped desktop route
- Entrypoint validation family; risk class: validation coverage and shortcut-gate proof
- Scope-control family; risk class: preventing WS-1 from widening into `main.py` reshaping or broader workspace movement

## Admitted Implementation Slice

- Slice ID: `WS-1 desktop shortcut launch-path runtime refinement`
- Goal: refine the real user-facing desktop launch path without widening into broader Step 5 / workspace restructuring
- In-Scope Paths:
  - `launch_orin_desktop.vbs`
  - `desktop/orin_desktop_launcher.pyw`
  - `desktop/orin_desktop_main.py`
  - `dev/orin_desktop_entrypoint_validation.py`
- Out-Of-Scope Paths:
  - `main.py`
  - `Docs/workspace_layout_plan.md` except for direct path-truth notes if required by implementation
  - `Audio/`
  - `jarvis_visual/`
  - `logs/`
  - installer/config packaging surfaces
  - unrelated tray/task/action authoring code outside the entrypoint path
- Allowed Changes:
  - bounded runtime and user-facing launch-path refinement on the existing VBS / launcher / runtime chain
  - validation updates in `dev/orin_desktop_entrypoint_validation.py` required to prove the slice
  - direct canon updates required to keep the admitted WS-1 slice truthful
- Prohibited Changes:
  - no `main.py` reshaping
  - no broader workspace relocation
  - no audio-path rewiring
  - no visual-asset reorganization
  - no installer or shortcut-registration redesign
  - no unrelated runtime UX expansion beyond the launch path itself

## Planning-Loop Guardrail

Implementation Delta Class: `runtime/user-facing`
Docs-Only Workstream: `No`
Planning-Loop Bypass User Approval: `None`
Planning-Loop Bypass Reason: `None`

- FB-042 is an implementation branch and must keep Workstream focused on the admitted runtime-bearing WS-1 slice.
- Branch rename, promotion, canon sync, or release posture do not count as Workstream progress by themselves.
- Any future docs-only or canon-only FB-042 pass requires explicit USER approval before it can bypass implementation execution.

## User-Facing Shortcut Contract

- User-Facing Shortcut Path: `C:\Users\anden\OneDrive\Desktop\Nexus Desktop Launcher.lnk`
- Equivalent Entry Path: `launch_orin_desktop.vbs` -> `desktop/orin_desktop_launcher.pyw` -> `desktop/orin_desktop_main.py`
- User-Facing Shortcut Validation: `PENDING`
- `User-Facing Shortcut Validation Pending` is expected to remain a blocker later in Live Validation until the declared path is re-validated or explicitly waived with evidence.

## Validation Contract

- run `python dev\orin_branch_governance_validation.py`
- run `git diff --check`
- confirm `Docs/Main.md` routes this promoted FB-042 workstream record
- confirm `Docs/feature_backlog.md` marks FB-042 as `Promoted`, `Active`, cites this canonical workstream doc, and no longer leaves FB-042 as selected-next planning-only
- confirm `Docs/prebeta_roadmap.md` records FB-042 as the current active promoted workstream and no longer routes through a planning-only branch-authority posture
- confirm `Docs/workstreams/index.md` lists this record under Active
- confirm `Docs/branch_records/index.md` no longer leaves an active FB-042 branch-authority owner after promotion
- confirm the admitted WS-1 slice is runtime-bearing on the real desktop launch path
- confirm `main.py` and broader workspace follow-through remain explicitly out of scope for WS-1

## Branch Readiness Validation Results

- Source-truth routing: `Docs/Main.md`, `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, `Docs/workstreams/index.md`, and the historicalized FB-042 branch record now route through this promoted workstream instead of a planning-only branch-authority surface.
- Branch-truth correction: the branch is renamed from `feature/fb-042-step5-entrypoint-planning` to `feature/fb-042-desktop-entrypoint-runtime-refinement` so git truth matches the admitted runtime-bearing target.
- Planning-loop correction: broader Step 5 / workspace language is no longer allowed to stand in for actual implementation admission; Branch Readiness now ends with a concrete runtime-bearing WS-1 on the shipped desktop entrypoint path.
- Implementation-slice admission: PASS. WS-1 touches the real user-facing desktop shortcut / VBS / launcher / runtime chain and keeps `main.py` plus broader workspace movement out of scope.

## User Test Summary Strategy

- Branch Readiness itself does not change user-facing behavior, so no manual User Test Summary is required for the reorientation pass.
- The admitted WS-1 slice is user-facing and desktop-relevant, so later Hardening / Live Validation must use the canonical `## User Test Summary` artifact and the user-facing desktop shortcut gate unless implementation evidence proves a narrow waiver is valid.
- `dev/orin_desktop_entrypoint_validation.py` is supporting proof only; it will not replace the later real shortcut gate.

## Later-Phase Expectations

- Workstream begins now with WS-1; do not reopen planning-only framing as a substitute for execution.
- Any later seam that touches `main.py` or broader workspace follow-through must be separately admitted after WS-1 evidence exists.
- Hardening must pressure-test launch-path ownership, startup sequencing, shortcut expectations, validator coverage, and rollback viability for the implemented WS-1 delta.
- Live Validation must classify shortcut applicability from the real shipped path and clear or waive the user-facing shortcut blocker with evidence.

## Initial Workstream Seam Sequence

Seam 1: `WS-1 desktop shortcut launch-path runtime refinement`

- Status: Admitted / not yet executed
- Goal: improve the real user-facing desktop launch path on the existing VBS / launcher / runtime chain
- Scope: bounded runtime and user-facing entrypoint refinement plus direct validator updates required to prove it
- Non-Includes: no `main.py` reshaping, no broader workspace moves, no audio-path changes, no visual-asset reorganization, no installer redesign

## Active Seam

Active seam: `WS-1 desktop shortcut launch-path runtime refinement`

- Workstream is active.
- WS-1 is admitted and must execute next.
- No later FB-042 seam is admitted yet.
- Broader `main.py` reshaping and broader workspace follow-through remain explicitly blocked until a later bounded admission.

## Seam Continuation Decision

Continue Decision: `Continue.`
Next Active Seam: `WS-1 desktop shortcut launch-path runtime refinement`
Stop Condition: `None yet; WS-1 is admitted and unexecuted.`
Continuation Action: `Execute WS-1 on the real desktop launch path before opening any later FB-042 seam or reintroducing broader planning-only follow-through.`
