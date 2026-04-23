# FB-004 Future Boot Orchestrator Layer

## Identity

- ID: `FB-004`
- Title: `Future boot orchestrator layer`

## Record State

- `Promoted`

## Status

- `Active`

## Release Stage

- `Slice-staged`

## Canonical Branch

- `feature/fb-004-future-boot-orchestrator-layer`

## Current Phase

- Phase: `Workstream`

## Phase Status

- `WS-1 complete / WS-2 admitted next`
- FB-032 is released and closed in `v1.6.2-prebeta`.
- Latest public prerelease truth is `v1.6.2-prebeta`.
- Release debt is clear.
- FB-004 is promoted and active in this canonical workstream record.
- Branch Readiness is complete.
- WS-1 current boot-to-desktop source map and ownership boundary is complete.
- WS-2 lifecycle and orchestration-state framing for boot and desktop transitions is admitted next.
- No FB-004 implementation, runtime behavior, launcher behavior, desktop shortcut behavior, UI change, installer change, release work, or tag work has started.

## Branch Class

- `implementation`

## Blockers

None.

## Entry Basis

- `main` reached the public `v1.6.2-prebeta` release at `e282072769ec25694928293ce51e144d6a37f611`.
- FB-032 post-release canon closure is complete.
- Release debt is clear.
- FB-004 was selected as the next lane by priority-led backlog selection after FB-032 closure.
- The canonical FB-004 branch is `feature/fb-004-future-boot-orchestrator-layer`.
- Branch Readiness is the first legal FB-004 surface and exists to admit the lane before any Workstream implementation begins.

## Branch Objective

- Define the smallest implementation-facing future boot orchestrator slice above the current desktop launcher.
- Establish boot-to-desktop ownership, lifecycle boundaries, validation proof paths, rollback boundaries, and non-goals before any runtime delivery starts.
- Keep launcher behavior, desktop shortcut behavior, startup diagnostics, renderer lifecycle, and future orchestrator responsibilities separated enough that later implementation seams can be admitted deliberately.
- Prevent a broad boot rewrite, service/autostart layer, UI implementation, installer change, or release task from entering by inertia.

## Target End-State

- FB-004 has a canonical boot-orchestrator planning frame that names the current boot-to-desktop surfaces and the future orchestrator boundary.
- Workstream execution can begin with a source-map and ownership seam instead of implementation.
- The branch has a validation contract that distinguishes docs/canon proof from later runtime, shortcut, launcher, or user-facing proof.
- Later implementation is blocked until a seam explicitly admits the affected runtime surfaces, rollback path, and user-facing validation requirements.

## Scope

- Define current boot-to-desktop ownership boundaries.
- Define the future orchestrator responsibility frame above the existing launcher and renderer startup path.
- Define validation and evidence expectations for planning-only, diagnostics-only, and runtime-affecting seams.
- Define what later Workstream seams may inspect or classify before any implementation.
- Preserve existing launcher, shortcut, desktop session, and release behavior during Branch Readiness.

## Non-Goals

- No runtime behavior changes.
- No launcher behavior changes.
- No desktop shortcut changes.
- No renderer lifecycle implementation.
- No service, autostart, installer, packaging, or OS integration changes.
- No UI implementation.
- No source tree reorganization.
- No release packaging, tag creation, or public release editing during Branch Readiness.

## Expected Seam Families And Risk Classes

- Current boot-to-desktop source map and ownership family; risk class: architecture/runtime-boundary, because future implementation can destabilize startup if ownership is guessed.
- Boot lifecycle and orchestration contract family; risk class: lifecycle/launcher, because launcher, renderer, diagnostics, readiness, and rollback responsibilities must not collapse into one ambiguous owner.
- Failure, diagnostics, and evidence boundary family; risk class: validation/observability, because startup failures need durable proof without broadening logging or changing runtime behavior by accident.
- Runtime admission and rollback contract family; risk class: implementation/governance, because later code seams must prove exact affected surfaces, rollback path, and validation gates before edits.
- User-facing startup path classification family; risk class: desktop/user-facing, because shortcut launch, visible startup, and User Test Summary handling become mandatory only when the completed delta affects those surfaces.

## Validation Contract

- Run `python dev\orin_branch_governance_validation.py`.
- Run `git diff --check`.
- Confirm `Docs/Main.md` routes this promoted FB-004 workstream record.
- Confirm `Docs/feature_backlog.md` marks FB-004 as `Promoted`, `Active`, and cites this canonical workstream doc.
- Confirm `Docs/workstreams/index.md` lists FB-004 under Active and not under Closed or Merged / Release Debt Owners.
- Confirm `Docs/prebeta_roadmap.md` records FB-004 as the active Branch Readiness workstream and does not leave selected-only or registry-only truth behind.
- Confirm this Branch Readiness pass changes only docs/canon surfaces.
- Confirm no runtime, launcher, shortcut, UI, installer, release, or desktop export artifact changed during Branch Readiness.

