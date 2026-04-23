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

- latest public prerelease: `v1.6.1-prebeta`
- latest public release commit: `4ba705d2c855ad271bc73b5dae0e1ba2b88bb5ff`
- latest public prerelease publication: `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.1-prebeta`
- latest public prerelease title: `Pre-Beta v1.6.1`
- merged unreleased non-doc implementation debt exists: no before FB-032 merge; after FB-032 merge, architecture-only release debt exists for `v1.6.2-prebeta`
- the latest public released implementation milestone is FB-031 Nexus Desktop AI UI/UX overhaul planning in `v1.6.1-prebeta`
- current phase after FB-031 release closure: `PR Readiness`
- phase status after FB-031 release closure: FB-032 PR Readiness prepares merge-target canon, release-debt target, selected-next workstream, and live PR validation
- blocker after FB-031 release: none before FB-032 merge; after FB-032 merge, FB-032 release debt blocks next implementation branch creation until `v1.6.2-prebeta` is published and updated `main` is revalidated
- current active workstream: FB-032 Nexus-era vision and source-of-truth migration
- current branch after FB-031 release: `feature/fb-032-nexus-era-vision-source-of-truth-migration`
- selected next workstream: FB-004 Future boot orchestrator layer
- next concern: complete FB-032 PR Readiness, merge PR after validation, then execute Release Readiness for `v1.6.2-prebeta`.

That means the released FB-027 interaction baseline, the released FB-036 authoring-and-callable-group milestone, the released FB-041 deterministic callable-group execution milestone, the released FB-037 built-in catalog milestone, the released FB-038 tray quick-task UX milestone, the released FB-039 external trigger intake architecture milestone, the released FB-040 monitoring/thermal architecture milestone, and the released FB-031 UI/UX architecture milestone are now part of the current public shared pre-Beta baseline.

## Current Release Debt Owner

Merged-Unreleased Release-Debt Owner: FB-032 Nexus-era vision and source-of-truth migration after PR merge.
Repo State: No Active Branch after PR merge until FB-032 release debt clears.

Latest Public Prerelease: v1.6.1-prebeta
Release Target: v1.6.2-prebeta
Release Floor: patch prerelease
Version Rationale: FB-032 is architecture-only and canon-only source-of-truth migration planning, naming policy, surface classification, admission-contract, governance repair, hardening, Live Validation waiver, and PR Readiness merge-target work with no executable, runtime, operator-facing, user-facing, or materially expanded product capability; per governance, architecture-only planning and admission work advances by patch prerelease from `v1.6.1-prebeta` to `v1.6.2-prebeta`.
Release Scope: Architecture-only Nexus-era source-of-truth inventory, current-vs-historical naming policy, canonical-vs-historical surface classification, controlled migration admission contract, bounded multi-seam continuation governance repair, release-note governance repair, backlog-selection governance repair, hardening pressure test, Live Validation waiver truth, and PR Readiness merge-target canon.
Release Artifacts: Tag v1.6.2-prebeta; release title Pre-Beta v1.6.2; inclusion-only release notes summarize the FB-032 source-of-truth migration frame, naming and historical-preservation policy, controlled migration admission contract, governance repairs, hardening result, Live Validation waivers, selected-next deferral, and clean PR history.
Post-Release Truth: FB-032 is Released / Closed in v1.6.2-prebeta; release debt is clear; FB-004 may enter Branch Readiness only after the FB-032 release is published, `main` is updated and revalidated, and the repo-level admission gate passes.
Selected Next Workstream: FB-004 Future boot orchestrator layer
Next-Branch Creation Gate: Do not create the FB-004 branch during FB-032 PR Readiness; successor branch creation is deferred to FB-004 Branch Readiness after PR merge, FB-032 release execution, updated-main revalidation, and release-debt clearance.
Current active workstream: none after FB-032 merge
Current Active Workstream Before Merge: FB-032 Nexus-era vision and source-of-truth migration
Active Branch Before Merge: `feature/fb-032-nexus-era-vision-source-of-truth-migration`

## Current Active Workstream

### FB-032 Nexus-era Vision And Source-Of-Truth Migration

