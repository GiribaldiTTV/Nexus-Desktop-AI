# Jarvis Workspace Layout Plan

## Purpose

This document defines the first planning pass for `FB-005`.

`rev1a` is planning-only.
It does not move files, rewrite imports, or change runtime behavior.

Its job is to:

- inventory the current workspace at a practical level
- define the target folder ownership model
- identify path-sensitive files that require controlled migration
- define a safe migration order for later approved implementation passes

## Current Workspace Inventory

### Repo Root

Current repo-root items with planning significance:

- `main.py`
- `jarvis_desktop_main.py`
- `jarvis_desktop_test.py`
- `jarvis_voice.py`
- `launch_jarvis_desktop.vbs`
- `dev/`
- `Audio/`
- `desktop/`
- `Docs/` / `docs/` references
- `jarvis_visual/`
- `logs/`

Repo metadata and environment artifacts that should remain root-owned:

- `.git/`
- `.gitattributes`
- `.gitignore`
- root `__pycache__/`

### Current Major Folder Ownership

`desktop/`

- launcher runtime and recovery control
- diagnostics UI
- desktop renderer support
- desktop support-reporting helpers
- harness tooling tied to desktop/runtime validation

`dev/`

- developer-only launchers
- deterministic manual-test renderer targets
- contained manual validation entry points that should not be treated as Windows-facing production shims

`Audio/`

- failure and shutdown voice runtime path
- audio-effect implementation for diagnostics and shutdown speech

`jarvis_visual/`

- HTML, CSS, and JS assets used by the current visual experience surfaces

`docs/`

- source-of-truth project docs
- version closeouts
- planning and task guidance

`logs/`

- generated runtime logs
- generated crash reports
- generated verification artifacts
- generated historical-memory storage

## Canonical Target Layout

### What Should Remain At Repo Root

Repo root should stay limited to:

- repo metadata and ignore files
- top-level Windows-facing launch shims
- top-level experience entrypoints that still belong to paused boot or top-level experience work
- temporary compatibility wrappers during later migration passes only if needed

For now, these should remain root-owned:

- `launch_jarvis_desktop.vbs`
- `main.py`

Developer-only launchers should not remain root-owned.
They should live under `dev/launchers/`.

### What Should Belong Under Domain Folders

`desktop/`

- desktop launcher
- desktop diagnostics
- desktop renderer support
- desktop-specific helpers
- desktop entrypoints later, after a controlled migration pass
- runtime harness helpers that are part of production-adjacent launcher behavior

`dev/`

- manual test launchers
- deterministic manual renderer targets
- developer-only helper surfaces for contained validation

Later move candidates into `desktop/`:

- `jarvis_desktop_main.py`
- `jarvis_desktop_test.py`

`audio/`

- voice and audio-effect implementation files

Later move candidates into `audio/`:

- current `Audio/jarvis_error_voice.py`
- `jarvis_voice.py`

`jarvis_visual/`

- current visual assets for the Jarvis interface layer

This folder already has coherent ownership and can remain a dedicated visual-assets domain.

`docs/`

- all source-of-truth docs
- planning docs
- version closeouts

`logs/`

- generated state only
- never a source-code ownership area

## Canonical Folder Naming

Use lowercase canonical folder names for core repo domains:

- `dev`
- `audio`
- `desktop`
- `docs`
- `logs`

For current visual assets, keep the descriptive domain name:

- `jarvis_visual`

Known current naming inconsistency:

- root inventory currently presents `Docs` while project references consistently use `docs`
- root inventory currently presents `Audio` with uppercase casing

Case normalization should be handled in a dedicated later move pass because case-only renames can be git-sensitive on Windows.

## Path-Sensitive Inventory

These files are sensitive enough that they must be migrated in a controlled order:

`launch_jarvis_desktop.vbs`

- Windows-facing launch shim
- hardcodes the launcher path under `desktop/`

`desktop/jarvis_desktop_launcher.pyw`

