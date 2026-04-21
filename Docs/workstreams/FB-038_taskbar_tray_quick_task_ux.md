# FB-038 Taskbar / Tray Quick-Task UX And Create Custom Task Surface

## ID And Title

- ID: `FB-038`
- Title: `Taskbar / tray quick-task UX and Create Custom Task surface`

## Record State

- `Promoted`

## Status

- `Hardening`

## Release Stage

- `pre-Beta`

## Target Version

- `TBD`

## Canonical Branch

- `feature/fb-038-taskbar-tray-quick-task-ux`

## Purpose / Why It Matters

Define and deliver the smallest safe shell-facing quick-task entry surface above the released interaction, authoring, callable-group execution, and built-in catalog baselines.

This workstream exists so taskbar or tray access and Create Custom Task entry are planned as deliberate UX surfaces instead of being added by inertia to the overlay, authoring, launcher, or settings systems.

## Current Phase

- Phase: `Hardening`

## Phase Status

- `Active Branch`
- current branch: `feature/fb-038-taskbar-tray-quick-task-ux`
- Branch Readiness is complete and durably checkpointed in commit `766ff67`
- Workstream seam chain and helper governance are complete and durably checkpointed in commit `ef05ab2`
- Hardening is admitted for branch-wide pressure testing; Hardening execution has not started in the transition pass
- FB-037 is released and closed in `v1.4.0-prebeta`
- FB-037 release publication exists at `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.4.0-prebeta`
- no FB-037 release-debt blocker remains
- no active release-packaging branch remains

## Branch Class

- `implementation`

## Blockers

- None.

## Entry Basis

- local `main` and `origin/main` are aligned at the FB-037 release-packaging merge baseline
- current branch is `feature/fb-038-taskbar-tray-quick-task-ux`
- current branch is based on updated `main`
- Branch Readiness governance/canon repair plus FB-038 admission setup is durable in commit `766ff67`
- Workstream seam chain completion, Workstream evidence finalization, User Test Summary finalization, and helper-governance registry integration are durable in commit `ef05ab2`
- FB-037 is `Released (v1.4.0-prebeta)` and `Closed`
- the `v1.4.0-prebeta` Git tag exists locally and remotely
- the GitHub prerelease for `v1.4.0-prebeta` exists, is published, and is marked prerelease
- FB-038 was selected in canon before this admission and is now promoted
- Branch Readiness exit criteria are satisfied
- Workstream exit criteria are satisfied: all approved seams are complete and green, the workstream-owned User Test Summary is current, evidence references exist, and no same-slice correctness gap remains

## Exit Criteria

- branch-wide pressure testing is complete for the tray overlay entry, tray Create Custom Task dialog-open/no-write path, tray-origin create completion, catalog reload, and exact-match re-resolution behavior
- helper default profiles and workstream-scoped helper obligations are pressure-tested enough to decide whether consolidation, promotion, or continued workstream-scoped status is appropriate before PR Readiness
- no regression appears in released FB-027 interaction behavior, FB-036 authoring/source safety, FB-041 callable-group behavior, or FB-037 built-in catalog and saved-action override behavior
- no stale evidence, no unresolved helper-governance contradiction, and no branch-truth drift remains
- Hardening validation is green enough to proceed to Live Validation

## Rollback Target

- `Workstream`

## Next Legal Phase

- `Live Validation`

Hardening was admitted after validating Workstream closure, evidence references, User Test Summary alignment, helper registry compliance, and clean durable branch truth. The next safe move is a separate Hardening execution pass; do not perform Hardening pressure testing inside the phase-transition admission pass.

## Bounded Objective

Plan and then implement the smallest safe user-facing entry surface for quick task access from taskbar or tray context, including a Create Custom Task affordance only when it can reuse the released shared action and authoring foundations safely.

The branch should prove a bounded shell-facing UX milestone, not redesign the action system.

## Target End-State

