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

- latest public prerelease: `v1.4.1-prebeta`
- latest public release commit: the `v1.4.1-prebeta` tag target
- latest public prerelease publication: `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.4.1-prebeta`
- latest public prerelease title: `Pre-Beta v1.4.1`
- merged unreleased non-doc implementation debt exists: yes
- the latest public released implementation milestone is FB-038 taskbar / tray quick-task UX and Create Custom Task surface in `v1.4.1-prebeta`
- current phase after FB-039 merge: `Release Readiness`
- phase status after FB-039 merge: `No Active Branch`
- blocker after release execution: none for FB-038
- current active workstream: none
- current branch after FB-039 merge: `No Active Branch`
- merged-unreleased release-debt owner: FB-039 External trigger and plugin integration architecture
- next concern: Release Readiness for FB-039 v1.5.0-prebeta after PR merge; FB-040 remains selected-only and Branch: Not created

That means the released FB-027 interaction baseline, the released FB-036 authoring-and-callable-group milestone, the released FB-041 deterministic callable-group execution milestone, the released FB-037 built-in catalog milestone, and the released FB-038 tray quick-task UX milestone are now part of the current public shared pre-Beta baseline.

## Current Release Debt Owner

### FB-039 External Trigger And Plugin Integration Architecture

- status: `merged unreleased`
- record state: `Promoted`
- branch before merge: `feature/fb-039-external-trigger-plugin-integration-architecture`
- canonical workstream doc: `Docs/workstreams/FB-039_external_trigger_plugin_integration_architecture.md`
- release readiness rule: Release Readiness remains analysis-only and consumes the inherited release target, scope, artifacts, and post-release truth below without file mutation.

Merged-Unreleased Release-Debt Owner: FB-039 External trigger and plugin integration architecture
Repo State: No Active Branch
Release Target: v1.5.0-prebeta
Release Floor: minor prerelease
Version Rationale: FB-039 creates the external trigger and plugin integration architecture lane with an internal trigger intake boundary, so it is a new pre-Beta capability lane rather than patch-only UX, sequencing, or governance repair.
Release Scope: Internal-only external trigger intake architecture and runtime boundary, including source map, ownership vocabulary, lifecycle/trust framing, in-memory registration, bounded invocation follow-through, lifecycle transitions, decision evidence, boundary snapshots, readiness inspection, readiness sweep, readiness summary, and readiness detail snapshot.
Release Artifacts: Tag v1.5.0-prebeta; release title Pre-Beta v1.5.0; release notes summarize the FB-039 internal-only trigger intake milestone, validation evidence, Live Validation waivers, and explicit non-includes.
Post-Release Truth: FB-039 becomes Released / Closed in v1.5.0-prebeta; release debt clears; repo remains No Active Branch until FB-040 Branch Readiness admission.
Selected Next Workstream: FB-040 Monitoring, thermals, and performance HUD surface
Next-Branch Creation Gate: FB-040 remains selected-only and Branch: Not created until FB-039 merge/release debt is resolved on updated main and Branch Readiness admits the next implementation branch.

## Current Active Workstream

None after FB-039 merge. The branch returns the repo to `No Active Branch` while FB-039 remains the merged-unreleased release-debt owner for `v1.5.0-prebeta`.

## Selected Next Workstream

### FB-040 Monitoring, Thermals, And Performance HUD Surface

- status: `Deferred`
- Record State: `Registry-only`
- Branch: Not created
- Selected Next Workstream: FB-040 Monitoring, thermals, and performance HUD surface
- Minimal Scope: Branch Readiness only after FB-039 merge/release debt is resolved on updated main; define source map, lifecycle ownership, validation contract, non-goals, and branch authority for monitoring, thermals, and performance HUD surfaces without implementation, telemetry plumbing, plugin/runtime integration, installer work, or branch creation before admission.

## Most Recent Released Workstream Context

### FB-038 Taskbar / Tray Quick-Task UX And Create Custom Task Surface

