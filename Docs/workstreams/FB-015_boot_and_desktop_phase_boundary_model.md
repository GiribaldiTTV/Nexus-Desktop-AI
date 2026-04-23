# FB-015 Boot And Desktop Phase-Boundary Model

## Identity

- ID: `FB-015`
- Title: `Boot and desktop phase-boundary model`

## Record State

- `Promoted`

## Status

- `Active`

## Release Stage

- `Slice-staged`

## Canonical Branch

- `feature/fb-015-boot-desktop-phase-boundary-model`

## Current Phase

- Phase: `Workstream`

## Phase Status

- `Workstream active; WS-1 complete; WS-2 next`
- FB-004 is released and closed in `v1.6.3-prebeta`.
- Latest public prerelease truth is `v1.6.3-prebeta`.
- Release debt is clear.
- FB-015 is now the active promoted workstream on `feature/fb-015-boot-desktop-phase-boundary-model`.
- Branch Readiness is complete.
- WS-1 current boot/desktop boundary inventory and ownership map is complete.
- WS-2 lifecycle and phase-boundary state framing is admitted next.
- A narrow supporting canon sync for released FB-040 Sensor HUD beta admission may ride on this branch only as docs/governance-only source-of-truth maintenance; it does not reopen FB-040, change FB-015 runtime scope, or replace WS-1 as the next admitted FB-015 seam.
- A requested future-lane admission for `FB-042 Stream Deck Integration via Elgato MCP` was reviewed and explicitly deferred because backlog identity, roadmap sequencing, and new auxiliary planning-reference canon for that lane would exceed the current FB-015 branch boundary and remains out of scope for WS-1.
- No FB-015 runtime, launcher, shortcut, renderer lifecycle, UI, installer, source-tree, or release work has started.

## Branch Class

- `implementation`

## Blockers

None.

## Entry Basis

- `main` reached `v1.6.3-prebeta` at `9f5ae9a78c7dbff79322089bca370fa49da38598`.
- FB-004 post-release canon closure is complete.
- Release debt is clear.
- FB-015 was selected as the priority-led successor after FB-004.
- Branch Readiness is the first legal FB-015 surface before any implementation-facing seam begins.

## Branch Objective

- Define the boot and desktop phase-boundary model that sits between the closed FB-025 milestone-taxonomy clarification and the closed FB-004 future boot-orchestrator planning frame.
- Name the ambiguity around boot ownership, desktop launcher authority, renderer readiness, desktop-settled state, diagnostics evidence, persisted state, and rollback ownership.
- Establish implementation-admission rules so later seams can change startup, launcher, desktop, renderer, shortcut, diagnostics, or user-facing surfaces only after the affected boundary, proof path, rollback path, and User Test Summary trigger are explicit.

## Target End-State

- FB-015 has a canonical phase-boundary model for boot authority, desktop authority, renderer readiness, desktop-settled outcomes, diagnostics evidence, and rollback ownership.
- Workstream execution can begin with a source and boundary inventory before implementation is considered.
- The branch has a validation contract that distinguishes docs/canon proof from runtime, shortcut, desktop-session, User Test Summary, and release proof.

## Scope

- Inventory current boot, desktop, launcher, renderer, diagnostics, persisted-state, and user-facing entrypoint ownership.
- Define phase-boundary vocabulary for boot, launch, renderer-ready, desktop-settled, failed-start, recovery, and rollback states.
- Define validation, User Test Summary, shortcut, and rollback triggers for later boundary-affecting seams.

## Non-Goals

- No runtime behavior changes.
- No launcher behavior changes.
- No desktop shortcut changes.
- No renderer lifecycle implementation.
- No service, autostart, installer, packaging, or OS integration changes.
- No UI implementation.
- No source tree reorganization.
- No FB-025 historical rewrite.
- No FB-004 future boot-orchestrator implementation.
- No release packaging, tag creation, or public release editing.

## Expected Seam Families And Risk Classes

- Current boundary inventory and ownership family; risk class: architecture/runtime-boundary.
- Phase vocabulary and lifecycle handoff family; risk class: lifecycle/launcher.
- Trust, startup, and readiness evidence family; risk class: validation/observability.
- Implementation admission and rollback contract family; risk class: governance/implementation.
- User-facing startup path classification family; risk class: desktop/user-facing.

