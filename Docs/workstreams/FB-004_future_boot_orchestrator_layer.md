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

- `Workstream complete / Hardening next`
- FB-032 is released and closed in `v1.6.2-prebeta`.
- Latest public prerelease truth is `v1.6.2-prebeta`.
- Release debt is clear.
- FB-004 is promoted and active in this canonical workstream record.
- Branch Readiness is complete.
- WS-1 current boot-to-desktop source map and ownership boundary is complete.
- WS-2 lifecycle and orchestration-state framing for boot and desktop transitions is complete.
- WS-3 validation and admission contract for orchestrator implementation seams is complete.
- Hardening is the next legal phase.
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

- Status: Completed.
- Goal: define the lifecycle states and transition ownership between future boot framing, current desktop launcher authority, renderer readiness, failure/recovery states, and desktop-settled outcomes.
- Scope: docs/canon lifecycle vocabulary, state-transition framing, ownership handoff boundaries, ambiguity capture, and implementation-readiness risks.
- Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no release work, and no public release editing.

Seam 3: Validation and admission contract for orchestrator implementation seams

- Status: Completed.
- Goal: define the proof and admission contract required before any future boot orchestrator implementation can change launcher, renderer, shortcut, startup, diagnostics, or user-facing surfaces.
- Scope: validation gates, shortcut/User Test Summary triggers, rollback proof, helper reuse requirements, implementation admission checklist, and later-phase evidence expectations.
- Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no release work, and no public release editing.

## Active Seam

Active seam: WS-3 validation and admission contract for orchestrator implementation seams is complete; no active Workstream seam remains before Hardening.

- BR-1 Status: Completed in this pass.
- BR-1 Boundary: promote FB-004, define branch objective, target end-state, seam families, validation contract, User Test Summary strategy, later-phase expectations, and the first Workstream seam.
- BR-1 Non-Includes: no runtime behavior, launcher behavior, desktop shortcut behavior, UI implementation, service/autostart work, installer work, source tree reorganization, release packaging, tag creation, or public release editing.
- WS-1 Status: Completed / executed.
- WS-1 Boundary: docs/canon source map and ownership boundary only.
- WS-1 Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no source tree reorganization, no release work, and no public release editing.
- WS-2 Status: Completed / executed.
- WS-2 Boundary: docs/canon lifecycle and orchestration-state framing only.
- WS-2 Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no release work, and no public release editing.
- WS-3 Status: Completed / executed.
- WS-3 Boundary: docs/canon validation and implementation-admission contract only.
- WS-3 Non-Includes: no runtime code edits, no launcher behavior changes, no desktop shortcut changes, no renderer lifecycle implementation, no UI work, no installer or autostart work, no release work, and no public release editing.

## Seam Continuation Decision

Continue Decision: `stop`
Next Active Seam: `Hardening`
Stop Condition: `phase boundary reached`
Continuation Action: FB-004 Workstream seam chain is complete after validation; proceed to Hardening next.

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

## WS-2 Execution Record

WS-2 is docs/canon only. It defines the lifecycle and orchestration-state framing that future boot-orchestrator work must use when reasoning about current desktop launch, dev-only boot transition evidence, failure handling, and handoff boundaries.

### Lifecycle Families

Production desktop-launch lifecycle:

1. `launch_orin_desktop.vbs` launches `desktop/orin_desktop_launcher.pyw`.
2. The launcher acquires or negotiates single-instance ownership, resets launcher status, creates the runtime log, and emits launcher-runtime start evidence.
3. The launcher starts a renderer attempt, spawns `desktop/orin_desktop_main.py`, passes the runtime log and startup-abort signal path, and begins startup observation.
4. The renderer creates the Qt application, resolves the visual HTML, constructs `DesktopRuntimeWindow`, initializes tray/hotkey surfaces, and defers visible window show until the core visualization is ready.
5. `DesktopRuntimeWindow` reports visual page readiness and core visualization readiness, then the renderer requests window show and desktop-mode attachment.
6. The renderer emits `RENDERER_MAIN|CORE_VISUALIZATION_FIRST_VISIBLE`, then `RENDERER_MAIN|STARTUP_READY`, and requests passive default handoff to `state=dormant`.
7. The launcher observes `RENDERER_MAIN|STARTUP_READY` and treats the startup attempt as ready. Final success, relaunch, startup abort, crash, or recovery exhaustion remains launcher-owned.

Dev-only boot-transition lifecycle:

1. `main.py` starts with a selected boot profile and audio mode and writes `BOOT_MAIN|START|profile=...|audio=...`.
2. The boot prototype resolves monitor topology, constructs boot windows and a `DesktopRuntimeWindow`, and emits boot-window construction and display markers.
3. The boot prototype runs the boot sequence, accepts the HUD command, resolves import choice, and emits `BOOT_MAIN|TRANSITION_BEGIN|import_home=...`.
4. The boot prototype emits `BOOT_MAIN|HANDOFF_SIGNAL_EMITTED`, shows the desktop window, hides boot windows, marks `BOOT_MAIN|DESKTOP_VISIBLE`, commits `state=dormant`, and emits `BOOT_MAIN|DESKTOP_SETTLED|state=dormant`.
5. This lifecycle is a dev-only boot/handoff evidence path. It is not the production desktop-launch path and is not equivalent to launcher-owned final runtime truth.

### State Vocabulary

Boot-framing states:

- `boot-profile selected`: dev-only `main.py` runtime configuration is resolved.
- `topology resolved`: dev-only screen layout is validated and assigned.
- `boot windows shown`: dev-only boot presentation is visible.
- `awaiting command`: dev-only boot prototype is waiting for the first accepted command.
- `awaiting import choice`: dev-only boot prototype is waiting for import-home choice.
- `transition begin`: dev-only handoff from boot presentation toward desktop presentation has started.
- `handoff emitted`: dev-only boot prototype requested desktop handoff.
- `desktop settled`: dev-only desktop presentation reached the expected dormant state after handoff.

Launcher states:

- `launcher runtime start`: launcher control envelope is active.
- `single-instance conflict`: launcher detected an existing runtime and either signals relaunch or exits by user choice.
- `recovery attempt start`: launcher starts a bounded renderer attempt.
- `renderer spawned`: renderer process has a PID and startup observation begins.
- `startup ready observed`: launcher found `RENDERER_MAIN|STARTUP_READY` in the runtime log.
- `startup ready missing`: launcher did not observe readiness inside the initial window.
- `startup stall confirmed`: launcher confirmed readiness did not arrive inside the stall window.
- `startup abort requested`: launcher writes the startup-abort signal for cooperative renderer shutdown.
- `startup abort observed`: launcher sees renderer acknowledgement of startup abort.
- `failure classified`: launcher extracts failure cause/origin and updates status evidence.
- `recovery exhausted`: launcher has no remaining permitted recovery path.
- `normal exit complete`: renderer exited normally and launcher cleaned status/signal artifacts.
- `failure flow complete`: launcher wrote final incident/crash evidence and finalized failure history.

Renderer states:

- `renderer main start`: renderer script entered its main flow.
- `Qt application created`: renderer has a Qt application.
- `visual resolved`: renderer resolved the visual HTML.
- `window constructed`: renderer constructed `DesktopRuntimeWindow`.
- `tray and hotkeys ready`: renderer initialized tray and global hotkey surfaces.
- `core visualization ready`: web visual page finished loading and pending visual state can apply.
- `window show requested`: renderer requests visible show after core visualization readiness.
- `desktop mode enable begin`: `DesktopRuntimeWindow` begins attaching/reframing the window as desktop presentation.
- `core visualization first visible`: initial visibility guard is released and the core is visible.
- `startup ready`: renderer reports ready after first visible core.
- `passive dormant handoff`: renderer sets the visual state to `dormant`.
- `renderer shutdown begin`: renderer begins cooperative shutdown.
- `event loop exit`: renderer Qt event loop has exited.

### Ownership Handoff Rules

- Future boot framing may own pre-delegation presentation, trust/access framing, and handoff narration only until it delegates into the desktop launcher or another explicitly admitted desktop authority.
- Current production desktop authority begins at `desktop/orin_desktop_launcher.pyw`; no future boot frame may reinterpret launcher-owned final classifications after delegation.
- Renderer readiness is not launcher success. `RENDERER_MAIN|STARTUP_READY` only proves the renderer reached the ready marker; the launcher still owns final runtime outcome.
- Dev-only `BOOT_MAIN|DESKTOP_SETTLED|state=dormant` is not the same state as production `RENDERER_MAIN|STARTUP_READY` or launcher `STARTUP_READY_OBSERVED`.
- `state=dormant` is a visual presentation state, not a trust state, authentication state, recovery state, or release-readiness state.
- `Local\JarvisRuntimeRelaunchRequestV1` is shared by the dev boot prototype, launcher, and renderer. Any future orchestrator implementation must explicitly define whether it observes, emits, or owns that signal before changing it.
- Startup-abort files, diagnostics status files, runtime logs, crash reports, and finalized historical records are launcher-owned unless a later implementation seam explicitly changes ownership.