- a clearly bounded taskbar or tray quick-task entry surface is implemented or the branch records why the smallest safe surface must be deferred
- Create Custom Task entry reuses the released FB-036 authoring model rather than inventing a second authoring path
- released shared-action resolution, saved-action authority, built-in catalog behavior, and callable-group execution remain unchanged
- branch-local validation and Live Validation evidence are sufficient to support PR Readiness

## Expected Seam Families And Risk Classes

- source map / seam-selection audit:
  - risk class: analysis and boundary-setting
  - goal: identify the existing taskbar, tray, launcher, overlay, and Create Custom Task entry surfaces before selecting code changes
- shell-facing entry surface:
  - risk class: UI-model and launcher-adjacent desktop UX
  - goal: expose one smallest safe taskbar or tray entry into existing Nexus behavior
- Create Custom Task affordance:
  - risk class: authoring-entry UX over released FB-036 foundations
  - goal: route to the existing authoring surface without changing saved-action schema, collision rules, or resolution behavior
- validation support:
  - risk class: helper or harness support only if the existing validation surface cannot prove the selected UX seam

Because taskbar, tray, launcher-adjacent, and UI-model behavior are higher-risk than catalog-only actions, FB-038 begins with single-seam fallback by default.
Bounded multi-seam workflow may be used later only if a Workstream analysis proves the seams share the same risk class, subsystem family, and validation gate.

## First Workstream Pass

The first Workstream source-map and seam-selection pass is complete.

It selected:

- `Minimal Tray Overlay Entry`

The selected seam proves a tray-shell entry into the existing command overlay path before any direct tray-to-authoring behavior is attempted.

Explicit non-includes for the selected seam:

- no direct `Create Custom Task` tray action
- no saved-action schema, source, authoring, collision, or resolution changes
- no built-in catalog changes
- no callable-group changes
- no taskbar pinning, jump lists, installer policy, startup registration, or protocol handling
- no launcher recovery changes
- no UI redesign, confirm/result copy changes, or settings surface work

## Explicit Non-Goals

- no product/runtime implementation during Branch Readiness
- no implementation before the first Workstream pass selects and bounds a seam
- no broad UI redesign
- no Action Studio behavior
- no saved-action schema change
- no shared-action resolution change
- no built-in catalog expansion
- no callable-group execution change
- no new target kinds
- no settings or protocol behavior
- no installer, startup, or Windows pinning policy changes unless a later approved seam proves that is the smallest safe need
- no external trigger, plugin integration, monitoring, thermals, or performance HUD work
- no FB-039 or FB-040 scope

## Reuse Baseline

- `Docs/closeouts/nexus_prebeta_rebaseline_through_v1.4.0-prebeta.md`
- `Docs/workstreams/FB-037_built_in_actions_and_settings_expansion.md`
- `Docs/workstreams/FB-041_deterministic_callable_group_execution_layer.md`
- `Docs/workstreams/FB-036_saved_action_authoring.md`
- `Docs/workstreams/FB-027_interaction_system_baseline.md`
- `desktop/shared_action_model.py`
- `desktop/interaction_overlay_model.py`

## Validation Contract

Branch Readiness validation proved:

- FB-038 is promoted exactly once
- this canonical workstream doc exists and owns active phase authority
- backlog, roadmap, workstream index, and this workstream doc agreed on `Branch Readiness`
- FB-037 remains released and closed in `v1.4.0-prebeta`
- no product/runtime code changed during Branch Readiness
- `python dev/orin_branch_governance_validation.py` passes
- `git diff --check` passes

Workstream validation must preserve:

- released FB-027 typed-first interaction baseline
- released FB-036 saved-action authoring, collision, and source-safety behavior
- released FB-041 deterministic callable-group execution behavior
- released FB-037 built-in catalog behavior and saved-action override authority
- existing confirm/result boundaries unless a later approved UI seam explicitly scopes visible changes

Future desktop UX validation must include:

- repo-side validators for affected behavior
- real interactive OS-level proof when feasible
- cleanup verification for any windows, tray state, helper processes, or temporary artifacts opened by validation
- User Test Summary updates when the branch changes user-visible behavior
- helper reuse and naming checks through `Docs/validation_helper_registry.md` before any new durable root `dev/` validation helper is kept