## Branch Readiness Validation Results

- `python dev\orin_branch_governance_validation.py`: PASS, 921 checks.
- `git diff --check`: PASS; no whitespace errors.
- Scope validation: PASS; Branch Readiness changed docs/canon routing and the new FB-004 workstream record only.
- Admission validation: PASS; FB-004 was promoted and WS-1 current boot-to-desktop source map and ownership boundary was admitted next.

## User Test Summary Strategy

- Branch Readiness is docs/canon planning only and does not change user-facing behavior.
- No desktop shortcut validation, desktop export, or manual User Test Summary handoff is required during Branch Readiness.
- If a later Workstream seam remains docs/canon-only, Live Validation may waive the exact `## User Test Summary` artifact with a recorded reason.
- If a later seam changes runtime startup, launcher behavior, desktop shortcut behavior, visible startup state, user-facing copy, UI, installer behavior, or another operator-facing path, FB-004 must add the exact `## User Test Summary` artifact and desktop export required by governance before Live Validation can advance.
- User-facing shortcut validation becomes applicable for any completed delta that must be exercised through the real desktop shortcut or user-visible boot path.

## Later-Phase Expectations

- Workstream must execute bounded seams and keep the active seam recorded here.
- Workstream must start with WS-1 and must not begin runtime implementation, launcher implementation, shortcut changes, UI work, installer work, service/autostart work, release work, or broad source movement unless a later seam explicitly admits it.
- Hardening must pressure-test the boot-to-desktop architecture frame, lifecycle ownership, validation gates, rollback boundary, startup-failure evidence, user-facing shortcut trigger, and implementation-readiness risks.
- Live Validation must classify user-facing shortcut applicability and User Test Summary applicability based on the completed FB-004 delta.
- PR Readiness must prove merge-target canon completeness, clean branch truth, successor selection, User Test Summary state, and live PR state before PR green.
- Release Readiness remains file-frozen and may only validate release package truth if FB-004 becomes release-bearing after merge.

## Initial Workstream Seam Sequence

Seam 1: Current boot-to-desktop source map and ownership boundary

- Status: Completed.
- Goal: inventory the current boot-to-desktop entrypoints, launcher and renderer startup ownership, diagnostics evidence roots, and rollback boundaries before any orchestrator implementation is considered.
- Scope: docs/canon source map, ownership vocabulary, current entrypoint inventory, lifecycle boundary notes, validation trigger classification, rollback boundary, and implementation admission checklist for later seams.
- Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no source tree reorganization, no release work, and no public release editing.

Seam 2: Lifecycle and orchestration-state framing for boot and desktop transitions

- Status: Admitted next.
- Goal: define the lifecycle states and transition ownership between future boot framing, current desktop launcher authority, renderer readiness, failure/recovery states, and desktop-settled outcomes.
- Scope: docs/canon lifecycle vocabulary, state-transition framing, ownership handoff boundaries, ambiguity capture, and implementation-readiness risks.
- Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no release work, and no public release editing.

Seam 3: Validation and admission contract for orchestrator implementation seams

- Status: Pending after WS-2.
- Goal: define the proof and admission contract required before any future boot orchestrator implementation can change launcher, renderer, shortcut, startup, diagnostics, or user-facing surfaces.
- Scope: validation gates, shortcut/User Test Summary triggers, rollback proof, helper reuse requirements, implementation admission checklist, and later-phase evidence expectations.
- Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no release work, and no public release editing.

## Active Seam

Active seam: WS-1 current boot-to-desktop source map and ownership boundary is complete; WS-2 lifecycle and orchestration-state framing for boot and desktop transitions is admitted next.

- BR-1 Status: Completed in this pass.
- BR-1 Boundary: promote FB-004, define branch objective, target end-state, seam families, validation contract, User Test Summary strategy, later-phase expectations, and the first Workstream seam.
- BR-1 Non-Includes: no runtime behavior, launcher behavior, desktop shortcut behavior, UI implementation, service/autostart work, installer work, source tree reorganization, release packaging, tag creation, or public release editing.
- WS-1 Status: Completed / executed.
- WS-1 Boundary: docs/canon source map and ownership boundary only.
- WS-1 Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no source tree reorganization, no release work, and no public release editing.
- WS-2 Status: Admitted next.
- WS-2 Boundary: docs/canon lifecycle and orchestration-state framing only.
- WS-2 Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no release work, and no public release editing.

## Seam Continuation Decision