## Validation Contract

- Run `python dev\orin_branch_governance_validation.py`.
- Run `git diff --check`.
- Confirm `Docs/Main.md` routes this workstream record.
- Confirm `Docs/feature_backlog.md` marks FB-015 as `Promoted`, `Active`, and cites this doc.
- Confirm `Docs/workstreams/index.md` lists FB-015 under Active.
- Confirm `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, and `Docs/workstreams/index.md` record FB-015 as the active Workstream with WS-1 complete and WS-2 next.
- Confirm FB-004 remains Released / Closed in `v1.6.3-prebeta`.
- Confirm the previously recorded supporting canon sync remains limited to active FB-015 branch authority wording, `Docs/workstreams/FB-040_monitoring_thermals_performance_hud_surface.md`, and `Docs/validation_helper_registry.md`, and does not reopen FB-040 or change the admitted FB-015 seam chain.
- Confirm requested future-lane `FB-042 Stream Deck Integration via Elgato MCP` admission remains deferred on this branch and does not add backlog, roadmap, workstream, or auxiliary planning-reference canon.
- Confirm no runtime, launcher, shortcut, renderer lifecycle, UI, installer, source-tree, release, helper-code, or desktop-export surface changed during WS-1.

## Branch Readiness Validation Results

- `python dev\orin_branch_governance_validation.py`: PASS, 916 checks.
- `git diff --check`: PASS; no whitespace errors.
- Scope validation: PASS; this follow-up docs-only clarification changes only the active FB-015 branch authority wording and does not add backlog, roadmap, workstream, auxiliary planning-reference, phase-governance, runtime, or helper-file changes.
- Admission validation: PASS; FB-015 remains the active promoted workstream, WS-1 current boot/desktop boundary inventory and ownership map remains next, FB-040 is not reactivated, and requested future-lane `FB-042 Stream Deck Integration via Elgato MCP` admission remains deferred on this branch.
- Boundary validation: PASS; no backlog, roadmap, workstream, or auxiliary planning-reference canon is added on this branch, and future-lane `FB-042 Stream Deck Integration via Elgato MCP` admission is preserved as a later legal-surface task.

## User Test Summary Strategy

- Branch Readiness and WS-1 are docs/canon only and do not change user-facing behavior.
- No desktop shortcut validation, desktop export, or manual User Test Summary handoff is required during Branch Readiness or WS-1.
- If a later seam changes startup, launcher, shortcut, visible startup state, user-facing copy, UI, installer behavior, or another operator-facing path, FB-015 must add the exact `## User Test Summary` artifact and desktop export required by governance before Live Validation can advance.

## Later-Phase Expectations

- Workstream must execute bounded seams and keep the active seam recorded here.
- Workstream must start with WS-1 and must not begin runtime implementation, launcher implementation, shortcut changes, renderer lifecycle work, UI work, installer work, source movement, or release work unless a later seam explicitly admits the affected surfaces.
- Hardening must pressure-test the phase-boundary frame, lifecycle handoffs, ownership boundaries, diagnostics evidence roots, rollback boundaries, stale-helper caveats, implementation-admission contract, and User Test Summary triggers.
- Live Validation must classify shortcut applicability and User Test Summary applicability based on the completed FB-015 delta.
- PR Readiness must prove merge-target canon completeness, clean branch truth, successor selection, User Test Summary state, and live PR state before PR green.

## Initial Workstream Seam Sequence

Seam 1: Current boot/desktop boundary inventory and ownership map

- Status: Completed.
- Goal: inventory current boot, launcher, renderer, desktop-settled, diagnostics, persisted-state, rollback, and user-facing entrypoint boundaries before implementation is considered.
- Scope: docs/canon source inventory, boundary vocabulary, current ownership map, evidence roots, ambiguity capture, validation trigger classification, rollback boundary, and implementation-admission checklist.
- Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no source tree reorganization, no release work, and no public release editing.

Seam 2: Lifecycle and phase-boundary state framing