Seam 1 `Minimal Tray Overlay Entry` validation must prove:

- startup still reaches `RENDERER_MAIN|STARTUP_READY`
- tray entry initialization emits runtime markers
- tray activation routes to the existing command overlay path
- existing hotkey, overlay, saved-action, built-in, confirm, result, and callable-group baselines are not widened by the seam

## User Test Summary Strategy

No meaningful manual User Test Summary exists yet because Branch Readiness does not change product behavior.

When a Workstream seam changes taskbar, tray, Create Custom Task, or other user-visible desktop behavior, update this workstream's `## User Test Summary` incrementally and refresh `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt` when the user-facing seam chain is complete unless an explicit exception applies.

## Later-Phase Plan

- Workstream:
  - run the first source-map and seam-selection pass
  - implement only the approved smallest safe seam
  - validate before continuing
  - use single-seam fallback until same-risk continuation is explicitly proven safe
- Hardening:
  - pressure-test the selected shell-facing UX and authoring-entry behavior across normal and edge cases
  - repair only defects, validation gaps, or helper seams inside the approved scope
- Live Validation:
  - capture real desktop evidence for taskbar/tray/Create Custom Task behavior when implementation reaches that point
  - digest evidence into this authority record before phase advancement
- PR Readiness:
  - complete merge-target canon, Governance Drift Audit, next-workstream selection, post-merge truth, and dirty-branch gates before PR green
- Release Readiness:
  - if FB-038 becomes a user-facing implementation milestone, handle release packaging only after merge according to the release-debt model

## Branch Readiness Progress

- promoted FB-038 from `Registry-only` to `Promoted`
- created this canonical workstream record
- recorded Branch Readiness phase authority, scope, non-goals, reuse baseline, validation contract, User Test Summary strategy, and later-phase plan
- preserved FB-037 released truth and cleared release-debt posture
- validated Branch Readiness with `python dev/orin_branch_governance_validation.py`
- validated whitespace with `git diff --check`
- committed Branch Readiness admission in `766ff67`
- transitioned phase authority from `Branch Readiness` to `Workstream`
- no product/runtime implementation was started during the transition

## Workstream Progress

- Source-map and seam selection complete:
  `Minimal Tray Overlay Entry` is the first implementation seam.
- Seam 1 complete:
  `Minimal Tray Overlay Entry`
- Added a lightweight desktop runtime tray entry in `desktop/orin_desktop_main.py`.
- Tray activation routes only through the existing `DesktopRuntimeWindow.toggle_command_overlay()` path.
- Added runtime markers:
  - `RENDERER_MAIN|TRAY_ENTRY_INITIALIZE_REQUESTED`
  - `RENDERER_MAIN|TRAY_ENTRY_READY`
  - `RENDERER_MAIN|TRAY_ICON_SHOWN` when the OS tray is available
  - `RENDERER_MAIN|TRAY_ACTIVATION_REQUESTED`
  - `RENDERER_MAIN|TRAY_ACTIVATION_ROUTED_TO_OVERLAY`
- Extended `dev/orin_desktop_entrypoint_validation.py` to prove startup readiness, tray initialization markers, and tray activation routing to the existing overlay toggle path.
- Same-phase seam-1 hardening completed:
  tray initialization now fails closed if Qt tray construction is unavailable or throws, startup-abort and shutdown paths hide the tray entry when needed, and validator coverage proves the bounded failure path emits `TRAY_ENTRY_READY|available=false|reason=RuntimeError` instead of crashing startup.
- Preserved explicit non-includes:
  no direct Create Custom Task tray action, saved-action changes, built-in catalog changes, callable-group changes, taskbar pinning, jump lists, installer policy, startup registration, protocol handling, launcher recovery changes, UI redesign, confirm/result copy changes, or settings surface work.
- Repo-side validation for Seam 1 passed:
  - `python dev/orin_desktop_entrypoint_validation.py`
  - `python dev/orin_interaction_baseline_validation.py`
  - `python dev/orin_branch_governance_validation.py`
  - `git diff --check`
