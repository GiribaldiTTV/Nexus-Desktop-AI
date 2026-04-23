# FB-015 Boot And Desktop Phase-Boundary Model

## Identity

- ID: `FB-015`
- Title: `Boot and desktop phase-boundary model`

## Record State

- `Promoted`

## Status

- `Merged unreleased`

## Release Stage

- `Slice-staged`

## Target Version

- `v1.6.4-prebeta`

## Canonical Branch

- `feature/fb-015-boot-desktop-phase-boundary-model`

## Current Phase

- Phase: `Release Readiness`

## Phase Status

- `Release Readiness pending on updated main after PR #75 merged cleanly into main at 3e821e07ff91d814fd7aba9b50819f97d700a301`
- Repo state is `No Active Branch` while FB-015 carries merged-unreleased release debt for `v1.6.4-prebeta`.
- FB-004 is released and closed in `v1.6.3-prebeta`.
- Latest public prerelease truth is `v1.6.3-prebeta`.
- Release debt is active for `v1.6.4-prebeta`.
- FB-015 is the merged-unreleased release-debt owner on `main`, not an active promoted implementation branch.
- Branch Readiness is complete.
- WS-1 current boot/desktop boundary inventory and ownership map is complete.
- WS-2 lifecycle and phase-boundary state framing is complete.
- WS-3 validation and admission contract for future boot/desktop boundary implementation is complete.
- H-1 pressure test of the boot/desktop boundary inventory and ownership map, lifecycle and phase-boundary state framing, and future implementation admission contract is complete.
- LV-1 repo-truth alignment, user-facing shortcut applicability, User Test Summary applicability, desktop export applicability, cleanup posture, and waiver handling are complete.
- PR-1 merge-target canon completeness is complete.
- PR-2 selected-next workstream selection is complete with FB-029 planning-only.
- PR-3 live PR creation and validation is complete, and PR #75 is now merged.
- FB-029 merged through PR #76 into `main` at `0897fab768dc07385f83fab81434ba7926ecc4a1` and is now merged-unreleased inside the inherited `v1.6.4-prebeta` package; it no longer owns active implementation truth, and explicit product/legal approval still blocks any implementation-facing naming, licensing, release, runtime, or persona-surface work.
- Hardening clarified launcher-owned `STARTUP_READY_OBSERVED`, `normal exit complete`, and `failure flow complete` as explicit boundary states and tightened later shortcut-proof classification so direct repository launch-shim invocation is not treated as real user-facing shortcut proof by default.
- Live Validation confirmed the completed FB-015 delta remains docs/canon only, so user-facing shortcut validation and User Test Summary results are both waived for this milestone.
- PR Readiness derived `v1.6.4-prebeta` / `Pre-Beta v1.6.4` as the semantic post-merge release target because FB-015 remains a docs/canon-only architecture/admission milestone with `patch prerelease` release-floor semantics.
- PR Readiness selected FB-029 as the next planning-only workstream because it is the highest-priority remaining open backlog candidate after FB-015, while keeping implementation-facing admission blocked until explicit product/legal approval and updated-main admission.
- A narrow supporting canon sync for released FB-040 Sensor HUD beta admission remained bounded to docs/governance-only source-of-truth maintenance; it did not reopen FB-040, change FB-015 runtime scope, or alter the admitted FB-015 seam chain.
- A requested future-lane admission for `FB-042 Stream Deck Integration via Elgato MCP` was reviewed and explicitly deferred because backlog identity, roadmap sequencing, and new auxiliary planning-reference canon for that lane would exceed the current FB-015 branch boundary and remains out of scope for the completed FB-015 Workstream seam chain.
- No FB-015 runtime, launcher, shortcut, renderer lifecycle, UI, installer, source-tree, helper-code, or release work has started.

## Branch Class

- `implementation`

## Blockers

- `Release Debt`

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
- Confirm `Docs/feature_backlog.md` marks FB-015 as `Promoted`, `Merged unreleased`, carries `Target Version: v1.6.4-prebeta`, and cites this doc.
- Confirm `Docs/workstreams/index.md` lists FB-015 under Merged / Release Debt Owners and not under Active.
- Confirm `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, and `Docs/workstreams/index.md` record FB-015 as the merged-unreleased release-debt owner with `Repo State: No Active Branch`.
- Confirm `Docs/prebeta_roadmap.md` records `merged unreleased non-doc implementation debt exists: yes` and `current active workstream: none`.
- Confirm `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, `Docs/workstreams/index.md`, and `Docs/Main.md` route FB-029 as `Promoted`, `Merged unreleased`, and included in the inherited `v1.6.4-prebeta` package with no active implementation truth.
- Confirm FB-030 remains selected-only / `Registry-only`, its selected-next implementation branch remains not created, and any temporary `emergency canon repair` branch is not misclassified as FB-030 implementation-branch creation.
- Confirm the validator rejects active implementation workstream truth on `main` when the canonical branch is not `main`.
- Confirm FB-004 remains Released / Closed in `v1.6.3-prebeta`.
- Confirm the previously recorded supporting canon sync remains limited to active FB-015 branch authority wording, `Docs/workstreams/FB-040_monitoring_thermals_performance_hud_surface.md`, and `Docs/validation_helper_registry.md`, and does not reopen FB-040 or change the admitted FB-015 seam chain.
- Confirm requested future-lane `FB-042 Stream Deck Integration via Elgato MCP` admission remains deferred on this branch and does not add backlog, roadmap, workstream, or auxiliary planning-reference canon.
- Confirm no runtime, launcher, shortcut, renderer lifecycle, UI, installer, source-tree, release, helper-code, or desktop-export surface changed during WS-1 through WS-3, H-1, or LV-1.

## Branch Readiness Validation Results

- `python dev\orin_branch_governance_validation.py`: PASS, 916 checks.
- `git diff --check`: PASS; no whitespace errors.
- Scope validation: PASS; this follow-up docs-only clarification changes only the active FB-015 branch authority wording and does not add backlog, roadmap, workstream, auxiliary planning-reference, phase-governance, runtime, or helper-file changes.
- Admission validation: PASS; FB-015 remained the active promoted workstream at Branch Readiness closeout, WS-1 current boot/desktop boundary inventory and ownership map was the admitted next seam at that point, FB-040 was not reactivated, and requested future-lane `FB-042 Stream Deck Integration via Elgato MCP` admission remained deferred on this branch.
- Boundary validation: PASS; no backlog, roadmap, workstream, or auxiliary planning-reference canon is added on this branch, and future-lane `FB-042 Stream Deck Integration via Elgato MCP` admission is preserved as a later legal-surface task.

