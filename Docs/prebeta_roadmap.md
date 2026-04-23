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

- latest public prerelease: `v1.6.4-prebeta`
- latest public release commit: `d2268b71feefa062c8117eae29f8ec17879a724f`
- latest public prerelease publication: `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.4-prebeta`
- latest public prerelease title: `Pre-Beta v1.6.4`
- merged unreleased non-doc implementation debt exists: no
- the latest public released implementation milestones are FB-015 Boot and desktop phase-boundary model and FB-029 ORIN legal-safe rebrand, future ARIA persona option, and repo licensing hardening in `v1.6.4-prebeta`
- current phase after `v1.6.4-prebeta` release closure: `PR Readiness`
- phase status after `v1.6.4-prebeta` release closure: FB-015 and FB-029 are Released / Closed in `v1.6.4-prebeta`; release debt is clear; FB-030 now owns active PR Readiness truth on `feature/fb-030-orin-voice-audio-direction-refinement`, with WS-1 through WS-3, H-1, LV-1, PR-1, PR-2, and PR-3 complete on open PR #81
- current active workstream: FB-030 ORIN voice/audio direction refinement
- current branch after `v1.6.4-prebeta` release closure: `feature/fb-030-orin-voice-audio-direction-refinement`
- next concern: merge live PR #81, preserve the docs/canon-only voice/audio planning boundary, and hand off to file-frozen Release Readiness on updated `main`

That means the released FB-027 interaction baseline, the released FB-036 authoring-and-callable-group milestone, the released FB-041 deterministic callable-group execution milestone, the released FB-037 built-in catalog milestone, the released FB-038 tray quick-task UX milestone, the released FB-039 external trigger intake architecture milestone, the released FB-040 monitoring/thermal architecture milestone, the released FB-031 UI/UX architecture milestone, the released FB-032 source-of-truth migration milestone, the released FB-004 future boot-orchestrator architecture milestone, and the released FB-015 plus FB-029 planning milestones are now part of the current public shared pre-Beta baseline.

## Current Release Debt Owner

Merged-Unreleased Release-Debt Owner: None.
Repo State: Active Branch. FB-030 now owns active promoted implementation truth on `feature/fb-030-orin-voice-audio-direction-refinement`; `v1.6.4-prebeta` is live and release debt is clear.

Latest Public Prerelease: v1.6.4-prebeta
Latest Public Release Commit: d2268b71feefa062c8117eae29f8ec17879a724f
Latest Public Prerelease Publication: https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.4-prebeta
Latest Public Prerelease Title: Pre-Beta v1.6.4
Release Debt: Clear after `v1.6.4-prebeta` publication, validation, and post-release canon closure.
Current active workstream: FB-030 ORIN voice/audio direction refinement
Current Active Workstream Before Release: FB-015 Boot and desktop phase-boundary model
Active Branch: `feature/fb-030-orin-voice-audio-direction-refinement`
Active Branch Before Release: `feature/fb-015-boot-desktop-phase-boundary-model`

## Current Active Workstream

FB-030 ORIN voice/audio direction refinement on `feature/fb-030-orin-voice-audio-direction-refinement`.

PR Readiness is active on this branch. Branch Readiness is complete, WS-1 current voice/audio surface inventory and ownership map is durably recorded, WS-2 lifecycle and persona-state framing for voice/audio transitions is complete, WS-3 validation and admission contract for future voice/audio implementation is complete, H-1 hardening is complete, LV-1 Live Validation is complete, and PR-1 through PR-3 are complete. PR #81 is open, non-draft, `MERGEABLE`, and `CLEAN`. No runtime voice/audio implementation, audio-asset changes, persona-default changes, or public voice-copy changes are admitted yet.

### FB-030 ORIN voice/audio direction refinement

- status: `Active`
- record state: `Promoted`
- priority: `Medium`
- canonical workstream doc: `Docs/workstreams/FB-030_orin_voice_audio_direction_refinement.md`
- branch: `feature/fb-030-orin-voice-audio-direction-refinement`
- phase status: PR Readiness is active; Branch Readiness is complete; WS-1 current voice/audio surface inventory and ownership map, WS-2 lifecycle and persona-state framing for voice/audio transitions, WS-3 validation and admission contract for future voice/audio implementation, H-1 hardening, LV-1 Live Validation, and PR-1 through PR-3 are complete; PR #81 is open, non-draft, `MERGEABLE`, and `CLEAN`; and no runtime voice/audio implementation is admitted yet.
- next legal seam: merge PR #81, then execute file-frozen Release Readiness on updated `main`.
- Minimal Scope: Complete the bounded docs/canon voice/audio planning seam chain: current surface inventory and ownership mapping, lifecycle/persona-state framing, and the implementation admission contract before runtime voice, shutdown voice, recovery voice, persona-default, or public voice-copy change begins.

## Backlog Priority Review

The 2026-04-23 priority reading is updated during FB-030 PR Readiness:

- FB-004 is released and closed in `v1.6.3-prebeta`; it is no longer an active or selected-next branch candidate.
- FB-015 is released and closed in `v1.6.4-prebeta`; it no longer owns release debt or active branch truth.
- FB-029 is released and closed in `v1.6.4-prebeta`; it no longer owns release debt or active branch truth.
- FB-030 remains `Medium`, is now promoted on `feature/fb-030-orin-voice-audio-direction-refinement`, and WS-1 through WS-3 plus H-1, LV-1, and PR-1 through PR-3 now record the ownership map, lifecycle/persona-state framing, implementation-admission contract, hardening corrections, Live Validation waivers, merge-target package truth, selected-next gate, and live PR validation needed to complete PR Readiness cleanly.
- FB-005 remains `Low`, is selected next planning-only, and still requires explicit path-sensitive workspace approval before Branch Readiness admission or branch creation.

Current-branch clarity: FB-030 is the active promoted implementation workstream on `feature/fb-030-orin-voice-audio-direction-refinement`; FB-005 is selected next planning-only; and the selected-next implementation branch remains not created while this branch owns execution truth.

## Selected Next Workstream

### FB-005 Workspace and folder organization

- Status: `Deferred`
- Record State: `Registry-only`
- Priority: `Low`
- Branch: Not created
- Selection Basis: FB-005 is the only remaining open backlog candidate after FB-030 and is selected next planning-only while explicit path-sensitive workspace approval remains unresolved.
- Minimal Scope: Define one bounded workspace/path slice with exact file/path ownership, migration limits, validation coverage, and rollback instructions before any workspace movement or branch admission begins.
- Branch Creation Gate: After FB-030 merges, `v1.6.5-prebeta` is published and validated, updated `main` is revalidated, and explicit path-sensitive workspace approval admits FB-005 Branch Readiness.

## Latest Released Workstream Context

### FB-029 ORIN Legal-Safe Rebrand, Future ARIA Persona Option, And Repo Licensing Hardening

- status: `released`
- record state: `Closed`
- priority: `High`
- canonical workstream doc: `Docs/workstreams/FB-029_orin_identity_licensing_hardening.md`
- selection basis: selected during FB-015 PR Readiness as the highest-priority remaining open backlog candidate, then carried on this branch first for blocker-clearing FB-015 canon repair and now for completed Branch Readiness planning.
- branch: `feature/fb-029-orin-identity-licensing-hardening`
- phase status: Released / Closed in `v1.6.4-prebeta`; PR #76 merged into `main` at `0897fab768dc07385f83fab81434ba7926ecc4a1`; the milestone remains docs/canon-only historical truth, and explicit product/legal approval still blocks any later implementation-facing naming, licensing, release, runtime, or persona-surface change.
- repo-level post-release state: active branch truth now belongs to FB-030 on `feature/fb-030-orin-voice-audio-direction-refinement`.
- next legal seam: none; this record is now historical released truth.
Release Target: v1.6.4-prebeta
Release Floor: patch prerelease
Version Rationale: FB-029 remains a docs/canon-only identity, persona-option, and licensing-planning milestone with no new executable, runtime, operator-facing, user-facing, or materially expanded product capability.
Release Scope: Identity source-of-truth inventory, persona-option boundary framing, licensing boundary framing, implementation admission contract, hardening corrections, Live Validation waivers, PR package history, merged-unreleased package-state repair, and post-merge current-state cleanup.
Release Artifacts: Tag v1.6.4-prebeta; release title Pre-Beta v1.6.4; rich Markdown release notes summarize the FB-015 boundary model and the FB-029 identity/licensing planning frame without repeating the release title inside the notes body, and GitHub-generated `## What's Changed` plus `**Full Changelog**:` must be included.
Post-Release Truth: FB-029 is Released / Closed in `v1.6.4-prebeta`; FB-015 is also Released / Closed in the same package; release debt is clear; and FB-030 now owns active PR Readiness truth on `feature/fb-030-orin-voice-audio-direction-refinement`, with WS-1 through WS-3, H-1, LV-1, PR-1, and PR-2 complete and PR-3 next.
- Minimal Scope: Define the legal-safe ORIN naming, optional future ARIA persona posture, and licensing-hardening planning frame before any naming, licensing, release, runtime, or persona-facing edits begin.

### FB-015 Boot And Desktop Phase-Boundary Model