- Manual/live validation checkpoint for Seam 1 passed:
  - evidence root: `dev/logs/fb_038_tray_live_validation/20260420_182512`
  - live runtime startup reached `RENDERER_MAIN|STARTUP_READY`
  - live runtime tray setup emitted `RENDERER_MAIN|TRAY_ENTRY_READY|available=true` and `RENDERER_MAIN|TRAY_ICON_SHOWN`
  - Windows UIAutomation exposed the tray entry as `Nexus Desktop AI` / `SystemTray.NormalButton`
  - keyboard activation of that tray entry emitted `RENDERER_MAIN|TRAY_ACTIVATION_REQUESTED|source=activation_Trigger` and opened the existing overlay with `RENDERER_MAIN|COMMAND_OVERLAY_OPENED|phase=entry|input_armed=true`
  - `Ctrl+Alt+Home` still opened the same command overlay path
  - controlled shutdown emitted `RENDERER_MAIN|SHUTDOWN_REQUESTED` and `RENDERER_MAIN|TRAY_ICON_HIDDEN`
  - no Create Custom Task direct-routing marker appeared
  - cleanup verification found `leftover_runtime_processes=0`
  - earlier failed probe roots remain classified as superseded, non-passing exploratory evidence:
    - `dev/logs/fb_038_tray_live_validation/20260420_154502`
    - `dev/logs/fb_038_tray_live_validation/20260420_154713`
    - `dev/logs/fb_038_tray_live_validation/20260420_155022`
  - classification: `manual/live activation evidence complete`
  - continuation decision: Seam 1 is fully validated for user-visible shell activation; Seam 2 selection may begin in a separate Workstream seam-selection pass
- Seam 2 complete:
  `Tray Create Custom Task Entry, Dialog-Open Only`
- Seam 2 implementation added a tray menu `Create Custom Task` affordance that routes through the existing overlay entry path and existing `handle_create_custom_task_requested()` authoring surface.
- Seam 2 added runtime proof markers for tray-origin authoring entry:
  - `RENDERER_MAIN|TRAY_CREATE_CUSTOM_TASK_REQUESTED`
  - `RENDERER_MAIN|TRAY_CREATE_CUSTOM_TASK_ROUTED_TO_OVERLAY_ENTRY`
  - existing `RENDERER_MAIN|COMMAND_OVERLAY_OPENED`
  - existing `RENDERER_MAIN|OVERLAY_ENTRY_ACTION_TRIGGERED|action=create_custom_task`
  - existing `RENDERER_MAIN|OVERLAY_ENTRY_DIALOG_CREATED|action=create_custom_task`
- Seam 2 validation support added:
  - tray create-action route coverage in `dev/orin_desktop_entrypoint_validation.py`
  - dialog-open/no-write coverage in `dev/orin_saved_action_authoring_ui_validation.py`