- Status: Admitted next.
- Goal: define the lifecycle states and handoff boundaries between dev-only boot framing, production desktop launch control, renderer readiness, desktop-settled state, failure, recovery, and rollback.
- Scope: docs/canon lifecycle vocabulary, phase-boundary state framing, ownership handoff notes, ambiguity capture, and implementation-readiness risks.
- Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no source tree reorganization, no release work, and no public release editing.

Seam 3: Validation and admission contract for future boot/desktop boundary implementation

- Status: Planned / not yet admitted beyond WS-2.
- Goal: define the proof and admission contract required before future seams can change startup, launcher, renderer, shortcut, diagnostics, persisted-state, or user-facing boot/desktop surfaces.
- Scope: validation gates, shortcut/User Test Summary triggers, rollback proof, helper reuse posture, implementation-admission checklist, and later-phase evidence expectations.
- Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no source tree reorganization, no release work, and no public release editing.

## Active Seam

Active seam: WS-1 current boot/desktop boundary inventory and ownership map is complete; WS-2 lifecycle and phase-boundary state framing is admitted next.

- BR-1 Status: Completed in this pass.
- BR-1 Boundary: promote FB-015 and define the branch objective, target end-state, seam families, validation contract, User Test Summary strategy, later-phase expectations, and first Workstream seam.
- BR-1 Non-Includes: no runtime behavior, launcher behavior, shortcut behavior, renderer lifecycle behavior, UI implementation, installer work, source tree reorganization, release packaging, tag creation, or public release editing.
- WS-1 Status: Completed / executed.
- WS-1 Boundary: docs/canon current boot/desktop boundary inventory and ownership map only.
- WS-1 Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no source tree reorganization, no release work, and no public release editing.
- WS-2 Status: Admitted next / not executed.
- WS-2 Boundary: docs/canon lifecycle and phase-boundary state framing only.
- WS-2 Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no source tree reorganization, no release work, and no public release editing.

## Seam Continuation Decision

Continue Decision: `continue`
Next Active Seam: `WS-2 lifecycle and phase-boundary state framing`
Stop Condition: `stop only if scope, phase authority, or validation truth breaks`
Continuation Action: execute FB-015 Workstream WS-2 after WS-1 validation is green and durably committed.

## WS-1 Execution Record

WS-1 is docs/canon only. It inventories the current boot and desktop phase boundaries and records the current ownership map that later FB-015 seams must use before any implementation-facing boundary change is admitted.

### Current Boot And Desktop Phase Boundary Inventory

Current user-facing production desktop-launch path:

- `launch_orin_desktop.vbs` is the repository-root Windows launch shim. It resolves the repo root from the script location, points at the configured `pythonw.exe`, and launches `desktop\orin_desktop_launcher.pyw` with a hidden window.
- `desktop/orin_desktop_launcher.pyw` is the current production desktop phase-control entrypoint. It defaults to `desktop/orin_desktop_main.py`, allows harness-only target and log-root overrides through `JARVIS_HARNESS_TARGET_SCRIPT` and `JARVIS_HARNESS_LOG_ROOT`, starts the renderer process, and observes `RENDERER_MAIN|STARTUP_READY`.
- `desktop/orin_desktop_main.py` is the current production renderer/runtime entrypoint. It parses `--runtime-log` and `--startup-abort-signal`, constructs `DesktopRuntimeWindow`, initializes tray and hotkey services, defers window show until core visualization readiness, emits `RENDERER_MAIN|...` milestones, and requests passive default handoff to `state=dormant`.
- `desktop/desktop_renderer.py::DesktopRuntimeWindow` is the current desktop presentation surface. It owns core-visualization readiness/visibility signaling, desktop-mode enablement and reinforcement, command-overlay toggling, tray-origin Create Custom Task routing, and renderer shutdown initiation.

Current dev-only boot and handoff path:

- `main.py` is the current boot-phase prototype and validation path, not the production desktop-launch authority. It accepts `--boot-profile manual` and `--boot-profile auto_handoff_skip_import`, writes `BOOT_MAIN|...` markers under `dev/logs/...`, constructs `DesktopRuntimeWindow` directly, and performs a dev-only boot-to-desktop handoff.
- `dev/launchers/launch_orin_main_dev.vbs` and `dev/launchers/launch_orin_main_auto_handoff_skip_import.vbs` launch `main.py` for manual or auto-handoff validation flows.
- `dev/orin_boot_transition_capture.py` and `dev/orin_boot_transition_verification.py` validate the `main.py` boot-transition path and prove `BOOT_MAIN|...` handoff markers through dev-log evidence only.