## User Test Summary Strategy

- Branch Readiness, WS-1 through WS-3, H-1, LV-1, PR-1, PR-2, and PR-3 remain docs/canon only and do not change user-facing behavior.
- No desktop shortcut validation, desktop export, or manual User Test Summary handoff is required during Branch Readiness, WS-1 through WS-3, H-1, LV-1, PR-1, PR-2, or PR-3.
- If a later seam changes startup, launcher, shortcut, visible startup state, user-facing copy, UI, installer behavior, or another operator-facing path, FB-015 must add the exact `## User Test Summary` artifact and desktop export required by governance before Live Validation can advance.

## Later-Phase Expectations

- Workstream must execute bounded seams and keep the active seam recorded here.
- Workstream must start with WS-1 and must not begin runtime implementation, launcher implementation, shortcut changes, renderer lifecycle work, UI work, installer work, source movement, or release work unless a later seam explicitly admits the affected surfaces.
- Hardening must pressure-test the phase-boundary frame, lifecycle handoffs, ownership boundaries, diagnostics evidence roots, rollback boundaries, stale-helper caveats, implementation-admission contract, and User Test Summary triggers.
- Live Validation must classify shortcut applicability and User Test Summary applicability based on the completed FB-015 delta.
- PR Readiness must prove merge-target canon completeness, clean branch truth, successor selection, User Test Summary state, live PR state, and authenticated review-thread state before PR green.
- Release Readiness must validate the file-frozen `v1.6.4-prebeta` release package on updated `main` after the PR merges.

## Initial Workstream Seam Sequence

Seam 1: Current boot/desktop boundary inventory and ownership map

- Status: Completed.
- Goal: inventory current boot, launcher, renderer, desktop-settled, diagnostics, persisted-state, rollback, and user-facing entrypoint boundaries before implementation is considered.
- Scope: docs/canon source inventory, boundary vocabulary, current ownership map, evidence roots, ambiguity capture, validation trigger classification, rollback boundary, and implementation-admission checklist.
- Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no source tree reorganization, no release work, and no public release editing.

Seam 2: Lifecycle and phase-boundary state framing

- Status: Completed.
- Goal: define the lifecycle states and handoff boundaries between dev-only boot framing, production desktop launch control, renderer readiness, desktop-settled state, failure, recovery, and rollback.
- Scope: docs/canon lifecycle vocabulary, phase-boundary state framing, ownership handoff notes, ambiguity capture, and implementation-readiness risks.
- Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no source tree reorganization, no release work, and no public release editing.

Seam 3: Validation and admission contract for future boot/desktop boundary implementation

- Status: Completed.
- Goal: define the proof and admission contract required before future seams can change startup, launcher, renderer, shortcut, diagnostics, persisted-state, or user-facing boot/desktop surfaces.
- Scope: validation gates, shortcut/User Test Summary triggers, rollback proof, helper reuse posture, implementation-admission checklist, and later-phase evidence expectations.
- Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no source tree reorganization, no release work, and no public release editing.

## Active Seam

Active seam: none after PR-3 completion; the next legal phase is Release Readiness after merge.

- BR-1 Status: Completed in this pass.
- BR-1 Boundary: promote FB-015 and define the branch objective, target end-state, seam families, validation contract, User Test Summary strategy, later-phase expectations, and first Workstream seam.
- BR-1 Non-Includes: no runtime behavior, launcher behavior, shortcut behavior, renderer lifecycle behavior, UI implementation, installer work, source tree reorganization, release packaging, tag creation, or public release editing.
- WS-1 Status: Completed / executed.
- WS-1 Boundary: docs/canon current boot/desktop boundary inventory and ownership map only.
- WS-1 Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no source tree reorganization, no release work, and no public release editing.
- WS-2 Status: Completed / executed.
- WS-2 Boundary: docs/canon lifecycle and phase-boundary state framing only.
- WS-2 Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no source tree reorganization, no release work, and no public release editing.
- WS-3 Status: Completed / executed.
- WS-3 Boundary: docs/canon validation and admission contract for future boot/desktop boundary implementation only.
- WS-3 Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no source tree reorganization, no release work, and no public release editing.
- H-1 Status: Completed / executed.
- H-1 Boundary: docs/canon pressure test of the boot/desktop boundary inventory and ownership map, lifecycle and phase-boundary state framing, future implementation admission contract, governance gaps, validation gaps, ambiguity, contradiction, scope issues, and boundary-readiness risks.
- H-1 Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no helper-code repair, no source tree reorganization, no release work, and no public release editing.
- LV-1 Status: Completed / executed.
- LV-1 Boundary: docs/canon repo-truth alignment, branch-truth alignment, user-facing shortcut applicability classification, User Test Summary applicability classification, desktop export applicability classification, cleanup posture, and PR Readiness admission posture.
- LV-1 Non-Includes: no runtime validation, no shortcut launch, no manual User Test Summary handoff, no desktop export, no runtime code edits, no launcher behavior changes, no desktop shortcut behavior changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no helper-code repair, no release work, and no public release editing.
- PR-1 Status: Completed / executed.
- PR-1 Boundary: merge-target canon completeness, semantic release-target derivation for the post-merge FB-015 release-debt state, and merge-target package preparation for the docs/canon-only milestone.
- PR-1 Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut behavior changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no helper-code repair, no release publication, and no public release editing.
- PR-2 Status: Completed / executed.
- PR-2 Boundary: next-workstream selection, deferred-context validation, branch-containment validation, and successor branch-creation gate recording.
- PR-2 Non-Includes: no successor branch creation, no runtime code edits, no launcher behavior changes, no desktop shortcut behavior changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no helper-code repair, no release publication, and no public release editing.
- PR-3 Status: Completed / executed.
- PR-3 Boundary: live PR creation, authenticated PR state validation, authenticated review-thread validation, final PR-state canon sync, and clean pushed branch truth.
- PR-3 Non-Includes: no merge execution, no release publication, no runtime code edits, no launcher behavior changes, no desktop shortcut behavior changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no helper-code repair, and no public release editing.

## Seam Continuation Decision

Continue Decision: `stop`
Next Active Seam: `Release Readiness`
Stop Condition: `Merged-unreleased release debt active`
Continuation Action: repair any escaped post-merge canon drift on the next legal branch surface, then rerun file-frozen Release Readiness for `v1.6.4-prebeta` on updated `main`.

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