- Seam 2 validation status:
  - added `dev/orin_fb038_seam2_validation.ps1` as the deterministic repo-local validator runner for this seam
  - added `dev/orin_fb038_seam2_live_validation.ps1` as the stable repo-local manual/live validation helper for the tray menu, dialog-open/no-write, tray overlay baseline, and hotkey overlay baseline evidence path
  - both helpers are registered as `Workstream-scoped` in `Docs/validation_helper_registry.md`; Hardening or PR Readiness must decide whether to consolidate them into reusable tray/authoring validation support, promote them, or keep them explicitly workstream-scoped
  - the runner resolves `NEXUS_VALIDATION_PYTHON`, then the existing Nexus user-local Python at `C:\Users\anden\AppData\Local\Python\pythoncore-3.14-64\python.exe`, then `python` on `PATH`
  - the runner refuses to proceed unless `PySide6` imports successfully; no validator skip, stub, or fake pass condition was added
  - `python` and `py` remain unavailable in the current sandbox `PATH`, but the user-local Nexus Python is available and has `PySide6 6.10.2`
  - `dev/orin_fb038_seam2_validation.ps1` passed
  - latest passing entrypoint report: `dev/logs/desktop_entrypoint_validation/reports/DesktopEntrypointValidationReport_20260420_221016.txt`
  - `dev/orin_desktop_entrypoint_validation.py` passed with the user-local Qt-capable Python, including tray initialization, tray overlay routing, and tray Create Custom Task request routing
  - `dev/orin_interaction_baseline_validation.py` passed with the user-local Qt-capable Python
  - `dev/orin_saved_action_authoring_ui_validation.py` passed with the user-local Qt-capable Python, including tray-origin Create Custom Task dialog-open/no-write coverage
  - `dev/orin_branch_governance_validation.py` passed with `292` checks
  - `git diff --check` passed with CRLF normalization warnings only
  - manual/live helper evidence passed at `dev/logs/fb_038_tray_create_live_validation/20260420_220847`
  - manual/live evidence observed the required tray-origin marker chain, confirmed `saved_actions.json` hash/timestamp/length unchanged on open/cancel, confirmed absence of `CUSTOM_TASK_CREATE_ATTEMPT_STARTED` and `CUSTOM_TASK_CREATED`, and rechecked both the tray `Open Command Overlay` baseline and the hotkey overlay baseline
  - Seam 2 is fully green.
  - continuation decision at Seam 2 closeout: Seam 3 could only start in a separate bounded Workstream pass.
- Seam 3 complete:
  `Tray-Origin Create Completion And Catalog Re-Resolution`
- Seam 3 reused the existing FB-036 authoring, persistence, catalog reload, resolution, confirm, and result paths without adding a new persistence path, target kind, schema field, or parallel resolution model.
- Seam 3 validation support added:
  - tray-origin create-completion/re-resolution coverage in `dev/orin_saved_action_authoring_ui_validation.py`
  - `dev/orin_fb038_seam3_live_validation.ps1` as the stable repo-local live helper for tray-origin create, persisted saved-action source update, catalog reload, created-task exact-match resolution, confirm/result flow, launched Notepad cleanup, and saved-action source restoration
  - the helper is registered as `Workstream-scoped` in `Docs/validation_helper_registry.md`; Hardening or PR Readiness must decide whether to consolidate it with the Seam 2 tray helper into reusable tray/Create Custom Task validation support, promote it, or keep it explicitly workstream-scoped
- Seam 3 repo-side validation passed:
  - `dev/orin_saved_action_authoring_ui_validation.py`
  - the validation proves `CUSTOM_TASK_CREATE_ATTEMPT_STARTED`, `COMMAND_ACTION_CATALOG_RELOAD_COMPLETED`, `CUSTOM_TASK_CREATED`, created-record persistence, catalog inventory refresh, exact-match resolution, and normal launch-result flow through a fake launcher
- Seam 3 manual/live validation passed:
  - evidence root: `dev/logs/fb_038_tray_create_completion_live_validation/20260421_045536`
  - observed marker chain:
    - `RENDERER_MAIN|TRAY_CREATE_CUSTOM_TASK_REQUESTED|source=menu`
    - `RENDERER_MAIN|COMMAND_OVERLAY_OPENED|phase=entry|input_armed=true`
    - `RENDERER_MAIN|TRAY_CREATE_CUSTOM_TASK_ROUTED_TO_OVERLAY_ENTRY|source=menu|phase=entry`
    - `RENDERER_MAIN|OVERLAY_ENTRY_ACTION_TRIGGERED|action=create_custom_task`
    - `RENDERER_MAIN|OVERLAY_ENTRY_DIALOG_CREATED|action=create_custom_task`
    - `RENDERER_MAIN|CUSTOM_TASK_CREATE_ATTEMPT_STARTED`
    - `RENDERER_MAIN|COMMAND_ACTION_CATALOG_RELOAD_COMPLETED`
    - `RENDERER_MAIN|CUSTOM_TASK_CREATED`
    - `RENDERER_MAIN|COMMAND_CONFIRM_READY|action_id=fb038_seam3_live_notepad_20260421045536`
    - `RENDERER_MAIN|COMMAND_LAUNCH_REQUEST_SENT|action_id=fb038_seam3_live_notepad_20260421045536`
  - persisted record proof: `dev/logs/fb_038_tray_create_completion_live_validation/20260421_045536/created_record.json`
  - saved-action source proof:
    - `dev/logs/fb_038_tray_create_completion_live_validation/20260421_045536/saved_actions_after_create.json`
    - `dev/logs/fb_038_tray_create_completion_live_validation/20260421_045536/saved_actions_restored.json`
  - screenshots:
    - `dev/logs/fb_038_tray_create_completion_live_validation/20260421_045536/02_create_custom_task_dialog.png`
    - `dev/logs/fb_038_tray_create_completion_live_validation/20260421_045536/03_created_task_confirm.png`
    - `dev/logs/fb_038_tray_create_completion_live_validation/20260421_045536/04_created_task_result.png`
  - cleanup verification: launched Notepad process closed, runtime process stopped, and `saved_actions.json` restored to its original hash and length
  - continuation decision: Seam 3 is fully validated; Seam 4 may execute only as Workstream evidence and User Test Summary finalization.
