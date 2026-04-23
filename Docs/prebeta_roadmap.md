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

- latest public prerelease: `v1.6.3-prebeta`
- latest public release commit: `9f5ae9a78c7dbff79322089bca370fa49da38598`
- latest public prerelease publication: `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.3-prebeta`
- latest public prerelease title: `Pre-Beta v1.6.3`
- merged unreleased non-doc implementation debt exists: no
- the latest public released implementation milestone is FB-004 Future boot orchestrator layer in `v1.6.3-prebeta`
- current phase after FB-004 release closure: `Workstream`
- phase status after FB-004 release closure: FB-015 Workstream is active; WS-1 is complete; no FB-015 implementation is admitted yet
- blocker after FB-004 release: release debt is clear; FB-015 Workstream WS-2 is the next legal seam
- current active workstream: FB-015 Boot and desktop phase-boundary model
- current branch after FB-004 release: `feature/fb-015-boot-desktop-phase-boundary-model`
- selected next workstream: none while FB-015 is active
- next concern: execute FB-015 Workstream WS-2 lifecycle and phase-boundary state framing.

That means the released FB-027 interaction baseline, the released FB-036 authoring-and-callable-group milestone, the released FB-041 deterministic callable-group execution milestone, the released FB-037 built-in catalog milestone, the released FB-038 tray quick-task UX milestone, the released FB-039 external trigger intake architecture milestone, the released FB-040 monitoring/thermal architecture milestone, the released FB-031 UI/UX architecture milestone, the released FB-032 source-of-truth migration milestone, and the released FB-004 future boot-orchestrator architecture milestone are now part of the current public shared pre-Beta baseline.

## Current Release Debt Owner

Merged-Unreleased Release-Debt Owner: None.
Repo State: FB-015 Workstream active on `feature/fb-015-boot-desktop-phase-boundary-model`; WS-1 is complete and WS-2 is next.

Latest Public Prerelease: v1.6.3-prebeta
Latest Public Release Commit: 9f5ae9a78c7dbff79322089bca370fa49da38598
Latest Public Prerelease Publication: https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.3-prebeta
Latest Public Prerelease Title: Pre-Beta v1.6.3
Release Debt: Clear after FB-004 release execution and live release validation.
Post-Release Truth: FB-004 is Released / Closed in v1.6.3-prebeta; release debt is clear; FB-015 is the active promoted Workstream with WS-1 complete.
Selected Next Workstream: None while FB-015 is active.
Next-Branch Creation Gate: Not applicable while FB-015 is active; successor selection belongs to later PR Readiness.
Current active workstream: FB-015 Boot and desktop phase-boundary model
Current Active Workstream Before Release: FB-004 Future boot orchestrator layer
Active Branch Before Release: `feature/fb-004-future-boot-orchestrator-layer`

## Current Active Workstream

FB-015 Boot and desktop phase-boundary model is the active promoted workstream on `feature/fb-015-boot-desktop-phase-boundary-model`. Workstream is active; WS-1 current boot/desktop boundary inventory and ownership map is complete, and WS-2 lifecycle and phase-boundary state framing is admitted next. No runtime behavior, launcher behavior, desktop shortcut behavior, renderer lifecycle behavior, UI behavior, installer behavior, source movement, release packaging, tag creation, or public release editing has started.

## Backlog Priority Review

The 2026-04-23 FB-015 WS-1 pass revalidated open backlog candidates against priority-led selection and deferred-context readiness:

- FB-004 is released and closed in `v1.6.3-prebeta`; it is no longer an active or selected-next branch candidate.
- FB-029 remains `High`, but explicit product/legal identity approval is required before selection; it is not a routine next branch by priority alone.
- FB-015 remains `High`, is promoted, and is the active Workstream with WS-1 complete after FB-004.
- FB-030 remains `Medium` and requires an explicit voice/audio design goal before selection.
- FB-005 remains `Low` and requires explicit path-sensitive workspace approval before selection.

Next-branch clarity: no successor branch is selected while FB-015 is active. Successor selection belongs to later FB-015 PR Readiness.

## Active Promoted Workstream

### FB-015 Boot And Desktop Phase-Boundary Model

- status: `Active`
- record state: `Promoted`
- priority: `High`
- canonical workstream doc: `Docs/workstreams/FB-015_boot_and_desktop_phase_boundary_model.md`
- selection basis: selected during FB-004 PR Readiness after GOV-PR0 raised FB-015 to High and confirmed it is the clearest routine technical successor after the FB-004 boot-orchestrator architecture frame; FB-029 remains High but product/legal-gated, FB-030 remains Medium and voice/audio-gated, and FB-005 remains Low and workspace/path-gated.
- branch: `feature/fb-015-boot-desktop-phase-boundary-model`
- phase status: Workstream active; Branch Readiness is complete; WS-1 current boot/desktop boundary inventory and ownership map is complete.
- next legal seam: WS-2 lifecycle and phase-boundary state framing.
- Minimal Scope: Complete the bounded docs/canon seam chain for current boot/desktop phase-boundary ambiguity, starting with current boundary inventory and ownership mapping before lifecycle framing or implementation-admission rules are extended.

