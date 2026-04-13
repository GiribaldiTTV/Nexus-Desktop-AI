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
- one merged unreleased non-doc implementation milestone currently exists on `main`
- the latest public released FB-027 milestone remains the first-class URL saved-action target release in `v1.2.8-prebeta`
- the current merged unreleased runtime delta on `main` is the later FB-027 saved-action inventory and guided-access follow-through
- no active non-doc implementation workstream is currently selected on `main`

That means `main` is not yet between released non-doc implementation lanes. The released FB-027 baseline-and-URL milestone still forms part of the current shared pre-Beta baseline, but `main` now also carries an additional unreleased FB-027 runtime milestone that should be handled through release prep or directly coupled truth repair before another unrelated implementation lane is selected.

## Current Merged Unreleased Implementation Context

### FB-027 Saved-Action Inventory And Guided Access

- status: `merged unreleased`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `TBD`
- release state: `merged unreleased`
- canonical workstream doc: `Docs/workstreams/FB-027_interaction_system_baseline.md`
- sequencing note: `main` now includes entry-state saved-action inventory, built-in-vs-saved distinction in choose and confirm, and source-health visibility plus guided access for missing, invalid, or colliding saved-action sources without changing exact-match resolution, state-machine boundedness, or baseline input-capture behavior
- merged-path note: the branch that carried this runtime milestone also carried directly coupled future-lane planning material, but the release-driving runtime delta is the inventory and guided-access milestone itself

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

- the released FB-027 baseline-and-URL milestone is now part of the current locked interaction baseline
- `main` also contains a later merged unreleased FB-027 inventory-and-guided-access milestone above that released baseline
- the released FB-035 lane is closed
- the recent released workstreams above remain part of the locked current baseline
- merged unreleased non-doc implementation debt currently exists on `main`
- the correct next move is release prep or directly coupled truth repair, not another unrelated implementation lane
- neither the released FB-027 milestone nor the merged unreleased inventory-and-guided-access follow-through authorizes further saved-action authoring, resolution, voice, Action Studio, routines, profiles, hotkey cleanup, or shutdown-confirmation work by inertia
- future candidate spaces now explicitly recorded in the backlog include:
  - FB-036 for limited saved-action authoring and type-first custom task UX
  - FB-037 for curated built-in system actions and Nexus settings expansion
  - FB-038 for taskbar or tray quick-task UX including Create Custom Task
  - FB-039 for external trigger and plugin integration architecture
  - FB-040 for monitoring, thermals, and performance HUD surfaces
- those candidate lanes must be selected deliberately rather than bundled together as one implicit interaction continuation

Use canonical workstream docs for execution detail.
Use the backlog for item identity.