## WS-2 Execution Record

WS-2 is docs/canon only. It defines the lifecycle and phase-boundary state framing that future FB-015 seams must use when reasoning about current production desktop launch, the dev-only boot prototype, renderer readiness, desktop-settled state, failure/recovery handling, and shared relaunch primitives.

### Lifecycle Families

Production launcher-controlled desktop lifecycle:

1. `launch_orin_desktop.vbs` launches `desktop/orin_desktop_launcher.pyw` as the current user-facing production entry surface.
2. The launcher negotiates single-instance ownership, prepares runtime evidence roots, resets launcher-owned status and startup-abort artifacts, and opens the runtime control envelope.
3. The launcher starts a renderer attempt, spawns `desktop/orin_desktop_main.py`, passes the runtime-log and startup-abort paths, and begins startup observation.
4. The renderer creates the Qt application, resolves the visual HTML, constructs `DesktopRuntimeWindow`, initializes tray and hotkey services, and keeps window show deferred until core-visualization readiness is reached.
5. `DesktopRuntimeWindow` emits core-visualization-ready and first-visible signals; the renderer requests window show only after readiness, then emits `RENDERER_MAIN|CORE_VISUALIZATION_FIRST_VISIBLE`.
6. The renderer emits `RENDERER_MAIN|STARTUP_READY`, requests passive visual handoff to `state=dormant`, and continues running inside the desktop presentation boundary.
7. The launcher observes readiness, but it remains the owner of final runtime outcome, relaunch handling, startup abort, recovery sequencing, diagnostics finalization, crash classification, and finalized history.

Production launcher failure/recovery lifecycle:

1. If `RENDERER_MAIN|STARTUP_READY` is not observed inside the launcher observe window, the launcher records warning-state startup observation drift.
2. If readiness still does not arrive inside the stall-confirm window, the launcher records stall confirmation and may request cooperative startup abort through `renderer_startup_abort.signal`.
3. A cooperative startup-abort result may re-enter the bounded recovery loop, while repeated startup aborts, repeated identical crash outcomes, or exhausted attempts escalate to launcher-owned failure finalization.
4. Diagnostics UI launch, failure voice, crash evidence, incident summary, and finalized runtime history remain launcher-owned after the failure boundary is crossed.

Dev-only boot-transition lifecycle:

1. `main.py` starts with a selected boot profile and audio mode, resolves boot runtime log paths under `dev/logs/...`, and emits `BOOT_MAIN|START|...`.
2. The dev boot prototype validates monitor topology, constructs the boot windows plus a `DesktopRuntimeWindow`, and emits boot-window and topology markers.
3. The boot prototype runs the staged command/import flow, then emits `BOOT_MAIN|TRANSITION_BEGIN|import_home=...` when handoff begins.
4. The boot prototype requests desktop handoff, emits `BOOT_MAIN|HANDOFF_SIGNAL_EMITTED`, requests desktop show, hides boot windows, emits `BOOT_MAIN|DESKTOP_VISIBLE`, commits `state=dormant`, and then emits `BOOT_MAIN|DESKTOP_SETTLED|state=dormant`.
5. This lifecycle is a dev-only boot/handoff evidence path. It is not the current production desktop-launch authority and does not replace launcher-owned final runtime truth.

### Phase-Boundary State Vocabulary

Launch-initiation and boot-framing states:

- `launch requested`: the user or Windows shell invoked a boot or desktop entry surface.
- `boot prototype active`: dev-only `main.py` owns the current session framing before handoff begins.
- `boot transition pending`: dev-only boot framing is still gathering input, topology, or staged command decisions before handoff.
- `boot handoff emitted`: the dev-only boot prototype has requested desktop handoff but still owns proof of the boot-side transition.

Launcher-control states:

- `desktop control envelope active`: `desktop/orin_desktop_launcher.pyw` owns the production runtime attempt.
- `single-instance negotiation`: launcher-owned conflict handling and relaunch-request processing are in progress.
- `renderer startup pending`: the launcher has spawned the renderer and is waiting for readiness proof.
- `startup warning`: readiness has not arrived inside the initial observation window, but the renderer attempt is still live.
- `startup stall confirmed`: readiness has still not arrived inside the stall-confirm window and the launcher may request cooperative startup abort.
- `startup ready observed`: the launcher has observed renderer readiness proof and now owns runtime-attempt success classification beyond the renderer's own emission.
- `recovery active`: the launcher is inside a bounded recovery attempt or cooldown path.
- `failure finalization`: the launcher is writing diagnostics, crash, or finalized history truth after recovery has failed.
- `normal exit complete`: the renderer exited normally and the launcher cleaned status/signal artifacts.
- `failure flow complete`: the launcher wrote final incident/crash evidence and finalized failure history.

Renderer-presentation states:

- `renderer constructed`: the Qt application, visual path, and `DesktopRuntimeWindow` are constructed.
- `first-visible pending`: the renderer has not yet shown the desktop surface because core visualization is not ready.
- `desktop first visible`: the core visualization is visible and the renderer has crossed the first-visible boundary.
- `renderer ready`: `RENDERER_MAIN|STARTUP_READY` has been emitted.
- `passive dormant handoff`: the renderer has requested visual state `dormant` as the steady desktop presentation baseline.
- `shutdown requested`: the renderer is tearing down because of relaunch, startup-abort, or normal shutdown flow.

Desktop-settled and evidence states:

- `desktop settled`: a surface has reached the expected post-handoff dormant desktop state for its own lifecycle.
- `live runtime truth`: launcher-owned runtime logs, crash artifacts, status files, startup-abort files, and finalized history are authoritative for the production path.
- `dev transition proof`: `BOOT_MAIN|...` markers under `dev/logs/<lane>/...` are authoritative only for the dev boot prototype path.

### Ownership Handoff Rules

