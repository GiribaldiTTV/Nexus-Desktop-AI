# Nexus Workspace Layout Plan

## Purpose

This document defines workspace-layout planning and ownership boundaries for the current repo.

It is a planning and reference surface.
It does not own:

- backlog identity
- roadmap sequencing
- workstream execution history

## Current Workspace Reality

Current repo-root items with planning significance include:

- `main.py`
- `launch_orin_desktop.vbs`
- `dev/`
- `Audio/`
- `desktop/`
- `Docs/`
- `jarvis_visual/`
- `logs/`

Current merged desktop runtime path is:

`launch_orin_desktop.vbs`
-> `desktop/orin_desktop_launcher.pyw`
-> `desktop/orin_desktop_main.py`

Current desktop test entrypoint is:

- `dev/desktop/orin_desktop_test.py`

Current audio runtime surfaces are:

- `Audio/orin_voice.py`
- `Audio/orin_error_voice.py`

Current visual assets remain under:

- `jarvis_visual/`

Historical note:

- older Jarvis-named move history remains historical context only
- current repo truth for the desktop and audio surfaces is ORIN-named as listed above

## Current Major Folder Ownership

`desktop/`

- launcher runtime and recovery control
- diagnostics UI
- desktop entrypoints
- desktop renderer support
- desktop support-reporting helpers

`dev/`

- developer launchers
- developer desktop harnesses
- deterministic targets
- validation helpers and toolkit-oriented support

`Audio/`

- voice and audio-effect implementation

`jarvis_visual/`

- current visual assets used by the desktop surfaces

`Docs/`

- source-of-truth and planning documentation

`logs/`

- generated runtime, crash, and validation state only

## Root Ownership Boundary

Repo root should stay limited to:

- repo metadata and environment files
- top-level Windows-facing launch shims
- top-level experience entrypoints still tied to paused boot or top-level experience work

Current root-owned planning-significant surfaces are:

- `launch_orin_desktop.vbs`
- `main.py`

That does not mean all future entrypoints should remain root-owned forever.
It means current merged truth still keeps those surfaces at root.

## Domain Ownership Model

`desktop/` should remain the home for:

- launcher-owned desktop execution
- renderer entrypoints
- desktop helpers and diagnostics surfaces

`dev/` should remain the home for:

- developer launchers
- contained validation surfaces
- deterministic targets and helper scripts

`Audio/` remains the current home for the voice layer.

`jarvis_visual/` remains the current visual-asset home until a later explicitly chosen visual-layout change says otherwise.

## Naming And Path Normalization

Current merged truth includes mixed historical naming:

- product framing is Nexus Desktop AI / ORIN
- some folder and artifact names remain older names for compatibility or historical continuity

Examples of still-current names:

- `Audio/`
- `jarvis_visual/`
- `%LOCALAPPDATA%/Nexus Desktop AI/state/jarvis_history_v1.jsonl`
- `C:/Jarvis/logs`

Those names should be treated as current runtime or repo truth where they still exist, not automatically rewritten in planning docs.

## Path-Sensitive Planning Boundary

Path-sensitive surfaces still require deliberate handling when future layout work resumes.

Examples include:

- `launch_orin_desktop.vbs`
- `main.py`
- `desktop/orin_desktop_launcher.pyw`
- `desktop/orin_desktop_main.py`
- `dev/desktop/orin_desktop_test.py`
- `Audio/orin_voice.py`
- `Audio/orin_error_voice.py`
- `jarvis_visual/`

Future layout work should continue to treat those as controlled surfaces rather than casual rename targets.

## Deferred Layout Work

The following remain planning-level or deferred topics:

- top-level experience entrypoint reshaping around `main.py`
- any future root-to-domain ownership changes for boot-facing entry surfaces
- case normalization such as `Audio` versus `audio`
- broader visual-asset reorganization
- generated-state reorganization under `logs/`

## Relationship To Other Canon Layers

- use `Docs/architecture.md` for system boundaries
- use `Docs/orchestration.md` for launcher and renderer ownership
- use `Docs/boot_access_design.md` for future boot-layer planning
- use `Docs/feature_backlog.md` for tracked layout-related identity
- use `Docs/prebeta_roadmap.md` for sequencing