- status: `active`
- lane type: `implementation`
- record state: `Promoted`
- current phase: `PR Readiness`
- branch class: `implementation`
- branch: `feature/fb-032-nexus-era-vision-source-of-truth-migration`
- canonical workstream doc: `Docs/workstreams/FB-032_nexus_era_vision_and_source_of_truth_migration.md`
- release floor: `patch prerelease`
- release state: `active delta`
- release target: `v1.6.2-prebeta`
- minimal scope: define the Nexus-era vision/source-of-truth migration boundary, current-vs-historical naming policy, AI/UI identity routing, canon migration admission rules, and explicit non-goals before any wording migration, persona work, runtime behavior, UI implementation, rebrand execution, or release work is considered.
- sequencing note: WS-1 records the current-vs-historical source-of-truth inventory and naming policy; WS-2 records canonical-vs-historical surface classification and mapping; WS-3 records validation and admission contract for controlled migration execution; H-1 pressure-tests the completed migration frame; LV-1 validates repo truth and records architecture-only shortcut/User Test Summary waivers; PR Readiness prepares merge-target release-debt canon and live PR validation.
- next legal phase: `Release Readiness after PR merge`

## Selected Next Workstream

### FB-004 Future Boot Orchestrator Layer

- status: `deferred / selected next`
- record state: `Registry-only`
- priority: `High`
- selection basis: priority-led backlog selection; FB-004 is a High-priority open candidate with deferred-context fields present, while FB-029 is also High but requires explicit product/legal approval before selection.
- branch: Not created
- minimal scope: define the smallest implementation-facing boot-orchestrator Branch Readiness plan above the desktop launcher, including boot-to-desktop ownership, non-goals, validation proof path, rollback boundary, and explicit protection against runtime delivery by inertia.
- creation gate: successor branch creation is deferred to FB-004 Branch Readiness after FB-032 merges, `v1.6.2-prebeta` release debt clears, updated `main` is revalidated, and the repo-level admission gate passes.

## Most Recent Released Workstream Context

### FB-031 Nexus Desktop AI UI/UX Overhaul Planning

- status: `released`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.6.1-prebeta`
- release state: `released`
- release title: `Pre-Beta v1.6.1`
- canonical workstream doc: `Docs/workstreams/FB-031_nexus_desktop_ai_ui_ux_overhaul_planning.md`
- sequencing note: released the architecture-only UI/UX planning milestone, including source map, visual-language ownership vocabulary, lifecycle and interaction-state framing, future UI implementation admission contract, Hardening pressure test, Live Validation waivers, PR Readiness merge-target canon, and PR-R1 release-floor validator repair.
- successor note: FB-032 PR Readiness selects FB-004 as the next workstream but defers branch creation until FB-032 merges, release debt clears, and updated `main` is revalidated.

## Prior Released Workstream Context

### FB-040 Monitoring, Thermals, And Performance HUD Surface

- status: `released`
- lane type: `implementation`
- release floor: `minor prerelease` (historical published tag; future architecture-only planning/admission milestones must not use minor solely because they define a planning lane)
- target version: `v1.6.0-prebeta`
- release state: `released`
- release title: `Pre-Beta v1.6.0`
- canonical workstream doc: `Docs/workstreams/FB-040_monitoring_thermals_performance_hud_surface.md`
- sequencing note: released the architecture-only monitoring and thermal planning milestone, including source map, ownership vocabulary, lifecycle/trust-safety framing, validation/admission contract, hardening result, and Live Validation waiver handling.
- version-governance note: FB-040 was already published as `v1.6.0-prebeta`; governance now records that future architecture-only, non-user-facing planning/admission milestones default to patch prerelease advancement unless they deliver a runtime, executable, or user-facing capability lane.

### FB-039 External Trigger And Plugin Integration Architecture

- status: `released`
- lane type: `implementation`
- release floor: `minor prerelease`
- target version: `v1.5.0-prebeta`
- release state: `released`
- release title: `Pre-Beta v1.5.0`
- canonical workstream doc: `Docs/workstreams/FB-039_external_trigger_plugin_integration_architecture.md`
- sequencing note: released the internal-only external trigger intake architecture milestone, including source map, ownership vocabulary, lifecycle/trust framing, in-memory registration, bounded invocation follow-through, lifecycle transitions, decision evidence, boundary state snapshots, readiness inspection, registry readiness sweep, summary, detail snapshot, reusable validation coverage, and Live Validation waiver handling.

### FB-038 Taskbar / Tray Quick-Task UX And Create Custom Task Surface

- status: `released`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.4.1-prebeta`
- release state: `released`
- release title: `Pre-Beta v1.4.1`
- canonical workstream doc: `Docs/workstreams/FB-038_taskbar_tray_quick_task_ux.md`
- sequencing note: released the tray quick-task UX milestone, including tray identity/discoverability, tray Open Command Overlay, tray Create Custom Task dialog-open/no-write route, tray-origin create completion through existing FB-036 authoring, catalog reload, exact-match resolution, confirm/result execution, and startup first-visible Core Visualization sequencing repair