- Seam 4 complete:
  `Workstream Evidence And User Test Summary Finalization`
- Consolidated Workstream evidence across:
  - Seam 1 `Minimal Tray Overlay Entry`
  - Seam 2 `Tray Create Custom Task Entry, Dialog-Open Only`
  - Seam 3 `Tray-Origin Create Completion And Catalog Re-Resolution`
- Updated this authority record so completed seams are marked green, evidence roots are current, no stale blocker remains, and Hardening is named only as the next legal phase.
- Finalized the canonical `## User Test Summary` for the completed FB-038 user-facing Workstream behavior.
- Refreshed the desktop convenience export at `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt` from this workstream-owned canonical summary.
- Recorded validation-helper registry drift:
  FB-038 currently carries workstream-scoped Seam 2 and Seam 3 helpers; this is acceptable for Workstream evidence, but the helper registry now requires a consolidation or promotion decision before PR Readiness.
- Workstream completion decision:
  COMPLETE for the approved same-risk seam chain.
- Remaining Workstream seams:
  none known inside the approved FB-038 scope.
- Continuation decision:
  stop Workstream execution and use a separate phase-transition durability pass before Hardening begins.

## User Test Summary

Seam 1 adds a user-visible tray entry into the existing command overlay path.
Seam 2 adds a tray menu `Create Custom Task` affordance that should open the existing Create Custom Task dialog without writing saved-action source state on open/cancel.
Seam 3 completes tray-origin Create Custom Task follow-through through the existing authoring path, proving create, persistence, catalog reload, created-task re-resolution, and confirm/result execution.

Current manual/live status:

- passed for Seam 1
- live startup and tray initialization markers are present
- real tray-shell activation produced the required tray activation and overlay-open markers
- existing hotkey overlay behavior still works through the released path
- normal shutdown hid the tray icon and left no runtime process behind
- no direct Create Custom Task routing exists yet
- Seam 2 route is implemented and repo-side Qt validators pass through `dev/orin_fb038_seam2_validation.ps1`
- Seam 2 manual/live tray readback passed at `dev/logs/fb_038_tray_create_live_validation/20260420_220847`
- Seam 2 is fully green
- Seam 3 repo-side and manual/live validation passed at `dev/logs/fb_038_tray_create_completion_live_validation/20260421_045536`
- Seam 3 is fully green
- Seam 4 Workstream evidence and User Test Summary finalization is complete
- the approved Workstream seam chain is complete and ready for a later Workstream-to-Hardening transition pass
- desktop export refreshed at `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt`

Completed user-facing behavior:

- the Nexus Desktop AI tray icon is available in a normal desktop session when the runtime starts
- tray `Open Command Overlay` opens the existing command overlay path without creating a second overlay path
- the existing overlay hotkey path still opens the same command overlay behavior
- tray `Create Custom Task` opens the existing command overlay entry path first, then opens the existing `Create Custom Task` dialog
- canceling or closing the tray-origin Create Custom Task dialog without submitting does not write `saved_actions.json` and does not create a saved action
- submitting a valid tray-origin custom task uses the existing FB-036 authoring path, persists exactly one saved-action record, reloads the catalog, and allows exact-match resolution of the created task without restart
- the created task uses the existing confirm/result execution flow
- validation restores temporary saved-action state after create-completion testing and closes launched apps and helper runtime processes