## Latest Released Workstream Context

### FB-004 Future Boot Orchestrator Layer

- status: `released`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.6.3-prebeta`
- release state: `released`
- release title: `Pre-Beta v1.6.3`
- canonical workstream doc: `Docs/workstreams/FB-004_future_boot_orchestrator_layer.md`
- sequencing note: released the docs/canon-only future boot-orchestrator architecture milestone, including source map, lifecycle/state framing, ownership boundaries, diagnostics evidence-root correction, rollback boundaries, stale helper caveat, implementation admission contract, hardening, Live Validation waivers, backlog governance sync, and PR Readiness merge-target canon.
- successor note: FB-015 is active on `feature/fb-015-boot-desktop-phase-boundary-model`; Workstream is active, WS-1 is complete, and WS-2 is next.

## Prior Released Workstream Context

### FB-032 Nexus-Era Vision And Source-Of-Truth Migration

- status: `released`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.6.2-prebeta`
- release state: `released`
- release title: `Pre-Beta v1.6.2`
- canonical workstream doc: `Docs/workstreams/FB-032_nexus_era_vision_and_source_of_truth_migration.md`
- sequencing note: released the architecture-only Nexus-era source-of-truth migration foundation, including current-vs-historical source inventory, naming policy, canonical-vs-historical surface classification, controlled migration admission contract, governance repairs, hardening, Live Validation waivers, and PR Readiness merge-target canon.
- successor note: FB-004 is released and closed in `v1.6.3-prebeta`; FB-015 is active with WS-1 complete and Workstream WS-2 next.

## Prior Released Workstream Context

### FB-031 Nexus Desktop AI UI/UX Overhaul Planning

- status: `released`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.6.1-prebeta`
- release state: `released`
- release title: `Pre-Beta v1.6.1`
- canonical workstream doc: `Docs/workstreams/FB-031_nexus_desktop_ai_ui_ux_overhaul_planning.md`
- sequencing note: released the architecture-only UI/UX planning milestone, including source map, visual-language ownership vocabulary, lifecycle and interaction-state framing, future UI implementation admission contract, Hardening pressure test, Live Validation waivers, PR Readiness merge-target canon, and PR-R1 release-floor validator repair.
- successor note: FB-032 is released and closed in `v1.6.2-prebeta`; FB-004 is released and closed in `v1.6.3-prebeta`; FB-015 is active on `feature/fb-015-boot-desktop-phase-boundary-model` with WS-1 complete and Workstream WS-2 next.

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
- FB-032 is released and closed in `v1.6.2-prebeta`; source-of-truth inventory, naming policy, surface classification, controlled migration admission contract, governance repairs, hardening, Live Validation waivers, and PR Readiness merge-target canon are preserved as historical evidence
- FB-004 is released and closed in `v1.6.3-prebeta`; future boot-orchestrator source map, lifecycle/state framing, ownership boundaries, diagnostics evidence-root correction, rollback boundaries, stale helper caveat, implementation admission contract, hardening, Live Validation waivers, backlog governance sync, and PR Readiness merge-target canon are preserved as historical evidence
- post-release repo truth after the FB-004 release is clear for release debt; FB-015 is active on `feature/fb-015-boot-desktop-phase-boundary-model` with WS-1 complete and Workstream WS-2 next
- successor-lane branch creation for FB-039 is historical; FB-039 is released and no longer an executable active implementation branch
- if a branch changes release-facing canon, those canon updates must land on that same branch before PR readiness is allowed
- escaped post-merge canon repair must ride a legal branch surface; `main` is protected and must not be patched directly by Codex
- the released FB-027 baseline does not authorize further saved-action authoring, resolution, voice, Action Studio, routines, profiles, hotkey cleanup, or shutdown-confirmation work by inertia
- remaining open backlog candidates now explicitly recorded in the backlog include:
  - FB-004 for future boot orchestrator layer, released and closed in `v1.6.3-prebeta`
  - FB-015 for boot and desktop phase-boundary model, active on `feature/fb-015-boot-desktop-phase-boundary-model`, `High` after the FB-004 priority review, and WS-1-complete with Workstream WS-2 next
  - FB-029 for ORIN legal-safe rebrand, future ARIA persona option, and repo licensing hardening, `High` but gated by explicit product/legal identity approval
  - FB-030 for ORIN voice/audio direction refinement, `Medium` and gated by an explicit voice/audio design goal
  - FB-005 for workspace and folder organization, `Low` and gated by explicit path-sensitive workspace approval
- those candidate lanes must be selected deliberately rather than bundled together as one implicit interaction continuation
- FB-037 Branch Readiness does not imply automatic continuation into any remaining candidate lane

Use canonical workstream docs for execution detail.
Use the backlog for item identity.
