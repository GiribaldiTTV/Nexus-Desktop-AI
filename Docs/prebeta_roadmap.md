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

- latest public prerelease: `v1.2.9-prebeta`
- latest public release commit: `1bdf7a0`
- no merged unreleased non-doc implementation debt currently exists on `main`
- the latest public released FB-027 milestone is the saved-action inventory and guided-access release in `v1.2.9-prebeta`
- no active non-doc implementation workstream is currently selected on `main`

That means `main` is again between released non-doc implementation lanes. The released FB-027 baseline, URL-target milestone, and later inventory-and-guided-access follow-through now form part of the current shared pre-Beta baseline, and the next implementation workstream should be chosen only after fresh post-release analysis on updated `main`.

## Most Recent Released Workstream Context

### FB-027 Interaction System Baseline

- status: `released`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.2.9-prebeta`
- release state: `released`
- canonical workstream doc: `Docs/workstreams/FB-027_interaction_system_baseline.md`
- sequencing note: released the locked typed-first baseline, first-class URL saved-action targets, and the later saved-action inventory and guided-access follow-through without changing exact-match resolution, state-machine boundedness, or input-capture behavior

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

- the released FB-027 baseline now includes both the earlier URL-target milestone and the later inventory-and-guided-access follow-through
- the released FB-035 lane is closed
- the recent released workstreams above remain part of the locked current baseline
- no merged unreleased non-doc implementation debt currently exists on `main`
- the next implementation workstream should be chosen only after fresh post-release analysis on updated `main`
- if post-release canon drift is found and a plausible next workstream can already be selected safely, the repair should normally happen at the start of that next workstream branch rather than as a standalone docs-only lane
- standalone docs-only post-release repair is exception-only when no plausible next workstream can yet be selected safely from current truth
- the released FB-027 baseline does not authorize further saved-action authoring, resolution, voice, Action Studio, routines, profiles, hotkey cleanup, or shutdown-confirmation work by inertia
- future candidate spaces now explicitly recorded in the backlog include:
  - FB-036 for limited saved-action authoring and type-first custom task UX
  - FB-037 for curated built-in system actions and Nexus settings expansion
  - FB-038 for taskbar or tray quick-task UX including Create Custom Task
  - FB-039 for external trigger and plugin integration architecture
  - FB-040 for monitoring, thermals, and performance HUD surfaces
- those candidate lanes must be selected deliberately rather than bundled together as one implicit interaction continuation

Use canonical workstream docs for execution detail.
Use the backlog for item identity.
