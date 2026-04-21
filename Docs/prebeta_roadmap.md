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

- latest public prerelease: `v1.4.0-prebeta`
- latest public release commit: the `v1.4.0-prebeta` tag target
- latest public prerelease publication: `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.4.0-prebeta`
- merged unreleased non-doc implementation debt exists: yes
- the latest public released implementation milestone is FB-037 curated built-in system actions and Nexus settings expansion in `v1.4.0-prebeta`
- current phase: `Release Readiness`
- phase status: `No Active Branch`
- blocker after release execution: none for FB-037
- current active workstream: none
- current branch: `No Active Branch`
- merged-unreleased release-debt owner: FB-038 Taskbar / Tray Quick-Task UX And Create Custom Task Surface
- next concern: Release Readiness may validate the inherited FB-038 release target, scope, artifacts, and post-release truth without mutating repository files

That means the released FB-027 interaction baseline, the released FB-036 authoring-and-callable-group milestone, the released FB-041 deterministic callable-group execution milestone, and the released FB-037 built-in catalog milestone are now part of the current public shared pre-Beta baseline.

## Current Release Debt Owner

### FB-038 Taskbar / Tray Quick-Task UX And Create Custom Task Surface

Status: `Merged Unreleased (Release Debt)`
canonical workstream doc: `Docs/workstreams/FB-038_taskbar_tray_quick_task_ux.md`
Merged-Unreleased Release-Debt Owner: FB-038
Repo State: No Active Branch
Release Target: v1.4.1-prebeta
Release Floor: patch prerelease
Version Rationale: FB-038 is tray UX, startup sequencing fix, and governance repair follow-through; it does not open a new feature lane or capability expansion beyond the completed tray/task UX milestone.
Release Scope: FB-038 tray/task UX milestone only: tray identity/discoverability, tray Open Command Overlay, tray Create Custom Task dialog-open/no-write route, tray-origin create completion through existing FB-036 authoring, catalog reload, exact-match resolution, confirm/result execution, and startup first-visible Core Visualization repair.
Release Artifacts: tag `v1.4.1-prebeta`; release title `Nexus Desktop AI v1.4.1-prebeta - Tray Quick-Task UX`; release notes summarizing FB-038 user-facing tray/task UX, validation evidence, and retained FB-038 evidence helpers.
Post-Release Truth: after release, FB-038 should be represented as `Released (v1.4.1-prebeta)` / `Closed`; release debt clears; the latest public prerelease advances from `v1.4.0-prebeta` to `v1.4.1-prebeta`.
Selected Next Workstream: FB-039 External Trigger And Plugin Integration Architecture.
Next-Branch Creation Gate: FB-039 remains selected-only and `Branch: Not created` until FB-038 release debt is cleared and updated `main` passes the repo-level admission gate.

## Current Active Workstream

### None

- repo state: `No Active Branch`
- blocker: `Release Debt`
- current owner: FB-038 is merged-unreleased release debt, not an active implementation branch
- release readiness rule: Release Readiness is analysis-only and may consume inherited FB-038 release target/scope/artifacts; any required file mutation must be repaired on a legal branch surface, not on `main` and not inside Release Readiness

## Selected Next Workstream

### FB-039 External Trigger And Plugin Integration Architecture

- Record State: `Registry-only`
- Minimal Scope: Branch Readiness only for external trigger and plugin integration architecture; define the source map, lifecycle ownership, trust/safety boundaries, validation contract, and explicit non-goals for external trigger surfaces such as Stream Deck or other installed integration points before any implementation. No plugin runtime implementation, Stream Deck integration, protocol handling, installer work, settings surface, taskbar/tray expansion, monitoring HUD work, or release packaging is admitted during Branch Readiness.
- Branch: Not created
- Selection Basis: FB-039 is the nearest canon successor after FB-038 because it plans external trigger ownership and plugin integration boundaries without expanding the completed tray/task UX branch. FB-040 remains deferred because monitoring, thermals, and HUD surfaces are a separate runtime/status lane.
- Successor Deferral: FB-039 remains selected in canon only. Its branch may not be created until FB-038 release debt clears, updated `main` is revalidated, and the repo-level admission gate passes.

## Most Recent Released Workstream Context

### FB-037 Curated Built-In System Actions And Nexus Settings Expansion

- status: `released`
- lane type: `implementation`
- release floor: `minor prerelease`
- target version: `v1.4.0-prebeta`
- release state: `released`
- canonical workstream doc: `Docs/workstreams/FB-037_built_in_actions_and_settings_expansion.md`
- sequencing note: released the curated built-in Windows utility catalog for Task Manager, Calculator, Notepad, and Paint while preserving saved-action override authority, authoring collision protection, confirm/result surfaces, and callable-group behavior

## Prior Released Workstream Context

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
- the released FB-035 lane is closed
- the recent released workstreams above remain part of the locked current baseline
- merged unreleased non-doc implementation debt exists: yes
- FB-038 is the merged-unreleased release-debt owner for the completed tray/task UX milestone; H1 identity/discoverability repair, H2 shortcut-launch tray readback validation, H3 window initialization sequencing, H4 post-fix startup visibility validation, fresh post-H4 technical/live validation, user-facing desktop shortcut validation, and UTS waiver digestion are green
- FB-039 is selected in canon only as the next workstream for Branch Readiness after FB-038 release debt clears and updated `main` is revalidated; no FB-039 branch exists
- FB-039 branch creation remains blocked while FB-038 release debt remains unresolved
- post-release repo truth after the FB-037 release branch merge resolved to no FB-037 release-debt blocker
- successor-lane branch creation for FB-038 is historical; FB-038 is now merged and no longer an executable active implementation branch
- if a branch changes release-facing canon, those canon updates must land on that same branch before PR readiness is allowed
- escaped post-merge canon repair must ride a legal branch surface; `main` is protected and must not be patched directly by Codex
- the released FB-027 baseline does not authorize further saved-action authoring, resolution, voice, Action Studio, routines, profiles, hotkey cleanup, or shutdown-confirmation work by inertia
- remaining future candidate spaces now explicitly recorded in the backlog include:
  - FB-038 for taskbar or tray quick-task UX including Create Custom Task, now merged-unreleased release debt with H3/H4 startup visibility re-entry green, `User-Facing Shortcut Validation: PASS`, UTS handling resolved by documented waiver, and Release Readiness allowed only as file-frozen analysis of inherited release target/scope/artifacts
  - FB-039 for external trigger and plugin integration architecture, selected in canon only with `Branch: Not created`
  - FB-040 for monitoring, thermals, and performance HUD surfaces
- those candidate lanes must be selected deliberately rather than bundled together as one implicit interaction continuation
- FB-037 Branch Readiness does not imply automatic continuation into any remaining candidate lane

Use canonical workstream docs for execution detail.
Use the backlog for item identity.