### Transition Ambiguities Captured For Later Seams

- `main.py` contains a boot-like interface and direct desktop handoff, but current architecture canon still defines the production runtime path as the launcher stack. Future work must keep `main.py` as dev/prototype truth until an implementation seam promotes or replaces it.
- `DesktopRuntimeWindow` is shared by the production renderer and dev boot prototype. Shared class reuse does not imply shared lifecycle ownership.
- The boot prototype constructs and controls a desktop window directly, while the production launcher delegates into `desktop/orin_desktop_main.py`. A future orchestrator must choose one delegation model explicitly instead of blending both.
- Current dev boot transition proof depends on monitor topology and boot-profile runtime markers, while production desktop readiness proof depends on launcher and renderer markers. Future validation must not substitute one proof family for the other without a recorded waiver.
- The reusable launcher regression harness has stale legacy path constants. WS-3 must account for that before admitting any orchestrator implementation proof that claims launcher regression coverage.

## WS-3 Execution Record

WS-3 is docs/canon only. It defines the validation and admission contract that must gate any later boot-orchestrator implementation seam. It does not admit implementation by itself.

### Implementation Admission Checklist

Before any later FB-004 implementation seam may edit runtime or user-facing surfaces, it must record:

- affected surface class: launch shim, desktop launcher, desktop renderer, `DesktopRuntimeWindow`, dev boot prototype, desktop shortcut, installer/OS integration, diagnostics evidence, state/history, or validation helper
- ownership class: future boot framing, launcher-owned, renderer-owned, shared helper, dev-only prototype, or user-facing entrypoint
- exact rollback target and rollback command or revert scope
- expected runtime markers before and after the change
- expected persisted files, state roots, signal files, log roots, and cleanup behavior before and after the change
- helper reuse decision from `Docs/validation_helper_registry.md`
- User Test Summary and user-facing shortcut applicability
- explicit non-includes that prevent adjacent launcher, renderer, UI, installer, service/autostart, release, or source-tree work from entering by inertia

If an implementation seam cannot answer those items before edits begin, it is not admitted.

### Required Proof By Surface Class

Docs/canon-only seams:

- `python dev\orin_branch_governance_validation.py`
- `git diff --check`
- source-truth sweep confirming backlog, roadmap, workstream index, and this workstream record agree on phase, seam state, blockers, and next legal phase

Desktop entrypoint or renderer-readiness seams:

- `dev/orin_desktop_entrypoint_validation.py` unless the seam records a stronger replacement
- runtime marker review for `RENDERER_MAIN|START`, `QAPPLICATION_CREATED`, `VISUAL_HTML_RESOLVED`, `WINDOW_CONSTRUCTED`, `WINDOW_SHOW_DEFERRED_UNTIL_CORE_READY`, `CORE_VISUALIZATION_READY`, `CORE_VISUALIZATION_FIRST_VISIBLE`, and `STARTUP_READY`
- no regression in tray identity, overlay route, startup-abort handling, or passive dormant handoff when those surfaces are affected

Launcher startup, recovery, or diagnostics seams:

- `dev/orin_desktop_launcher_healthy_validation.py` for healthy launcher-to-renderer startup proof
- failure/recovery coverage only through a current, repaired, or explicitly admitted harness path
- runtime marker review for launcher recovery attempts, renderer spawn, startup observation, startup-abort handling, normal exit, failure flow, status/signal cleanup, and crash-log behavior
- crash report and runtime incident evidence review when failure behavior is affected

Boot-transition or boot-prototype seams:

- `dev/orin_boot_monitor_preflight.py` when monitor topology assumptions matter
- `dev/orin_boot_transition_verification.py` for marker-order proof
- `dev/orin_boot_transition_capture.py` when visual capture proof is materially required
- explicit proof that dev-only boot markers do not replace production launcher readiness markers unless the seam admits that product-path change

Startup snapshot or diagnostics-evidence seams:

- `dev/orin_startup_snapshot_harness_validation.py` when startup snapshot behavior is touched
- proof that snapshot output remains opt-in and writes to a dev evidence path
- proof that new dev or worker evidence does not write under root live logs without explicit approval

Desktop shortcut or visible startup seams:

