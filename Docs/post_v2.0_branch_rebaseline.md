# Jarvis Post-v2.0 Branch Rebaseline

## Purpose

This document records the implemented branch truth for the current post-`v2.0` workstream without treating that work as a version closeout.

It exists to:

- capture the implemented reality of the active `feature/v2.1.0-planning` branch
- keep future prompts from relying on stale backlog wording alone
- preserve the historical accuracy of `docs/v2.0_closeout.md`
- separate implemented branch truth from still-deferred follow-up work

This is an interim rebaseline doc, not a closeout doc.

## Branch Context

Current branch truth for this rebaseline:

- branch: `feature/v2.1.0-planning`
- boundary start: `10cd024`
- current `HEAD`: `e14cd53`

When this document conflicts with stale backlog wording from the same workstream, actual code plus commit history is the higher-priority truth.

The current architectural boundaries still in force are:

- `main.py` remains the dev-only Boot Jarvis harness
- `launch_jarvis_desktop.vbs` remains the normal manual user launch
- the controlled desktop path remains:
  - `desktop/jarvis_desktop_launcher.pyw`
  - `desktop/jarvis_desktop_main.py`

## Implemented Workstream Truth

### Boot Harness And Transition Surfaces

The dev-only Boot Jarvis harness now includes a real Phase 1 seam layer in `main.py`:

- `--boot-profile manual|auto_handoff_skip_import`
- `--audio-mode voice|quiet`
- dedicated boot evidence roots under `dev/logs`
- structured `BOOT_MAIN|...` milestones
- quiet/no-audio behavior inside `main.py`
- auto-drive for the existing `engage hud -> no` prompt chain

The branch also added dev-only hidden-window boot launchers under `dev/launchers` for:

- manual quiet
- manual voice
- auto-handoff skip-import quiet
- auto-handoff skip-import voice

Boot-to-desktop handoff behavior was then tightened inside `main.py` so the current transition reads as one continuous Jarvis-controlled flow rather than a visible overlap or a distinct fade-out/fade-in swap.

The later `FB-024` follow-through then closed the remaining narrow boot unhappy-path blind spots in `main.py` by adding explicit markers for:

- rejected first-command input
- rejected import yes/no input
- typed shutdown accepted from command stage 1 or 2
- hotkey-triggered shutdown
- handoff signal emitted versus dropped

### Desktop Renderer Observability And Attach Follow-Through

The controlled desktop path now has renderer-side runtime evidence for:

- visual page ready versus load failed
- desktop mode enable begin
- desktop attach result
- renderer shutdown begin

Those markers exposed a real desktop attach problem on this machine.
The branch then added:

- WorkerW discovery probe evidence
- a guarded `Progman` fallback when the confirmed shell shape is:
  - `Progman`
  - direct `SHELLDLL_DefView`
  - no next WorkerW sibling

That means the current desktop attach path is no longer failing only because the old WorkerW host-selection assumption was wrong on this machine.

### Single-Instance Relaunch Model

Single-instance behavior is now a cooperative relaunch flow rather than a dead-end block.

That flow now includes:

- relaunch-request signaling between instances
- clean shutdown handling in Boot Jarvis, Desktop Jarvis, and the Dev Toolkit
- a Jarvis-owned relaunch prompt
- topmost/focus-stealing prompt behavior
- surface-specific prompt copy for Boot Jarvis, Desktop Jarvis, and the Dev Toolkit
- decision-level logging for accept, decline, signal-sent, and wait outcomes

### Dev Toolkit Expansion

The Dev Toolkit is now a materially broader internal validation surface than the one described in `v2.0_closeout.md`.

Implemented additions in this branch include:

- `Boot & Transition Checks` Toolkit surfacing
- Dev Toolkit session runtime logging under `dev/logs/dev_toolkit_session`
- boot monitor preflight
- boot-to-desktop handoff verification
- boot transition capture
- boot-helper Toolkit validation
- desktop-helper Toolkit validation
- top-level Dev Toolkit smoke validation
- live background-lane status and progress reporting
- latest smoke-report and latest transition-capture utilities

These additions build on the delivered `v2.0` Toolkit foundation rather than replacing its split-utility and per-run-history model.

## Current Evidence Roots Added Or Expanded

Key branch-era dev evidence roots now include:

- `dev/logs/boot_manual_flow`
- `dev/logs/boot_auto_handoff_skip_import`
- `dev/logs/boot_monitor_preflight`
- `dev/logs/boot_transition_verification`
- `dev/logs/boot_transition_capture`
- `dev/logs/boot_toolkit_validation`
- `dev/logs/desktop_toolkit_validation`
- `dev/logs/dev_toolkit_session`
- `dev/logs/dev_toolkit_smoke_validation`

## Current Guarantees

The following truths remain in force after this branch work:

- `main.py` remains dev-only and root-owned
- `launch_jarvis_desktop.vbs` remains the normal manual user launch path
- the controlled desktop path is still launcher-owned through `desktop/jarvis_desktop_launcher.pyw` and `desktop/jarvis_desktop_main.py`
- `docs/v2.0_closeout.md` remains historical closeout truth for `v2.0`
- `docs/boot_access_design.md` remains the active boot-planning canon
- `docs/workspace_layout_plan.md` remains the active workspace-planning canon

## Still Deferred After This Rebaseline

This branch does not close out all later work.

The following remain deferred:

- broader boot-orchestrator implementation beyond the dev-only harness
- later boot/desktop milestone taxonomy clarification
- a dedicated Dev Toolkit uploaded-bundle intake surface
- any full `v2.1` closeout-style version document

## Doc Sync Implication

The current doc-sync consequence of this branch is that backlog truth should now show `FB-021` through `FB-024` as implemented while keeping `FB-025` and `FB-026` deferred.

This rebaseline doc should be used when a task depends on implemented post-`v2.0` branch truth before any later version closeout exists.