- Current production desktop authority begins at `desktop/orin_desktop_launcher.pyw`; there is no admitted production boot-phase owner ahead of it.
- `launch_orin_desktop.vbs` owns process launch handoff only. It does not own startup readiness, runtime success, recovery, or failure classification.
- Renderer first-visible proof is not the same as renderer-ready proof, renderer-ready proof is not the same as launcher-owned `startup ready observed`, and launcher-owned readiness observation is not the same as final runtime success.
- Dev-only `BOOT_MAIN|DESKTOP_SETTLED|state=dormant` is not equivalent to production `RENDERER_MAIN|STARTUP_READY` or launcher `STARTUP_READY_OBSERVED`.
- `state=dormant` is a presentation state, not a release, trust, shortcut, recovery, or success-state claim by itself.
- `Local\JarvisRuntimeSingletonV1` and `Local\JarvisRuntimeRelaunchRequestV1` are shared primitives. Shared primitive reuse does not collapse ownership between the launcher path and the dev-only boot prototype.
- Live runtime logs, crash reports, startup-abort/status files, and finalized history remain launcher-owned until a later admitted implementation seam explicitly changes that contract.

### Transition Ambiguities Captured For Later Seams

- `main.py` directly constructs `DesktopRuntimeWindow`, while the production path delegates through launcher to renderer. Future work must choose or preserve those models explicitly instead of blending them by implication.
- `DesktopRuntimeWindow` is shared by the production renderer and the dev-only boot prototype. Shared class reuse does not imply shared phase ownership.
- Current production truth has `RENDERER_MAIN|STARTUP_READY` and launcher observation markers, while the dev-only boot prototype has `BOOT_MAIN|DESKTOP_SETTLED|state=dormant`. Future validation must not substitute one proof family for the other without an admitted product-path change.
- Launcher-owned live evidence defaults to root `logs/`, while dev boot-transition proof belongs under `dev/logs/<lane>/...`. Future seams must preserve that evidence-root split unless they explicitly change ownership and rollback.
- `dev/orin_desktop_launcher_regression_harness.py` still contains stale legacy-path assumptions. Later launcher-regression claims must repair, replace, or explicitly bypass that harness with recorded rationale.

### WS-2 Completion Decision

- WS-2 Result: Complete / green.
- Validation Layer: docs/canon plus live repo marker and entrypoint inspection.
- User Test Summary Applicability: not applicable for WS-2 because this seam changes docs/canon only and adds no user-visible behavior.
- Cleanup: no programs, helper processes, windows, temporary files, probes, or runtime artifacts were created.
- Continue/Stop Decision: continue to WS-3 under `Next-Seam Continuation Required`; WS-3 remains inside the same approved Workstream, phase, branch class, and docs/canon validation surface.

### WS-2 Validation Results

- `python dev\orin_branch_governance_validation.py`: PASS, 963 checks.
- `git diff --check`: PASS with line-ending normalization warnings only and no whitespace errors.
- WS-2 continuation-state scan: PASS; current authority surfaces report WS-1 and WS-2 complete, WS-3 complete, and Hardening next.
- WS-2 scope validation: PASS; the seam changed docs/canon only in the FB-015 workstream record, backlog, roadmap, and workstream index.
- WS-2 changed no runtime behavior, launcher behavior, renderer behavior, desktop shortcut behavior, UI, installer behavior, helper code, release artifact, or desktop export.

## WS-3 Execution Record

WS-3 is docs/canon only. It defines the validation and admission contract required before any later FB-015 implementation seam may change boot, launcher, renderer, shortcut, diagnostics, persisted-state, or other boot/desktop boundary surfaces.

### Implementation Admission Checklist

Before any later FB-015 implementation seam may edit runtime or user-facing surfaces, it must record:

- affected surface class: launch shim, production desktop launcher, production renderer, `DesktopRuntimeWindow`, dev boot prototype, shared single-instance/relaunch primitive, desktop shortcut, diagnostics evidence root, persisted history/state, or validation helper
- ownership class: launch-initiation, launcher-control, renderer-presentation, dev-only boot framing, shared infrastructure primitive, live evidence/state root, or user-facing entry surface
- exact before/after phase-boundary states and the runtime markers expected to prove them
- exact rollback target and revert scope for the touched surface
- expected signal files, log roots, persisted files, cleanup behavior, and historical-state handling before and after the change
- helper reuse decision from `Docs/validation_helper_registry.md`
- desktop shortcut applicability, declared user-facing entrypoint class, and `User Test Summary` applicability
- explicit non-includes that stop adjacent launcher, renderer, tray, overlay, shortcut, installer, release, or source-tree work from entering by inertia

If an implementation seam cannot answer those items before edits begin, it is not admitted.

### Required Proof By Surface Class

Docs/canon-only seams:

- `python dev\orin_branch_governance_validation.py`
- `git diff --check`
- source-of-truth sweep confirming backlog, roadmap, workstream index, and this workstream record agree on phase, seam state, blockers, and next legal phase

Production desktop-launch or renderer-readiness seams:

- `dev/orin_desktop_entrypoint_validation.py` unless the seam records a stronger replacement
- runtime marker review for `RENDERER_MAIN|START`, `QAPPLICATION_CREATED`, `VISUAL_HTML_RESOLVED`, `WINDOW_CONSTRUCTED`, `WINDOW_SHOW_DEFERRED_UNTIL_CORE_READY`, `WINDOW_SHOW_REQUESTED|reason=core_visualization_ready`, `CORE_VISUALIZATION_FIRST_VISIBLE`, `STARTUP_READY`, and `PASSIVE_DEFAULT_HANDOFF_REQUESTED|state=dormant`
- no regression in tray identity, discovery cue, command-overlay routing, relaunch handling, or passive dormant handoff when those surfaces are affected

Launcher startup, recovery, diagnostics, or state-root seams:

- `dev/orin_desktop_launcher_healthy_validation.py` for healthy launcher-to-renderer startup proof
- failure/recovery coverage only through a current, repaired, or explicitly admitted harness path
- runtime marker review for single-instance negotiation, renderer spawn, startup observation, startup-abort request/observation, normal exit, failure flow, signal/status cleanup, and crash-history behavior
- crash report and finalized-history evidence review when failure classification, diagnostics, or persisted-state behavior is affected

Boot-transition or dev boot-prototype seams:

- `dev/orin_boot_monitor_preflight.py` when monitor topology assumptions matter
- `dev/orin_boot_transition_verification.py` for marker-order proof
- `dev/orin_boot_transition_capture.py` when visual handoff evidence is materially required
- explicit proof that dev-only `BOOT_MAIN|...` markers do not replace production launcher/renderer readiness proof unless the seam admits that product-path change

Shared single-instance or relaunch-primitive seams:

- proof across both the production launcher path and the dev-only boot prototype path that mutex, relaunch-signal, and replace-session semantics remain consistent
- proof that relaunch dialogs, relaunch-request cleanup, and shutdown initiation leave no stale live artifacts behind