Continue Decision: `continue`
Next Active Seam: `WS-2 lifecycle and orchestration-state framing for boot and desktop transitions`
Stop Condition: `none`
Continuation Action: WS-1 is complete after validation; continue to WS-2 on the same branch because the approved seam chain remains inside Workstream scope.

## WS-1 Execution Record

WS-1 is docs/canon only. It inventories the current boot-to-desktop source map and records the ownership, evidence, and rollback boundaries that later FB-004 seams must preserve before any orchestrator implementation is admitted.

### Current Boot-To-Desktop Entrypoint Inventory

Current production desktop-launch path:

- `launch_orin_desktop.vbs` is the Windows-facing repository-root launch shim. It resolves the repository root from the script location, resolves `desktop\orin_desktop_launcher.pyw`, and starts it through the configured `pythonw.exe` path with a hidden window.
- `desktop/orin_desktop_launcher.pyw` is the current desktop launcher and orchestration authority. Its default renderer target is `desktop/orin_desktop_main.py`; harness-only environment overrides may replace the target script or log root for validation.
- `desktop/orin_desktop_main.py` is the current desktop renderer/runtime entrypoint. It receives launcher-passed `--runtime-log` and `--startup-abort-signal` arguments, emits `RENDERER_MAIN|...` milestones, creates the Qt application/window/tray/hotkey surfaces, and reports startup readiness through the launcher-owned runtime log.

Current dev-only boot/handoff surfaces:

- `main.py` contains a boot-interface and desktop-handoff prototype with `--boot-profile manual` and `--boot-profile auto_handoff_skip_import` modes. It emits `BOOT_MAIN|...` markers under `dev/logs/boot_manual_flow` or `dev/logs/boot_auto_handoff_skip_import` and constructs a `DesktopRuntimeWindow` directly for boot-transition validation.
- `dev/launchers/launch_orin_main_dev.vbs` and `dev/launchers/launch_orin_main_auto_handoff_skip_import.vbs` launch `main.py` for dev-only manual or auto-handoff flows.
- `dev/orin_boot_transition_capture.py` and `dev/orin_boot_transition_verification.py` exercise the `main.py` boot-transition path and write proof under `dev/logs/boot_transition_capture` or `dev/logs/boot_transition_verification`.
- These boot/handoff surfaces are planning and validation references only. They do not replace the current production desktop-launch path and do not own launcher final-state truth.

Current validation and support entrypoints:

- `dev/orin_desktop_entrypoint_validation.py` validates non-live desktop renderer startup, tray identity, overlay routing, and expected `RENDERER_MAIN|...` milestones.
- `dev/orin_desktop_launcher_healthy_validation.py` validates launcher-to-renderer healthy startup, launcher observation of renderer readiness, clean shutdown markers, and contained cleanup under a dev log root.
- `dev/launchers/launch_orin_desktop_safe.ps1` starts `desktop/orin_desktop_launcher.pyw` through `pythonw.exe` as a dev-safe launcher wrapper with optional overlay trace.
- Manual validation launchers under `dev/launchers/` may set `JARVIS_HARNESS_TARGET_SCRIPT`, `JARVIS_HARNESS_LOG_ROOT`, or related harness flags before invoking the launcher. Those are validation entrypoints, not production boot ownership.

Validation-helper boundary note:

- `dev/orin_desktop_launcher_regression_harness.py` is still registered as reusable launcher regression coverage, but its current constants point at legacy `jarvis_*` paths that are absent in this workspace. WS-1 does not repair helper code. A later validation/admission seam must either repair or explicitly bypass that harness before treating it as current FB-004 proof.

### Launcher Startup Ownership Boundaries

`desktop/orin_desktop_launcher.pyw` owns the current desktop startup control layer:

- single-instance acquisition and relaunch signaling through `Local\JarvisRuntimeSingletonV1` and `Local\JarvisRuntimeRelaunchRequestV1`
- renderer process spawning through `pythonw()` and the current target script
- startup observation, including `RENDERER_MAIN|STARTUP_READY`, startup-abort detection, and confirmed-startup-stall handling
- recovery attempt sequencing and terminal failure classification
- diagnostics UI launch, failure voice routing, runtime incident summaries, crash report generation, and finalized runtime/crash truth
- cleanup of launcher-owned status, stop, and startup-abort signal files when the flow exits normally, aborts, relaunches, or finalizes failure

The launcher does not own renderer presentation internals after the renderer is running. It owns the control envelope and final classification around that renderer.

### Renderer Startup Ownership Boundaries

`desktop/orin_desktop_main.py` owns the current desktop presentation and readiness layer:

- Qt application creation and desktop runtime window construction
- tray identity, tray discovery cue, overlay routing, Create Custom Task tray routing, and global hotkey startup
- cooperative response to launcher-passed startup-abort and relaunch signals
- `RENDERER_MAIN|...` milestone emission into the launcher-owned runtime log
- startup-ready emission after the core visualization becomes visible
- passive default handoff to the dormant desktop state after readiness
- renderer event-loop exit and clean renderer shutdown markers

The renderer does not own retry policy, crash classification, recovery escalation, diagnostics finalization, or final runtime outcome truth. Those remain launcher-owned.

### Diagnostics Evidence Roots

Current live launcher/runtime evidence:

- launcher default runtime log root: `<runtime root>/logs` through `DEFAULT_LOG_DIR`
- launcher runtime logs: `Runtime_<timestamp>_<token>.txt`
- launcher crash reports: `<log root>/crash/Crash_<timestamp>_<token>.txt`
- launcher status/control files: `<log root>/diagnostics_status.txt`, `<log root>/diagnostics_stop.signal`, and `<log root>/renderer_startup_abort.signal`
- historical runtime state: `%LOCALAPPDATA%/Nexus Desktop AI/state/jarvis_history_v1.jsonl` during normal runtime, with harness log-root override behavior confined to validation contexts

Current dev and harness evidence:

- desktop entrypoint validation: `dev/logs/desktop_entrypoint_validation/...`
- desktop launcher healthy validation: `dev/logs/desktop_launcher_healthy_validation/...`
- boot transition capture: `dev/logs/boot_transition_capture/...`
- boot transition verification: `dev/logs/boot_transition_verification/...`
- boot auto handoff runtime logs: `dev/logs/boot_auto_handoff_skip_import/...`
- startup snapshot validation: `dev/logs/startup_snapshot_harness_validation/...`

Evidence-root boundary:

- Root `logs/` is ignored runtime evidence and must not be used for new dev or harness evidence by default.
- Dev, boot-transition, toolkit, and harness proof belongs under `dev/logs/<lane>/...`.
- Future FB-004 implementation must not create a new diagnostics evidence root, promote a dev root to live truth, or move launcher-owned state without an explicit admitted implementation seam and rollback plan.

### Rollback Boundaries

WS-1 rollback:

- Revert the WS-1 docs/canon commit and return this record to the post-Branch-Readiness state where WS-1 is admitted but not executed.

Future runtime rollback baseline:

- The safe current desktop baseline remains `launch_orin_desktop.vbs` -> `desktop/orin_desktop_launcher.pyw` -> `desktop/orin_desktop_main.py`.
- Any later change to the launch shim must roll back without changing launcher target semantics.
- Any later launcher change must roll back to the current default target, retry/recovery model, signal-file cleanup, single-instance/relaunch behavior, and runtime/crash evidence roots.
- Any later renderer change must roll back to renderer-owned startup milestone emission, tray/hotkey initialization, startup-ready timing, passive dormant handoff, and clean event-loop shutdown behavior.
- Any later boot-orchestrator implementation must remain above the launcher until an explicit seam admits a delegation-boundary change; rollback must restore launcher-owned final-state truth.
- Dev-only `main.py` boot-transition behavior must not become production boot ownership by accident; any promotion from dev prototype to product path requires separate implementation admission and user-facing validation.

## Reuse Baseline

- `Docs/architecture.md` and `Docs/orchestration.md` are the baseline architecture and orchestration references for current startup, launcher, renderer, and evidence boundaries.
- `Docs/workstreams/FB-025_boot_desktop_milestone_taxonomy_clarification.md` preserves historical boot/desktop milestone separation and must not be expanded by inertia.
- `Docs/workstreams/FB-033_startup_snapshot_harness_follow_through.md` preserves startup snapshot harness context for future validation reuse where applicable.
- `Docs/phase_governance.md`, `Docs/development_rules.md`, `Docs/codex_modes.md`, and `Docs/orin_task_template.md` own phase, seam, proof, User Test Summary, and durability governance.
- `dev/orin_branch_governance_validation.py` is the reusable governance validator for this admission pass.
- No new validator, harness, runtime helper, desktop export, or release helper is introduced during Branch Readiness.

## Exit Criteria

- Branch objective is recorded.
- Target end-state is recorded.
- Seam families and risk classes are recorded.
- Validation contract is recorded.
- User Test Summary strategy is recorded.
- Later-phase expectations are recorded.
- First Workstream seam is recorded and admitted next.
- Backlog, roadmap, workstream index, and Main routing all point to this canonical FB-004 workstream record.
- Branch Readiness validation passes.
- Branch remains docs/canon only.

## Rollback Target

- `Branch Readiness`
- Revert the FB-004 Branch Readiness canon promotion commit and return FB-004 to selected-only registry truth with no admitted Workstream seam.

## Next Legal Phase

- `Workstream`
