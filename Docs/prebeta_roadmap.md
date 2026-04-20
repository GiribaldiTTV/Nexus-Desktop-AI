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
- `Docs/phase_governance.md`
- `Docs/codex_modes.md`
- `Docs/feature_backlog.md`
- `Docs/workstreams/index.md`
- `Docs/closeout_guidance.md`

That means:

- backlog owns identity
- workstream docs own promoted-work feature-state, branch-local evidence, and closure records
- phase governance owns repo-wide lifecycle, proof, timeout, and stop-loss rules
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

- latest public prerelease: `v1.3.1-prebeta`
- latest public release commit: `f743281`
- merged unreleased non-doc implementation debt exists after this branch merges: FB-037 curated built-in system actions and Nexus settings expansion
- the latest public released implementation milestone is FB-041 deterministic callable-group execution layer in `v1.3.1-prebeta`
- current phase after this branch merges: `Release Readiness`
- phase status after this branch merges: `No Active Branch`
- blocker after this branch merges: `Release Debt` (FB-037)
- next concern after this branch merges: release packaging for FB-037

That means the released FB-027 interaction baseline, the released FB-036 authoring-and-callable-group milestone, and the released FB-041 deterministic callable-group execution milestone are now part of the current public shared pre-Beta baseline.

## Current Release Debt Owner

### FB-037 Curated Built-In System Actions And Nexus Settings Expansion

- status: `merged unreleased`
- lane type: `implementation`
- release floor: `minor prerelease`
- target version: `TBD`
- release state: `merged unreleased`
- current phase after merge: `Release Readiness`
- phase status after merge: `No Active Branch`
- blocker after merge: `Release Debt` (FB-037)
- next concern after merge: release packaging
- canonical workstream doc: `Docs/workstreams/FB-037_built_in_actions_and_settings_expansion.md`
- sequencing note: Workstream same-risk built-in catalog seams remain complete; helper-only Hardening cleared the reusable-helper cleanup no-progress and missing-manifest gap; Live Validation then passed with manifest-backed evidence across built-in execution, saved-action override, authoring collision rejection, mixed environments, and repeated execution; successor-lane lock is waived because post-merge truth resolves to `No Active Branch` due to FB-037 release debt

## Selected Next Workstream

### FB-038 Taskbar / Tray Quick-Task UX And Create Custom Task Surface

- selection state: `selected next workstream`
- Record State: `Registry-only`
- Branch: Not created
- sequence: after FB-037 release packaging clears `Release Debt`
- Minimal Scope: Branch Readiness admission and planning for the shell-facing quick-task entry surface, initially limited to defining the smallest safe taskbar/tray or Create Custom Task UX seam above the released FB-027 interaction baseline, FB-036 authoring baseline, FB-041 callable-group execution baseline, and FB-037 built-in catalog baseline.
- branch creation rule: defer branch creation to `Branch Readiness` after FB-037 release debt is cleared and updated `main` is revalidated

## Most Recent Released Workstream Context

### FB-041 Deterministic Callable-Group Execution Layer

- status: `released`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.3.1-prebeta`
- release state: `released`
- canonical workstream doc: `Docs/workstreams/FB-041_deterministic_callable_group_execution_layer.md`
- sequencing note: released deterministic stored-order callable-group execution, stop-on-failure semantics, group-aware failure-path reuse, and confirm/result status alignment while preserving single-action behavior

## Prior Released Workstream Context

### FB-036 Saved-Action Authoring And Callable Groups

- status: `released`
- lane type: `implementation`
- release floor: `minor prerelease`
- target version: `v1.3.0-prebeta`
- release state: `released`
- canonical workstream doc: `Docs/workstreams/FB-036_saved_action_authoring.md`
- sequencing note: released bounded custom-task authoring, callable groups, inline group quick-create, explicit trigger modeling, and the final exact-green authoring hardening without changing the locked typed-first overlay contract or widening into Action Studio behavior

## Recently Closed Workstreams

### FB-027 Interaction System Baseline

- status: `closed`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.2.9-prebeta`
- release state: `released`
- canonical workstream doc: `Docs/workstreams/FB-027_interaction_system_baseline.md`
- sequencing note: remains the locked interaction baseline below the later released FB-036 authoring and callable-group milestone

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

- the released FB-027 baseline remains part of the locked current interaction floor
- the released FB-036 authoring-and-callable-group milestone is now part of the locked current pre-Beta baseline
- the released FB-041 deterministic callable-group execution milestone is now part of the locked current pre-Beta baseline
- the released FB-035 lane is closed
- the recent released workstreams above remain part of the locked current baseline
- merged unreleased non-doc implementation debt exists after this branch merges: FB-037
- no active implementation workstream remains selected after this branch merges
- post-merge repo truth resolves to `Release Readiness` with phase status `No Active Branch` and blocker `Release Debt` (FB-037)
- successor-lane lock is waived for this PR Readiness pass because release debt blocks next implementation admission
- if a branch changes release-facing canon, those canon updates must land on that same branch before PR readiness is allowed
- post-release canon repair is emergency-only when merged canon is already stale or external drift made pre-merge prevention impossible
- the released FB-027 baseline does not authorize further saved-action authoring, resolution, voice, Action Studio, routines, profiles, hotkey cleanup, or shutdown-confirmation work by inertia
- remaining future candidate spaces now explicitly recorded in the backlog include:
  - FB-038 for taskbar or tray quick-task UX including Create Custom Task, selected as the next implementation workstream after FB-037 release packaging clears release debt
  - FB-039 for external trigger and plugin integration architecture
  - FB-040 for monitoring, thermals, and performance HUD surfaces
- those candidate lanes must be selected deliberately rather than bundled together as one implicit interaction continuation
- FB-037 Branch Readiness does not imply automatic continuation into any remaining candidate lane

Use canonical workstream docs for execution detail.
Use the backlog for item identity.