Desktop shortcut, visible startup, or other operator-facing seams:

- launch through the declared user-facing desktop shortcut or equivalent production entrypoint during Live Validation
- record whether the declared user-facing entrypoint is a Windows shortcut, another equivalent production entrypoint, or the repository launch shim used only as supporting proof
- direct invocation of `launch_orin_desktop.vbs` is supporting evidence by default and does not count as real user-facing desktop-shortcut proof unless the seam explicitly records why that path is the true operator-facing entry surface
- record `User-Facing Shortcut Path:` and `User-Facing Shortcut Validation:` in this workstream record before User Test Summary handoff
- add and export the canonical User Test Summary when the completed delta changes user-visible startup, shortcut behavior, visible runtime behavior, prompts, tray/overlay behavior, voice behavior, or another operator-facing path

### Helper Reuse And Repair Contract

- Reuse-first selection from `Docs/validation_helper_registry.md` is mandatory before any new helper is created.
- Later seams should extend the current boot/desktop proof families first: `dev/orin_desktop_entrypoint_validation.py`, `dev/orin_desktop_launcher_healthy_validation.py`, `dev/orin_boot_transition_verification.py`, and `dev/orin_boot_transition_capture.py`.
- New durable root `dev/` helpers must follow the registry naming pattern and be registered immediately.
- Workstream-scoped helpers require owner, non-reuse reason, consolidation target, and promotion decision point before PR Readiness.
- Temporary probes must stay under ignored evidence roots and must be deleted or promoted before closeout-grade proof.
- `dev/orin_desktop_launcher_regression_harness.py` currently points at stale legacy launcher paths. It must be repaired, replaced by a current registered helper, or explicitly bypassed with documented rationale before launcher regression coverage can be claimed.

### User Test Summary Admission Rules

- WS-1 through WS-3 are docs/canon only and do not require User Test Summary handoff.
- A later implementation seam that changes startup behavior, launcher behavior, desktop shortcut behavior, visible startup state, desktop UI behavior, tray behavior, overlay behavior, prompts, voice behavior, installer/OS integration, or another operator-facing path must add the exact `## User Test Summary` section before Live Validation.
- If User Test Summary is required, the desktop export at `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt` must also be refreshed unless an explicit documented exception applies.
- If a later completed delta remains non-user-facing, Live Validation may waive User Test Summary only with a recorded waiver reason.

### Rollback And Cleanup Contract

Any later implementation seam must prove rollback and cleanup at the same surface it changed:

- launch-shim changes must roll back to the current `launch_orin_desktop.vbs` semantics that target `desktop/orin_desktop_launcher.pyw` with no new authority above it
- launcher changes must roll back to the current single-instance, startup-observation, startup-abort, recovery, diagnostics, runtime-log, and finalized-history model
- renderer changes must roll back to deferred-first-visible startup, tray/hotkey initialization, `STARTUP_READY`, passive dormant handoff, and clean event-loop shutdown behavior
- dev boot-prototype changes must roll back to the current dev-only `main.py` handoff path and must not silently become production-launch truth
- evidence/state changes must roll back the current split between live root `logs/` truth and dev `dev/logs/<lane>/...` proof, plus cleanup of status/abort artifacts and preserved history files
- helper changes must leave no unregistered durable helper, stale temporary probe, or unexplained cleanup residue behind

### WS-3 Completion Decision

- WS-3 Result: Complete / green.
- Validation Layer: docs/canon plus live repo entrypoint and helper-surface inspection.
- User Test Summary Applicability: not applicable for WS-3 because this seam changes docs/canon only and adds no user-visible behavior.
- Cleanup: no programs, helper processes, windows, temporary files, probes, or runtime artifacts were created.
- Continue/Stop Decision: stop at the Workstream phase boundary because the approved WS-1 through WS-3 docs/canon seam chain is complete. The next legal phase is `Hardening`.

### WS-3 Validation Results

- `python dev\orin_branch_governance_validation.py`: PASS, 963 checks.
- `git diff --check`: PASS with line-ending normalization warnings only and no whitespace errors.
- WS-3 phase-boundary scan: PASS; current authority surfaces report FB-015 Workstream complete and Hardening as the next legal phase.
- WS-3 scope validation: PASS; the seam changed docs/canon only in the FB-015 workstream record, backlog, roadmap, and workstream index.
- WS-3 changed no runtime behavior, launcher behavior, renderer behavior, desktop shortcut behavior, UI, installer behavior, helper code, release artifact, or desktop export.

## H-1 Hardening Record

H-1 is docs/canon only. It pressure-tests whether the WS-1 through WS-3 boot/desktop boundary frame is coherent enough to move into Live Validation without admitting runtime, launcher, shortcut, renderer, or helper implementation.

### Hardening Findings

- Governance Gap: the active workstream record still carried Workstream-complete / Hardening-next phase truth after the bounded WS-1 through WS-3 seam chain had already finished. H-1 corrects current-state canon to Hardening-complete / Live-Validation-next truth.
- Ownership/State Framing Gap: WS-2 recorded renderer-ready and launcher failure handling, but it did not yet name launcher-owned `startup ready observed` as a separate boundary between renderer readiness emission and launcher outcome classification. H-1 records that boundary and the launcher terminal states `normal exit complete` and `failure flow complete` so later seams do not collapse renderer proof, launcher observation, and finalized outcome into one claim.
- Validation/Shortcut Gap: WS-3 required shortcut applicability classification, but it left too much room to blur a real desktop shortcut with direct repository launch-shim invocation. H-1 tightens the admission contract so future seams must classify whether proof comes from a Windows shortcut, another equivalent production entrypoint, or a repository-local shim used only as supporting evidence.
- Source-Of-Truth Pressure Test: `Docs/architecture.md`, `Docs/orchestration.md`, the current launcher/runtime entrypoints, and `Docs/validation_helper_registry.md` agree that production desktop authority begins at `desktop/orin_desktop_launcher.pyw`, live evidence stays launcher-owned under the runtime root, and `dev/orin_desktop_launcher_regression_harness.py` remains repair-gated. No source-of-truth contradiction blocks Live Validation.
- Scope Check: WS-1 through WS-3 and H-1 changed docs/canon only. No runtime behavior, launcher behavior, desktop shortcut behavior, renderer behavior, UI, installer behavior, source layout, helper code, release artifact, or desktop export changed.
- Boundary-Readiness Risk: FB-015 is ready for repo-truth and applicability validation, but it is not ready for implementation by inertia. Any later runtime or operator-facing seam still requires explicit affected surface class, boundary states, proof markers, rollback target, helper reuse decision, user-facing entrypoint classification, and User Test Summary applicability.