## Earlier Released Workstream Context

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
- the released FB-039 external trigger intake architecture milestone is now part of the locked current pre-Beta baseline
- the released FB-035 lane is closed
- the recent released workstreams above remain part of the locked current baseline
- merged unreleased non-doc implementation debt exists: no
- FB-038 is released and closed in `v1.4.1-prebeta`; H1 identity/discoverability repair, H2 shortcut-launch tray readback validation, H3 window initialization sequencing, H4 post-fix startup visibility validation, fresh post-H4 technical/live validation, user-facing desktop shortcut validation, and UTS waiver digestion are preserved as historical evidence
- FB-039 is released and closed in `v1.5.0-prebeta`; internal-only intake runtime boundaries, reusable validation coverage, Live Validation waivers, PR readiness governance, and post-merge release-truth repairs are preserved as historical evidence
- FB-040 is released and closed in `v1.6.0-prebeta`; architecture-only monitoring and thermal source mapping, lifecycle/trust-safety framing, validation/admission contract, hardening, Live Validation waiver truth, and post-release canon closure are preserved as historical evidence
- FB-031 is released and closed in `v1.6.1-prebeta`; UI/UX source mapping, visual-language ownership vocabulary, lifecycle/interaction-state framing, future implementation admission contract, hardening, Live Validation waiver truth, PR Readiness merge-target canon, and PR-R1 release-floor validator repair are preserved as historical evidence
- post-release repo truth after the FB-031 release is clear for release debt before FB-032 merge; FB-032 PR Readiness prepares `v1.6.2-prebeta` release-debt truth and FB-004 selected-next branch deferral
- successor-lane branch creation for FB-039 is historical; FB-039 is released and no longer an executable active implementation branch
- if a branch changes release-facing canon, those canon updates must land on that same branch before PR readiness is allowed
- escaped post-merge canon repair must ride a legal branch surface; `main` is protected and must not be patched directly by Codex
- the released FB-027 baseline does not authorize further saved-action authoring, resolution, voice, Action Studio, routines, profiles, hotkey cleanup, or shutdown-confirmation work by inertia
- remaining future candidate spaces now explicitly recorded in the backlog include:
  - FB-038 for taskbar or tray quick-task UX including Create Custom Task, now released and closed in `v1.4.1-prebeta` with H3/H4 startup visibility re-entry green, `User-Facing Shortcut Validation: PASS`, and UTS handling resolved by documented waiver
  - FB-039 for external trigger and plugin integration architecture, now released and closed in `v1.5.0-prebeta`
  - FB-040 for monitoring, thermals, and performance HUD surfaces, released and closed in `v1.6.0-prebeta`
  - FB-031 for Nexus Desktop AI UI/UX overhaul planning, released and closed in `v1.6.1-prebeta`
  - FB-032 for Nexus-era vision and source-of-truth migration, PR Readiness active on `feature/fb-032-nexus-era-vision-source-of-truth-migration`
  - FB-004 for future boot orchestrator layer, selected next with branch not created
- those candidate lanes must be selected deliberately rather than bundled together as one implicit interaction continuation
- FB-037 Branch Readiness does not imply automatic continuation into any remaining candidate lane

Use canonical workstream docs for execution detail.
Use the backlog for item identity.