- derives `ROOT_DIR`
- assumes `jarvis_desktop_main.py` lives at repo root
- assumes `logs/` lives under repo root
- assumes `Audio/jarvis_error_voice.py` lives under repo root
- launches sibling diagnostics script from `desktop/`

`jarvis_desktop_main.py`

- root entrypoint
- imports `desktop.*`
- resolves visual assets from `jarvis_visual/` relative to repo root

`jarvis_desktop_test.py`

- same path pattern as `jarvis_desktop_main.py`
- should migrate in step with the desktop entrypoint layout, not separately

`main.py`

- top-level experience entrypoint
- imports `jarvis_voice.py`
- resolves visual assets from `jarvis_visual/`
- should be treated as coupled to paused top-level experience and boot-adjacent work

`jarvis_voice.py`

- root-level voice helper
- currently coupled to `main.py`
- should not be moved independently from `main.py` without an approved paired pass

`Audio/jarvis_error_voice.py`

- current failure and shutdown voice script
- path is referenced directly by the launcher

`dev/launchers/*.vbs`

- developer-only Windows launch shims
- should remain separate from the root Windows-facing production launcher surface

`dev/targets/*.pyw`

- deterministic manual launcher-path test targets
- safe to move independently from production runtime code because they are only selected through harness env overrides

## Generated And Runtime State

These areas are generated state and should not be reorganized first:

- `logs/`
- `logs/crash/`
- harness and verification subfolders under `logs/`
- `jarvis_history_v1.jsonl`
- all `__pycache__/` directories

Generated state should be classified and documented, but excluded from the first move pass.

## Migration Order

### Step 1

Planning only.

- approve this layout and ownership model
- confirm canonical folder naming
- confirm which root files are intentionally deferred

### Step 2

Low-risk naming and documentation alignment only.

- normalize documentation references to canonical folder names
- handle `Docs` / `docs` and `Audio` / `audio` casing only in a dedicated approved pass

### Step 3

Desktop entrypoint consolidation.

- move `jarvis_desktop_main.py` into the `desktop/` domain
- move `jarvis_desktop_test.py` with it
- update the launcher's target-script assumption in the same approved pass

This should be the first real code-moving pass because it addresses the clearest root-level ownership leak without crossing into paused boot work.

### Step 4

Audio-domain consolidation.

- move root-level `jarvis_voice.py` only in a pass that also updates `main.py`
- normalize `Audio/` naming in the same approved pass if selected

### Step 5

Defer top-level experience entrypoint work until later.

- keep `main.py` root-owned until the paused boot or top-level experience track is explicitly resumed
- keep `launch_jarvis_desktop.vbs` root-owned as the Windows-facing shim unless a dedicated entrypoint pass is approved

## Areas Explicitly Deferred From The First Implementation Move Pass

- `main.py`
- `launch_jarvis_desktop.vbs`
- `logs/`
- generated verification artifacts
- broader visual-asset reorganization
- boot-adjacent top-level experience restructuring

## Rev1a Non-Goals

`rev1a` does not:

- move files
- rename folders
- rewrite imports
- rewrite launcher paths
- change behavior
- redesign orchestration
- reopen boot planning

## Risks And Blockers

- case-only folder renames may be unreliable without a controlled git-aware pass on Windows
- `launch_jarvis_desktop.vbs` hardcodes a root-to-desktop path
- `desktop/jarvis_desktop_launcher.pyw` assumes root-owned renderer and audio paths
- `main.py` and `jarvis_voice.py` are coupled and should not be split casually
- generated `logs/` content should not be mixed into source-layout refactors

## Recommended First Implementation Move Pass After Rev1a

If `FB-005` proceeds beyond planning, the safest first implementation move pass should be:

- desktop-entrypoint consolidation only

That means:

- move `jarvis_desktop_main.py`
- move `jarvis_desktop_test.py`
- update the launcher path assumptions in the same approved pass

This is smaller and safer than starting with a broad repo rewrite.