### Hardening Corrections

- Current-state canon is updated from Workstream-complete / Hardening-next wording to Hardening-complete / Live-Validation-next wording.
- WS-2 lifecycle framing now explicitly separates renderer-ready, launcher-owned `startup ready observed`, `normal exit complete`, and `failure flow complete`.
- WS-3 admission contract now requires explicit user-facing entrypoint classification and prevents direct repository launch-shim invocation from counting as desktop-shortcut proof by default.
- No new helper, validator, runtime artifact, desktop artifact, release artifact, or User Test Summary export was created.

### H-1 Completion Decision

- H-1 Result: Complete / green.
- User-facing impact: none. This pass changed docs/canon only.
- Next legal phase: Live Validation.
- Stop condition: phase boundary reached; Hardening is complete after H-1.

### H-1 Validation Results

- `python dev\orin_branch_governance_validation.py`: PASS, 958 checks.
- `git diff --check`: PASS with line-ending normalization warnings only and no whitespace errors.
- H-1 phase-state scan: PASS; current authority surfaces report FB-015 Hardening complete and Live Validation as the next legal phase.
- H-1 scope validation: PASS; changed files are docs/canon surfaces only.
- H-1 changed no runtime behavior, launcher behavior, renderer behavior, desktop shortcut behavior, UI, installer behavior, helper code, release artifact, or desktop export.

## Live Validation Record

LV-1 validated the completed FB-015 docs/canon-only milestone against live repo truth, branch truth, and user-facing/manual validation applicability. The branch remains docs/canon-only for this milestone: no runtime boot/desktop boundary implementation, launcher behavior change, renderer lifecycle change, desktop shortcut change, visible startup change, UI surface, tray/overlay path, installer path, source layout change, helper code, release artifact, or operator-facing invocation behavior has been added.

### Live Validation Findings

- Repo Truth Alignment: FB-015 remains `Promoted`, active on `feature/fb-015-boot-desktop-phase-boundary-model`, and FB-004 remains released/closed in `v1.6.3-prebeta` with release debt clear.
- Branch Truth Alignment: the checked-out branch is the canonical FB-015 branch and carries completed Branch Readiness, WS-1 through WS-3, and H-1 records at the durable hardening baseline.
- User-Facing Shortcut Applicability: waived for this milestone because the completed FB-015 delta is docs/canon only and does not add or change the user-facing desktop shortcut, equivalent production entrypoint behavior, launcher behavior, renderer behavior, visible startup state, UI behavior, installer behavior, or another operator-facing path. Exercising the existing shortcut would not validate the FB-015 delta.
- Manual Validation Applicability: waived for this milestone because the deliverable is boundary inventory, ownership mapping, lifecycle/state framing, implementation-admission governance, hardening correction, and repo-truth validation only; a filled manual User Test Summary would not materially validate behavior that did not change.
- Runtime Evidence Applicability: no runtime/helper evidence is required or meaningful for this milestone because no runtime product surface, helper, harness, launcher behavior, renderer behavior, shortcut behavior, installer behavior, or user-facing artifact was created.
- Desktop Export Applicability: no desktop `User Test Summary.txt` export is required for this Live Validation pass because there is no user-facing desktop path or manual checklist to hand off.
- Cleanup: no programs, helper processes, windows, temporary files, probes, assets, screenshots, helpers, harnesses, runtime artifacts, desktop exports, release artifacts, or session-scoped evidence files were created.

### Live Validation Completion Decision

- LV-1 Result: Complete / green with repo-truth alignment and applicability waivers recorded.
- User-facing shortcut gate: waived with exact markers in `## User Test Summary`.
- User Test Summary results gate: waived with exact markers in `## User Test Summary`.
- Validation Layer: documentation, branch truth, targeted repo-truth scan, and governance validation only.
- Continue/Stop Decision: stop at the Live Validation phase boundary after validation because FB-015 Live Validation proof is green and the next normal phase is `PR Readiness`; PR Readiness must still prove merge-target canon, clean branch truth, successor selection, PR package creation, and live PR validation before reporting PR-ready.

### LV-1 Validation Results

- `python dev\orin_branch_governance_validation.py`: PASS, 968 checks.
- `git diff --check`: PASS with line-ending normalization warnings only and no whitespace errors.
- LV-1 phase-state scan: PASS; current authority surfaces report FB-015 Live Validation complete and PR Readiness as the next legal phase.
- LV-1 user-facing shortcut gate: WAIVED with exact markers in `## User Test Summary`.
- LV-1 User Test Summary results gate: WAIVED with exact markers in `## User Test Summary`; no desktop export was required.
- LV-1 scope validation: PASS; changed files are docs/canon surfaces only.
- LV-1 changed no runtime behavior, launcher behavior, renderer behavior, desktop shortcut behavior, UI, installer behavior, helper code, release artifact, or desktop export.

## Supporting Canon Sync

This branch carried tightly scoped supporting canon sync earlier in Workstream when the change stayed docs/governance-only, preserved FB-015 as the active workstream, and did not widen into runtime or branch-selection churn.

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
- no change to the admitted FB-015 seam chain or later Hardening admission posture

## Governance Drift Audit

Governance Drift Found: Yes, resolved before PR green.

- Successor-selection drift was found at PR Readiness entry: every remaining open backlog candidate was deferred, and FB-029's prior wording could be read as prohibiting even planning-only selected-next recording. PR-2 resolves this by clarifying that FB-029 may be selected as the next planning lane during PR Readiness while branch creation and Branch Readiness admission remain explicitly product/legal-gated.
- Current-state canon drift was found across backlog, roadmap, workstream index, and this workstream doc because they still reported LV-1 complete / PR Readiness next after PR-1 and PR-2 had already been executed locally. PR-2 reconciles all active authority surfaces to the same PR Readiness package-ready truth.
- Escaped post-merge canon drift was found after PR #75 merged: backlog, roadmap, workstream index, and this workstream doc still claimed active PR Readiness truth, open PR state, clear release debt, and no merged-unreleased owner.
- Root cause: the normal validator only enforced merged-unreleased release-debt rules after status had already flipped to `Merged unreleased`, so stale active implementation workstream truth on `main` for a non-`main` canonical branch could pass unchecked.
- Repair: FB-029 Branch Readiness carried the first blocker-clearing seam, moved FB-015 to merged-unreleased release-debt truth for `v1.6.4-prebeta`, cleared stale PR-open and active-workstream claims, and then advanced FB-029 into promoted Branch-Readiness-complete truth with WS-1 admitted next.
- Permanent validator fix: the normal governance validator now fails if `main` still carries active implementation workstream truth for a promoted workstream whose canonical branch is not `main`.
- No unresolved contradiction remains across backlog priority, deferred-context fields, successor lock, semantic release-target derivation, merged-unreleased release-debt framing, or FB-015 docs/canon-only validation posture.