- status: `released`
- record state: `Closed`
- priority: `High`
- canonical workstream doc: `Docs/workstreams/FB-015_boot_and_desktop_phase_boundary_model.md`
- selection basis: selected during FB-004 PR Readiness after GOV-PR0 raised FB-015 to High and confirmed it is the clearest routine technical successor after the FB-004 boot-orchestrator architecture frame; PR #75 merged, FB-015 carried release debt through `v1.6.4-prebeta`, and the lane is now released and closed.
- branch: `feature/fb-015-boot-desktop-phase-boundary-model`
- phase status: Released / Closed in `v1.6.4-prebeta`; PR #75 merged into `main` at `3e821e07ff91d814fd7aba9b50819f97d700a301`; WS-1 through WS-3, H-1, LV-1, PR-1, PR-2, and PR-3 are complete; release debt is clear after publication, validation, and post-release canon closure.
- next legal seam: none; this record is now historical released truth.
Release Target: v1.6.4-prebeta
Release Floor: patch prerelease
Version Rationale: FB-015 remains a docs/canon-only boot and desktop phase-boundary architecture plus admission milestone with no new executable, runtime, operator-facing, user-facing, or materially expanded product capability.
Release Scope: FB-015 boot and desktop phase-boundary inventory, ownership map, lifecycle and state framing, implementation admission contract, hardening corrections, Live Validation waivers, PR package history, post-merge canon repair, and merged-unreleased release-debt framing, plus the FB-029 identity source-of-truth inventory, persona-option boundary framing, licensing boundary framing, implementation admission contract, hardening corrections, Live Validation waivers, and PR Readiness package history.
Release Artifacts: Tag v1.6.4-prebeta; release title Pre-Beta v1.6.4; rich Markdown release notes summarize the FB-015 boundary model and the FB-029 identity/licensing planning frame without repeating the release title inside the notes body, and GitHub-generated `## What's Changed` plus `**Full Changelog**:` must be included.
Post-Release Truth: FB-015 is Released / Closed in `v1.6.4-prebeta`; FB-029 is also Released / Closed in the same package; release debt is clear; and FB-030 now owns active PR Readiness truth on `feature/fb-030-orin-voice-audio-direction-refinement`, with WS-1 through WS-3, H-1, LV-1, PR-1, and PR-2 complete and PR-3 next.
- Minimal Scope: Complete the bounded docs/canon seam chain for current boot/desktop phase-boundary ambiguity, starting with current boundary inventory and ownership mapping before lifecycle framing or implementation-admission rules are extended.

## Prior Released Workstream Context

### FB-004 Future Boot Orchestrator Layer

- status: `released`
- lane type: `implementation`
- release floor: `patch prerelease`
- target version: `v1.6.3-prebeta`
- release state: `released`
- release title: `Pre-Beta v1.6.3`
- canonical workstream doc: `Docs/workstreams/FB-004_future_boot_orchestrator_layer.md`
- sequencing note: released the docs/canon-only future boot-orchestrator architecture milestone, including source map, lifecycle/state framing, ownership boundaries, diagnostics evidence-root correction, rollback boundaries, stale helper caveat, implementation admission contract, hardening, Live Validation waivers, backlog governance sync, and PR Readiness merge-target canon.
- successor note: FB-015 and FB-029 are released and closed in `v1.6.4-prebeta`, and FB-030 now owns active Workstream truth on `feature/fb-030-orin-voice-audio-direction-refinement`.

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
- successor note: FB-004 is released and closed in `v1.6.3-prebeta`; FB-015 and FB-029 are released and closed in `v1.6.4-prebeta`; and FB-030 now owns active Workstream truth on `feature/fb-030-orin-voice-audio-direction-refinement`.

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
- successor note: FB-032 is released and closed in `v1.6.2-prebeta`; FB-004 is released and closed in `v1.6.3-prebeta`; FB-015 and FB-029 are released and closed in `v1.6.4-prebeta`; and FB-030 now owns active Workstream truth on `feature/fb-030-orin-voice-audio-direction-refinement`.

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
- post-release repo truth after the `v1.6.4-prebeta` release now carries FB-015 and FB-029 as released and closed while FB-030 owns active Workstream truth on `feature/fb-030-orin-voice-audio-direction-refinement`
- successor-lane branch creation for FB-039 is historical; FB-039 is released and no longer an executable active implementation branch
- if a branch changes release-facing canon, those canon updates must land on that same branch before PR readiness is allowed
- escaped post-merge canon repair must ride a legal branch surface; `main` is protected and must not be patched directly by Codex
- the released FB-027 baseline does not authorize further saved-action authoring, resolution, voice, Action Studio, routines, profiles, hotkey cleanup, or shutdown-confirmation work by inertia
- remaining open backlog candidates now explicitly recorded in the backlog include:
  - FB-004 for future boot orchestrator layer, released and closed in `v1.6.3-prebeta`
  - FB-015 for boot and desktop phase-boundary model, released and closed in `v1.6.4-prebeta`
  - FB-029 for ORIN legal-safe rebrand, future ARIA persona option, and repo licensing hardening, released and closed in `v1.6.4-prebeta` and still implementation-gated for any later naming, licensing, release, runtime, or persona-facing execution
  - FB-030 for ORIN voice/audio direction refinement, `Medium`, promoted on `feature/fb-030-orin-voice-audio-direction-refinement`, and now carrying the explicit voice/audio design goal, ownership map, and conflict inventory needed for continued Workstream admission
  - FB-005 for workspace and folder organization, `Low` and gated by explicit path-sensitive workspace approval
- those candidate lanes must be selected deliberately rather than bundled together as one implicit interaction continuation
- FB-037 Branch Readiness does not imply automatic continuation into any remaining candidate lane

Use canonical workstream docs for execution detail.
Use the backlog for item identity.