- launch through the declared user-facing desktop shortcut or equivalent user entrypoint during Live Validation
- record `User-Facing Shortcut Path:` and `User-Facing Shortcut Validation:` in this workstream record before User Test Summary handoff
- add and export the canonical User Test Summary when the completed delta changes user-visible startup, shortcut behavior, visible runtime behavior, prompts, tray/overlay behavior, voice behavior, or another operator-facing path

### Helper Reuse And Repair Contract

- Reuse-first selection from `Docs/validation_helper_registry.md` is mandatory before any new helper is created.
- New durable root `dev/` helpers must follow the `dev/orin_<domain>_<capability>_...` naming pattern and be registered immediately.
- Workstream-scoped helpers require owner, non-reuse reason, consolidation target, and promotion decision point before PR Readiness.
- Temporary probes must stay under ignored evidence roots and must be deleted or promoted before closeout-grade proof.
- `dev/orin_desktop_launcher_regression_harness.py` currently points at absent legacy `jarvis_*` paths. It must be repaired, replaced by a current registered helper, or explicitly bypassed with a documented rationale before launcher regression coverage can be claimed for FB-004.

### User Test Summary Admission Rules

- WS-1 through WS-3 are docs/canon only and do not require User Test Summary handoff.
- A later implementation seam that changes user-visible startup behavior, desktop shortcut behavior, runtime interaction, visible desktop UI, tray behavior, prompts, voice behavior, installer/OS integration, or another operator-facing path must add the exact `## User Test Summary` section before Live Validation.
- If User Test Summary is required, the desktop export at `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt` must also be refreshed unless an explicit documented exception applies.
- If a later completed delta remains non-user-facing, Live Validation may waive User Test Summary only with a recorded waiver reason.

### Rollback And Cleanup Contract

Any later implementation seam must prove rollback and cleanup at the same surface it changed:

- launch shim changes must restore the previous shim target and invocation behavior
- launcher changes must restore default target, retry/recovery policy, signal files, status cleanup, runtime log generation, crash report behavior, single-instance mutex, and relaunch event semantics
- renderer changes must restore startup markers, startup-ready timing, tray/hotkey startup, desktop attach behavior, passive dormant handoff, and event-loop exit behavior
- boot-prototype changes must remain dev-only unless product promotion is explicitly admitted
- diagnostics changes must restore evidence roots and prevent new dev evidence from entering live root logs by default
- helper changes must leave no unregistered durable helper and no temporary closeout-grade probe

### Implementation Admission Blockers

The following conditions block future implementation until resolved inside an admitted seam:

- affected surface cannot be named precisely
- ownership boundary between boot, launcher, renderer, shared helper, and dev-only prototype is ambiguous
- rollback target or cleanup path is undefined
- required helper is stale, absent, unregistered, or weaker than the surface being changed
- user-facing shortcut validation applicability is unresolved for a user-facing startup or shortcut delta
- User Test Summary applicability is unresolved for a user-facing or operator-facing delta
- a seam attempts installer, service/autostart, OS integration, release packaging, tag work, or public release editing without explicit phase authority
- a seam promotes `main.py` boot prototype behavior into product boot ownership without product-path admission and user-facing validation

### Workstream Validation Results

- `python dev\orin_branch_governance_validation.py`: PASS after WS-1 and WS-2 checkpoints.
- `git diff --check`: PASS after WS-1 and WS-2 checkpoints.
- WS-1 scope validation: PASS; docs/canon source map only.
- WS-2 scope validation: PASS; docs/canon lifecycle/state framing only.
- WS-3 scope validation: PASS; docs/canon validation and implementation-admission contract only.
- Final Workstream validation: `python dev\orin_branch_governance_validation.py` PASS, 914 checks.
- Final whitespace validation: `git diff --check` PASS.

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
- WS-1 current boot-to-desktop source map and ownership boundary is complete.
- WS-2 lifecycle and orchestration-state framing for boot and desktop transitions is complete.
- WS-3 validation and admission contract for orchestrator implementation seams is complete.
- Backlog, roadmap, workstream index, and Main routing all point to this canonical FB-004 workstream record.
- Workstream validation passes.
- Branch remains docs/canon only through WS-1, WS-2, and WS-3.

## Rollback Target

- `Branch Readiness`
- Revert the FB-004 Branch Readiness canon promotion commit and return FB-004 to selected-only registry truth with no admitted Workstream seam.

## Next Legal Phase

- `Hardening`