Current shared control and validation support surfaces:

- `desktop/single_instance.py` provides `SingleInstanceGuard`, `NamedSignal`, and `acquire_or_prompt_replace`. Both the production launcher and the dev-only boot prototype reuse the same `Local\\JarvisRuntimeSingletonV1` mutex and `Local\\JarvisRuntimeRelaunchRequestV1` relaunch event, but that shared primitive does not collapse their separate phase ownership.
- `dev/orin_desktop_entrypoint_validation.py` validates direct renderer startup, tray readiness, overlay routing, and `RENDERER_MAIN|...` startup milestones without making launcher-owned recovery decisions.
- `dev/orin_desktop_launcher_healthy_validation.py` validates the launcher-to-renderer healthy path through harness log-root overrides and `RENDERER_MAIN|STARTUP_READY` evidence.
- `dev/orin_desktop_launcher_regression_harness.py` remains a registered launcher-regression helper, but its current legacy-path constants are not repaired in WS-1 and therefore do not redefine current phase truth.

Current evidence and persisted-state surfaces:

- Live launcher/runtime evidence defaults to root `logs/` through `desktop/orin_desktop_launcher.pyw`, including `Runtime_<timestamp>_<token>.txt`, `crash/Crash_<timestamp>_<token>.txt`, `diagnostics_status.txt`, `diagnostics_stop.signal`, and `renderer_startup_abort.signal`.
- Launcher-managed historical outcome state persists through `%LOCALAPPDATA%/Nexus Desktop AI/state/jarvis_history_v1.jsonl`, with harness log-root overrides only in validation contexts.
- Dev and harness proof belongs under `dev/logs/<lane>/...`, including boot-transition, desktop-entrypoint, and launcher-healthy validation roots.

### Ownership Map Across Current Boundaries

User-facing launch initiation boundary:

- Windows shell and the user own invoking the desktop entry surface.
- `launch_orin_desktop.vbs` owns resolving the repo root, fixed `pythonw.exe` path, and hidden process launch of the production launcher.
- This boundary does not own retry policy, renderer readiness, tray behavior, diagnostics finalization, or boot-phase behavior.

Production desktop phase-control boundary:

- `desktop/orin_desktop_launcher.pyw` owns single-instance negotiation, relaunch coordination, renderer process spawning, startup observation, cooperative startup-abort control flow, recovery attempt sequencing, diagnostics UI launch, failure voice routing, crash-report generation, and final runtime outcome classification.
- The production launcher also owns live runtime evidence roots and historical outcome persistence.
- This boundary does not own the renderer's visual hierarchy, command overlay behavior, tray command routing after startup, or the dev-only boot prototype's handoff flow.

Production desktop presentation boundary:

- `desktop/orin_desktop_main.py` and `desktop/desktop_renderer.py::DesktopRuntimeWindow` own Qt application/window construction, visual HTML load, core-visualization readiness and first-visible markers, tray identity and discovery cue behavior, command-overlay and tray command routing, hotkey startup, desktop-mode attachment/reinforcement, passive default handoff to `state=dormant`, and clean renderer shutdown initiation.
- This boundary does not own recovery policy, diagnostics finalization, crash classification, or historical outcome persistence.

Dev-only boot-phase prototype boundary:

- `main.py` owns dev-only boot-profile selection, boot-window topology, staged voice/command flow, boot-to-desktop transition markers, and dev-only handoff evidence.
- This boundary does not own current production desktop-launch truth, launcher-owned retry/recovery policy, live diagnostics finalization, or release-facing user entrypoint authority.

Shared single-instance and relaunch primitive boundary:

- `desktop/single_instance.py` owns the reusable mutex, relaunch-signal, and replace-session prompting primitive.
- The primitive is shared by the production launcher and the dev-only boot prototype, but it is infrastructure ownership only; it does not decide whether current truth is boot-owned or desktop-owned.