## Merged-Unreleased Release-Debt State

Merged-Unreleased Release-Debt Owner: FB-015 Boot and desktop phase-boundary model
Repo State: No Active Branch
Latest Public Prerelease: v1.6.3-prebeta
Release Debt: Active
Release Target: v1.6.4-prebeta
Release Title: Pre-Beta v1.6.4
Release Floor: patch prerelease
Version Rationale: FB-015 remains a docs/canon-only boot and desktop phase-boundary architecture plus admission milestone with no new executable, runtime, operator-facing, user-facing, or materially expanded product capability
Release Scope: FB-015 boot and desktop phase-boundary inventory, ownership map, lifecycle and state framing, implementation admission contract, hardening corrections, Live Validation waivers, PR Readiness package history, post-merge canon repair, and merged-unreleased release-debt framing, plus the FB-029 identity source-of-truth inventory, persona-option boundary framing, licensing boundary framing, implementation admission contract, hardening corrections, Live Validation waivers, and PR Readiness package history
Release Artifacts: Tag v1.6.4-prebeta; release title Pre-Beta v1.6.4; rich Markdown release notes summarize the FB-015 boundary model and the FB-029 identity/licensing planning frame without repeating the release title inside the notes body, and GitHub-generated `## What's Changed` plus `**Full Changelog**:` must be included
Post-Release Truth: FB-015 and FB-029 are Released / Closed in v1.6.4-prebeta after publication and validation; release debt then clears, and FB-030 Branch Readiness may begin only after updated-main revalidation and an explicit voice/audio design goal with affected-surface map admits promotion. Temporary `emergency canon repair` branches do not satisfy or consume the selected-next implementation-branch gate
Selected Next Workstream: FB-030 ORIN voice/audio direction refinement
Next-Branch Creation Gate: FB-030 remains selected-only, and its selected-next implementation branch must remain not created until `v1.6.4-prebeta` is published and validated and an explicit voice/audio design goal with affected-surface map admits promotion. Temporary `emergency canon repair` branches may exist only to clear release-readiness blockers and do not count as selected-next implementation-branch creation

## Post-Merge State

- PR #75 merged cleanly into `main` at `3e821e07ff91d814fd7aba9b50819f97d700a301`, and FB-015 is now the merged-unreleased release-debt owner for `v1.6.4-prebeta`.
- After merge, repo state is `No Active Branch` until `v1.6.4-prebeta` is published, validated, and post-release canon closure is completed on the next legal branch surface.
- FB-029 is merged-unreleased inside the inherited `v1.6.4-prebeta` package after PR #76 merged into `main`, and FB-030 remains selected-only while release debt plus its explicit voice/audio design-goal and affected-surface-map blockers still control any later Branch Readiness admission.

## PR Readiness Record

PR Readiness validates the completed docs/canon-only FB-015 milestone for merge to `main`. This record prepares the post-merge release-debt path, successor-selection state, durable PR package, and live PR validation gate.

### PR-1 Merge-Target Canon Findings

- Merge Target: `main`.
- Head Branch: `feature/fb-015-boot-desktop-phase-boundary-model`.
- Source-of-Truth Alignment: PASS. `Docs/Main.md`, `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, `Docs/workstreams/index.md`, and this workstream record point to FB-015 as the active promoted PR Readiness authority.
- Release Debt Framing: PASS. Before merge, release debt is clear after `v1.6.3-prebeta`; after merge, FB-015 becomes the merged-unreleased release-debt owner for `v1.6.4-prebeta`.
- Release Target: `v1.6.4-prebeta`.
- Release Title: `Pre-Beta v1.6.4`.
- Release Floor: `patch prerelease`.
- Version Rationale: `patch prerelease` is required because FB-015 remains a docs/canon-only phase-boundary architecture and admission milestone with no new executable, runtime, operator-facing, or materially expanded product capability.
- Release Scope: docs/canon-only boot/desktop boundary inventory, ownership map, lifecycle/state framing, implementation admission contract, hardening corrections, Live Validation waivers, selected-next governance sync, and PR Readiness merge-target canon.
- Release Artifacts: Tag `v1.6.4-prebeta`; release title `Pre-Beta v1.6.4`; rich Markdown release notes summarize the boot/desktop phase-boundary model, ownership map, lifecycle/state framing, implementation admission contract, hardening corrections, waiver posture, selected-next FB-029 branch gate, GitHub-generated `## What's Changed`, and the generated `**Full Changelog**:` compare link.
- Post-Release Truth: FB-015 is Released / Closed after `v1.6.4-prebeta` is published and validated; release debt clears only after post-release canon closure, and FB-029 Workstream may continue after updated `main` is revalidated while this milestone stays docs/canon-only and explicit product/legal approval remains required before implementation-facing work.

### PR-2 Selected-Next Workstream Findings

- Selected Next Workstream: FB-029 ORIN legal-safe rebrand, future ARIA persona option, and repo licensing hardening.
- Selected Next Basis: FB-029 is the highest-priority remaining open backlog candidate after FB-015, and PR-2 records it as the next planning lane while preserving the explicit product/legal gate on branch creation and Branch Readiness admission.
- Selected Next Record State At PR Package Time: `Registry-only`.
- Selected Next Implementation Branch At PR Package Time: Not created.
- Branch Creation Gate At PR Package Time: FB-029 branch creation remained blocked until FB-015 merged, `v1.6.4-prebeta` was published and validated, updated `main` was revalidated, and explicit product/legal approval admitted FB-029 Branch Readiness.
- Branch Containment At PR Package Time: PASS. No local or remote branch existed for FB-029 when PR #75 was packaged.

### PR-3 PR Package Details