- status: `released`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.4.1-prebeta`
- release state: `released`
- release title: `Pre-Beta v1.4.1`
- canonical workstream doc: `Docs/workstreams/FB-038_taskbar_tray_quick_task_ux.md`
- sequencing note: released the tray quick-task UX milestone, including tray identity/discoverability, tray Open Command Overlay, tray Create Custom Task dialog-open/no-write route, tray-origin create completion through existing FB-036 authoring, catalog reload, exact-match resolution, confirm/result execution, and startup first-visible Core Visualization sequencing repair

## Prior Released Workstream Context

### FB-037 Curated Built-In System Actions And Nexus Settings Expansion

- status: `released`
- lane type: `implementation`
- release floor: `minor prerelease`
- target version: `v1.4.0-prebeta`
- release state: `released`
- canonical workstream doc: `Docs/workstreams/FB-037_built_in_actions_and_settings_expansion.md`
- sequencing note: released the curated built-in Windows utility catalog for Task Manager, Calculator, Notepad, and Paint while preserving saved-action override authority, authoring collision protection, confirm/result surfaces, and callable-group behavior

### FB-041 Deterministic Callable-Group Execution Layer

- status: `released`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.3.1-prebeta`
- release state: `released`
- canonical workstream doc: `Docs/workstreams/FB-041_deterministic_callable_group_execution_layer.md`
- sequencing note: released deterministic stored-order callable-group execution, stop-on-failure semantics, group-aware failure-path reuse, and confirm/result status alignment while preserving single-action behavior

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
- the released FB-037 built-in catalog milestone is now part of the locked current pre-Beta baseline
- the released FB-038 tray quick-task UX milestone is now part of the locked current pre-Beta baseline
- the released FB-035 lane is closed
- the recent released workstreams above remain part of the locked current baseline
- merged unreleased non-doc implementation debt exists: no
- FB-038 is released and closed in `v1.4.1-prebeta`; H1 identity/discoverability repair, H2 shortcut-launch tray readback validation, H3 window initialization sequencing, H4 post-fix startup visibility validation, fresh post-H4 technical/live validation, user-facing desktop shortcut validation, and UTS waiver digestion are preserved as historical evidence
- FB-039 is now active in Live Validation on `feature/fb-039-external-trigger-plugin-integration-architecture`
- FB-039 runtime/product implementation remains limited to the internal-only WS-6 intake skeleton, WS-7 in-memory registration and bounded invocation follow-through, WS-10 in-memory lifecycle state transitions, WS-13 in-memory decision evidence snapshots, WS-16 in-memory state snapshots, WS-19 read-only readiness inspection, WS-22 read-only registry readiness sweep, WS-25 read-only registry readiness summary, and WS-28 read-only registry readiness detail snapshot; WS-8, WS-11, WS-14, WS-17, WS-20, WS-23, WS-26, and WS-29 validation helper coverage plus WS-9, WS-12, WS-15, WS-18, WS-21, WS-24, WS-27, and WS-30 boundary reviews are durable; WS-31 records Workstream completion evaluation; H-1 through H-3 records Hardening pressure-test, validator tightening, and Hardening-green evaluation; LV-1 through LV-3 records Live Validation-green evaluation; LV-R1 through LV-R3 records corrected waiver handling with PR Readiness as the next legal phase
- post-release repo truth after the FB-038 release resolves to no FB-038 release-debt blocker
- successor-lane branch creation for FB-038 is historical; FB-038 is now merged and no longer an executable active implementation branch
- if a branch changes release-facing canon, those canon updates must land on that same branch before PR readiness is allowed
- escaped post-merge canon repair must ride a legal branch surface; `main` is protected and must not be patched directly by Codex
- the released FB-027 baseline does not authorize further saved-action authoring, resolution, voice, Action Studio, routines, profiles, hotkey cleanup, or shutdown-confirmation work by inertia
- remaining future candidate spaces now explicitly recorded in the backlog include:
  - FB-038 for taskbar or tray quick-task UX including Create Custom Task, now released and closed in `v1.4.1-prebeta` with H3/H4 startup visibility re-entry green, `User-Facing Shortcut Validation: PASS`, and UTS handling resolved by documented waiver
  - FB-039 for external trigger and plugin integration architecture, active in Live Validation on `feature/fb-039-external-trigger-plugin-integration-architecture`
  - FB-040 for monitoring, thermals, and performance HUD surfaces
- those candidate lanes must be selected deliberately rather than bundled together as one implicit interaction continuation
- FB-037 Branch Readiness does not imply automatic continuation into any remaining candidate lane

Use canonical workstream docs for execution detail.
Use the backlog for item identity.