Manual validation checklist for `Minimal Tray Overlay Entry`:

- setup:
  launch Nexus Desktop AI from this branch in a normal Windows desktop session
- action:
  confirm a Nexus Desktop AI tray icon appears when the runtime starts
- expected:
  the app still reaches the normal passive desktop state and the existing overlay hotkeys continue to work
- action:
  activate the tray icon or choose `Open Command Overlay` from the tray entry
- expected:
  the existing command overlay opens or toggles using the same overlay surface as the hotkey path
- action:
  type a known built-in command such as `open calculator`
- expected:
  the existing confirm and result flow appears unchanged
- action:
  use `Esc` or normal overlay close behavior
- expected:
  the overlay returns to a clean entry/passive state without changing saved actions, built-ins, callable groups, or launcher behavior
- failure signs:
  no tray icon appears in a normal desktop session, tray activation does nothing, tray activation bypasses confirmation, hotkeys regress, saved-action behavior changes, or confirm/result copy changes unexpectedly

Manual validation checklist for `Tray Create Custom Task Entry, Dialog-Open Only`:

- setup:
  launch Nexus Desktop AI from this branch in a normal Windows desktop session with a clean saved-action source snapshot
- action:
  open the tray menu and choose `Create Custom Task`
- expected:
  the existing command overlay opens into entry state first, then the existing `Create Custom Task` dialog opens
- expected runtime marker chain:
  `TRAY_CREATE_CUSTOM_TASK_REQUESTED`, `COMMAND_OVERLAY_OPENED`, `TRAY_CREATE_CUSTOM_TASK_ROUTED_TO_OVERLAY_ENTRY`, `OVERLAY_ENTRY_ACTION_TRIGGERED|action=create_custom_task`, and `OVERLAY_ENTRY_DIALOG_CREATED|action=create_custom_task`
- action:
  cancel or close the dialog without submitting
- expected:
  no saved-action source file write occurs, no custom task is created, and the overlay returns to a stable entry/passive state
- action:
  use the existing `Open Command Overlay` tray action and the existing overlay hotkey
- expected:
  both still open the command overlay through their existing paths
- failure signs:
  the tray action opens a separate authoring path, bypasses overlay entry, writes the saved-action source on open/cancel, creates a custom task, duplicates the overlay, breaks the hotkey path, or changes confirm/result behavior

Manual validation checklist for `Tray-Origin Create Completion And Catalog Re-Resolution`:

- setup:
  launch Nexus Desktop AI from this branch in a normal Windows desktop session and snapshot `%LOCALAPPDATA%\Nexus Desktop AI\saved_actions.json`
- action:
  open the tray menu, choose `Create Custom Task`, fill a valid application task, and submit
- expected:
  the route opens the existing overlay entry path first, opens the existing `Create Custom Task` dialog, persists exactly one new saved-action record, and emits `CUSTOM_TASK_CREATE_ATTEMPT_STARTED`, `COMMAND_ACTION_CATALOG_RELOAD_COMPLETED`, and `CUSTOM_TASK_CREATED`
- action:
  run the created task phrase through the command overlay
- expected:
  the created task resolves by exact match, shows the existing confirm surface, executes through the existing result flow, and emits `COMMAND_CONFIRM_READY` plus `COMMAND_LAUNCH_REQUEST_SENT` for the created action id
- cleanup:
  close any launched app window and restore the saved-action source if the validation used a temporary test task
- failure signs:
  no saved-action record is written on submit, the catalog does not reload, the created phrase does not resolve, confirm/result behavior changes, a new authoring or resolution path appears, built-ins or existing saved actions regress, or the saved-action source cannot be restored after validation

The desktop `User Test Summary.txt` export was refreshed during Seam 4 because FB-038's user-facing Workstream seam chain is complete.