- PR Title: `FB-015 Boot And Desktop Phase-Boundary Model`
- Base Branch: `main`
- Head Branch: `feature/fb-015-boot-desktop-phase-boundary-model`
- PR Summary: Promote the docs/canon-only FB-015 boot/desktop phase-boundary model, including the current boundary inventory, ownership map, lifecycle/state framing, implementation admission contract, hardening corrections, Live Validation waivers, selected-next FB-029 branch gate, and post-merge `v1.6.4-prebeta` release-debt path.
- PR URL: https://github.com/GiribaldiTTV/Nexus-Desktop-AI/pull/75
- PR State: MERGED, base `main`, head `feature/fb-015-boot-desktop-phase-boundary-model`, merge commit `3e821e07ff91d814fd7aba9b50819f97d700a301`.
- Review Thread State: PASS. Authenticated PR validation found no unresolved blocking Codex review-thread state before merge, and no blocking review state remained at merge time.
- Merge Readiness: PASS. GitHub reported `MERGEABLE` with merge state `CLEAN`, and the PR then merged successfully.

### PR Readiness Completion Decision

- PR-1 Result: Complete / green.
- PR-2 Result: Complete / green.
- PR-3 Result: Complete / green.
- User-facing impact: none. FB-015 remains docs/canon-only.
- Next legal action after merge: execute file-frozen Release Readiness for `v1.6.4-prebeta` on updated `main`; if escaped post-merge canon drift is discovered after merge, repair it on the next active branch's Branch Readiness surface before release packaging proceeds.

### PR Readiness Validation Results

- `python dev\orin_branch_governance_validation.py`: PASS before live PR creation and again after PR-state canon sync.
- `git diff --check`: PASS before live PR creation with line-ending normalization warnings only and no whitespace errors.
- User-facing shortcut gate: WAIVED with exact markers in `## User Test Summary`.
- User Test Summary results gate: WAIVED with exact markers in `## User Test Summary`.
- Successor branch containment at PR package time: PASS; no FB-029 branch existed and successor branch creation remained prohibited during FB-015 PR Readiness.
- Scope validation: PASS; PR Readiness changed docs/canon surfaces only.

## Reuse Baseline

- `Docs/workstreams/FB-004_future_boot_orchestrator_layer.md`
- `Docs/workstreams/FB-025_boot_desktop_milestone_taxonomy_clarification.md`
- `Docs/feature_backlog.md`
- `Docs/prebeta_roadmap.md`
- `Docs/workstreams/index.md`
- `Docs/architecture.md`
- `Docs/orchestration.md`
- `Docs/phase_governance.md`
- `Docs/validation_helper_registry.md`
- `dev/orin_branch_governance_validation.py`
- `main.py`
- `desktop/orin_desktop_launcher.pyw`
- `desktop/orin_desktop_main.py`
- `desktop/desktop_renderer.py`
- `desktop/single_instance.py`
- `dev/orin_boot_transition_capture.py`
- `dev/orin_boot_transition_verification.py`
- `dev/orin_desktop_entrypoint_validation.py`
- `dev/orin_desktop_launcher_healthy_validation.py`

## Exit Criteria

- WS-1 current boot and desktop phase boundaries are recorded.
- WS-2 lifecycle families, phase-boundary states, and ownership handoff rules for production desktop launch, launcher failure/recovery, and the dev-only boot prototype are recorded.
- WS-3 validation and admission rules for future boot/desktop boundary implementation are recorded.
- H-1 pressure test findings and corrections are recorded.
- LV-1 repo-truth alignment, user-facing shortcut applicability, User Test Summary applicability, desktop export applicability, cleanup posture, and waiver handling are recorded.
- PR-1 merge-target canon completeness is recorded.
- PR-2 selected-next workstream truth is recorded with FB-029 selected-next and preserved as historical pre-branch package state.
- PR-3 live PR creation and validation is recorded, and PR #75 merge completion is preserved as historical evidence.
- The ownership map across the current user-facing launch shim, production launcher, production renderer, dev-only boot prototype, shared single-instance primitives, and evidence/state roots is recorded.
- `## User Test Summary` records `User-Facing Shortcut Validation: WAIVED`, `User-Facing Shortcut Waiver Reason:`, `User Test Summary Results: WAIVED`, and `User Test Summary Waiver Reason:` for the docs/canon-only milestone.
- `Docs/Main.md`, `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, and `Docs/workstreams/index.md` route FB-015 as the merged-unreleased release-debt owner with `Repo State: No Active Branch`, `Release Target: v1.6.4-prebeta`, and no stale active-workstream truth.
- Backlog, roadmap, and workstreams index route FB-029 as promoted and merged-unreleased inside the inherited `v1.6.4-prebeta` package, with no stale active implementation truth remaining after PR #76 merged.
- FB-004 remains Released / Closed, and the latest public prerelease remains `v1.6.3-prebeta`.
- Requested future-lane `FB-042 Stream Deck Integration via Elgato MCP` admission remains deferred and no out-of-scope backlog, roadmap, workstream, or auxiliary planning-reference canon was added on this branch.
- No runtime, launcher, shortcut, renderer lifecycle, UI, installer, source-tree, release, helper-code, or desktop-export surface changed during WS-1 through WS-3, H-1, or LV-1.
- Validation is green.

## Rollback Target

- `Live Validation`
- Revert the FB-015 PR Readiness docs/canon commit(s) and return FB-015 to the Live-Validation-complete / PR-Readiness-next state with WS-1 through WS-3, H-1, and LV-1 recorded and no PR package or selected-next canon applied.

## Next Legal Phase

- `Release Readiness`

## User Test Summary

- User-Facing Shortcut Path: Not applicable - FB-015 Live Validation is docs/canon only and does not change any user-facing desktop shortcut, equivalent production entrypoint behavior, launcher behavior, or visible startup path.
- User-Facing Shortcut Validation: WAIVED
- User-Facing Shortcut Waiver Reason: FB-015 LV-1 validates docs/canon only. The completed milestone changes no user-facing desktop shortcut behavior, equivalent production entrypoint behavior, launcher behavior, renderer behavior, visible startup state, UI behavior, installer behavior, or other operator-facing invocation path, so exercising the existing shortcut would not validate the FB-015 delta.
- User Test Summary Results: WAIVED
- User Test Summary Waiver Reason: The milestone remains docs/canon-only and validator-proven through repo/canon checks; a filled manual User Test Summary would not materially validate behavior because no user-visible setup, display, runtime, shortcut, launcher, renderer, installer, or invocation surface changed.
