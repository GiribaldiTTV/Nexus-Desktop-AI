# Nexus Pre-Beta Roadmap

## Purpose

This document is the sequencing and release-posture layer for current Nexus `pre-Beta` planning.

Use it for:

- latest public prerelease truth
- release-debt posture
- current sequencing posture
- recently closed milestone context

Do not use it as:

- a second backlog
- a workstream execution diary
- a substitute for canonical workstream records

## Authority And Boundaries

This roadmap is subordinate to:

- `Docs/development_rules.md`
- `Docs/codex_modes.md`
- `Docs/feature_backlog.md`
- `Docs/workstreams/index.md`
- `Docs/closeout_guidance.md`

That means:

- backlog owns identity
- workstream docs own promoted-work execution and closure truth
- closeouts and rebaselines own epoch summaries
- roadmap owns sequencing and release posture only

## Lane Types And Release Fields

Use these lane types:

- `docs-only`
- `implementation`
- `rebaseline`

Use these release-floor values:

- `no release`
- `patch prerelease`
- `minor prerelease`

Use these release-state values when relevant:

- `active delta`
- `merged unreleased`
- `released`
- `closed`

## Current Release Posture

Current merged truth indicates:

- latest public prerelease: `v1.2.8-prebeta`
- latest public release commit: `4816aac`
- no merged unreleased non-doc implementation debt currently exists on `main`
- the most recent released implementation milestone is FB-027 for first-class URL saved-action targets
- no active non-doc implementation workstream is currently selected on `main`

That means `main` is again between released non-doc implementation lanes. The released FB-027 baseline-and-URL milestone now forms part of the current shared pre-Beta baseline, and the next workstream should be chosen from refreshed post-release truth rather than by continuing released work by inertia.

## Most Recent Released Workstream Context

### FB-027 Interaction System Baseline

- status: `released`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.2.8-prebeta`
- release state: `released`
- canonical workstream doc: `Docs/workstreams/FB-027_interaction_system_baseline.md`
- sequencing note: released the locked typed-first baseline plus first-class URL saved-action targets without changing exact-match resolution, state-machine boundedness, or input-capture behavior

## Recently Closed Workstreams

### FB-035 Release-Context Fallback Hardening

- status: `closed`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.2.7-prebeta`
- release state: `released`
- canonical workstream doc: `Docs/workstreams/FB-035_release_context_fallback_hardening.md`
- sequencing note: closed the support-report release-context hardening milestone and established the current release-context baseline

### FB-034 Recoverable Diagnostics

- status: `closed`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.2.6-prebeta`
- release state: `released`
- canonical workstream doc: `Docs/workstreams/FB-034_recoverable_diagnostics.md`
- sequencing note: remains a closed recoverable-diagnostics milestone, not an automatically active continuation lane

### FB-025 Boot/Desktop Taxonomy Clarification

- status: `closed`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.2.5-prebeta`
- release state: `released`
- canonical workstream doc: `Docs/workstreams/FB-025_boot_desktop_milestone_taxonomy_clarification.md`

### FB-033 Startup Snapshot Harness Follow-Through

- status: `closed`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.2.4-prebeta`
- release state: `released`
- canonical workstream doc: `Docs/workstreams/FB-033_startup_snapshot_harness_follow_through.md`

### FB-028 History State Relocation

- status: `closed`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.2.3-prebeta`
- release state: `released`
- canonical workstream doc: `Docs/workstreams/FB-028_history_state_relocation.md`

## Current Sequencing Reading

Current merged truth indicates:

- the released FB-027 lane is now part of the current locked interaction baseline
- the released FB-035 lane is closed
- the recent released workstreams above remain part of the locked current baseline
- no merged unreleased non-doc implementation debt currently exists on `main`
- the next implementation workstream should be chosen only after fresh post-release analysis on updated `main`
- the released FB-027 milestone does not authorize further saved-action, resolution, voice, Action Studio, routines, profiles, hotkey cleanup, or shutdown-confirmation work by inertia
- future candidate spaces now explicitly recorded in the backlog include:
  - FB-036 for limited saved-action authoring and type-first custom task UX
  - FB-037 for curated built-in system actions and Nexus settings expansion
  - FB-038 for taskbar or tray quick-task UX including Create Custom Task
  - FB-039 for external trigger and plugin integration architecture
  - FB-040 for monitoring, thermals, and performance HUD surfaces
- those candidate lanes must be selected deliberately rather than bundled together as one implicit interaction continuation

Use canonical workstream docs for execution detail.
Use the backlog for item identity.