Evidence and state-root boundary:

- Live runtime, crash, status, startup-abort, and history truth remain launcher-owned.
- Root `logs/` remains the live launcher/runtime evidence root.
- `dev/logs/<lane>/...` remains dev and harness proof only.
- Future work must not move evidence or persisted state ownership without an explicit admitted seam.

### WS-1 Boundary Conclusions

- Current production truth begins at the desktop launcher path; there is no admitted production boot phase ahead of it.
- Current boot-phase behavior exists only in the dev-only `main.py` prototype and its validation paths.
- The current boot/desktop boundary problem is therefore an authority split between future boot intent, a dev-only boot prototype, and the shipped desktop launcher/runtime path rather than a single already-admitted product boot stack.

### WS-1 Validation Results

- `python dev\orin_branch_governance_validation.py`: PASS, 909 checks.
- `git diff --check`: PASS; no whitespace errors.
- Scope validation: PASS; WS-1 changed docs/canon only in the FB-015 workstream record, backlog, roadmap, and workstream index.
- Boundary validation: PASS; current production desktop-launch surfaces, dev-only boot prototype surfaces, shared single-instance primitives, evidence roots, and ownership boundaries are recorded without runtime or helper changes.

### WS-1 Completion Decision

- WS-1 Result: Complete / green.
- Validation Layer: docs/canon plus live repo entrypoint inspection.
- User Test Summary Applicability: not applicable for WS-1 because this seam changes docs/canon only and adds no user-visible behavior.
- Cleanup: no programs, helper processes, windows, temporary files, probes, or runtime artifacts were created.
- Continue/Stop Decision: continue to WS-2 under the admitted bounded Workstream chain.

## Supporting Canon Sync

This active branch may carry tightly scoped supporting canon sync when the change stays docs/governance-only, preserves FB-015 as the active workstream, and does not widen into runtime or branch-selection churn.

Admitted supporting canon sync for this pass:

- active FB-015 branch authority clarification that requested future-lane `FB-042 Stream Deck Integration via Elgato MCP` admission remains deferred on this branch
- post-release future beta admission contract additions in `Docs/workstreams/FB-040_monitoring_thermals_performance_hud_surface.md`
- future Sensor HUD helper-family reservation in `Docs/validation_helper_registry.md`

Non-includes for this supporting canon sync:

- no FB-040 reactivation as the active workstream
- no FB-042 backlog admission, roadmap sequencing change, workstream creation, or `Docs/stream_deck_integration_design.md` planning-reference creation on this branch
- no backlog, roadmap, or workstreams-index selection changes
- no `Docs/phase_governance.md` policy expansion
- no runtime code, helper-file, installer, shortcut, tray, overlay, or UI changes
- no change to the admitted next FB-015 seam; WS-1 remains next

## Reuse Baseline

- `Docs/workstreams/FB-004_future_boot_orchestrator_layer.md`
- `Docs/workstreams/FB-025_boot_desktop_milestone_taxonomy_clarification.md`
- `Docs/feature_backlog.md`
- `Docs/prebeta_roadmap.md`
- `Docs/workstreams/index.md`
- `Docs/phase_governance.md`
- `dev/orin_branch_governance_validation.py`

## Exit Criteria

- WS-1 current boot and desktop phase boundaries are recorded.
- The ownership map across the current user-facing launch shim, production launcher, production renderer, dev-only boot prototype, shared single-instance primitives, and evidence/state roots is recorded.
- `Docs/Main.md`, `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, and `Docs/workstreams/index.md` route FB-015 as the active promoted Workstream with WS-1 complete and WS-2 next.
- FB-004 remains Released / Closed and release debt remains clear.
- No runtime, launcher, shortcut, renderer lifecycle, UI, installer, source-tree, release, helper-code, or desktop-export surface changed during WS-1.
- Validation is green.

## Rollback Target

- `Branch Readiness`
- Revert the FB-015 Branch Readiness canon commit and return FB-015 to selected-only / registry-only after FB-004 release closure.

## Next Legal Phase

- `Workstream`

## User Test Summary

Not applicable during WS-1. FB-015 WS-1 is docs/canon only and does not change user-facing behavior.
