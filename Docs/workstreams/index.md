# Workstream Records Index

## Purpose

This document is the routing index for canonical workstream records under `Docs/workstreams/`.

Docs Source-Truth Reform Model: Compact Pointer Layer.

Use this layer when a backlog item has been promoted and now needs:

- a stable feature-state record
- a branch-local validation/evidence record
- an executed seam or hardening proof trail when needed, with current execution state owned externally
- a closure record
- a stable path before and after closure

This index does not own repo-wide process rules.
Use `Docs/phase_governance.md` for phase names, proof authority, seam governance, timeout governance, preflight rules, stop-loss rules, the validation helper contract, and the desktop UI audit rule.
Use `Docs/validation_helper_registry.md` for durable root `dev/` helper naming, helper status, reuse, and consolidation rules.

## Workstream Record Rules

Durable workstream records preserve identity, approved objective, implemented delta, actual affected proof, accepted deferrals, reusable artifacts and meaningful milestone/closeout evidence. Current phase, assignment, locks, blockers and next action belong to the matching external operational owner. Git owns volatile ref facts.

Use the existing family/backlog identity and accepted plan. One coherent slice is valid; slice counts do not grant authority or require a waiver. New scope/branch splits retain their applicable decision. Detailed element/phase matrices apply when they help the actual risk and acceptance contract, not as a diary after every repair.

Preserve product vision and history by reference. `Docs/phase_governance.md` owns phase/acceptance rules, including applicable launched-client proof, protected state and USER/UTS results. Synthetic/source tests cannot substitute for required actual runtime or human results. UTS remains at its applicable Live Validation boundary. Helper status/reuse belongs to `Docs/validation_helper_registry.md`.


- branch-local "what worked", reuse guidance, and future-branch carry-forward notes belong in the canonical workstream doc first
- only generalized cross-branch lessons should be distilled into `Docs/incident_patterns.md`
- closed workstream docs remain historical lane truth and must not be treated as active execution authority by inertia
- closed workstream docs may explicitly state that no separate ongoing `UTS` artifact remains
- family dossiers are additive lifetime traceability surfaces for feature-family anchors; they do not replace the canonical workstream docs that preserve branch-local historical proof
- family dossiers may begin as shell-only records before pass indexes, slice/seam ledgers, validator/helper indexes, artifact indexes, or migrated historical bodies are populated
- workstreams and family dossiers own durable package trace, slice trace, proof history, branch lessons, and reusable continuity after active branch fold-down
- workstreams and family dossiers must not mirror live Git/GitHub state, open PR state, review-thread state, latest-release state, or worktree dirty/ahead/behind state as current operational truth
- backlog and roadmap point to this layer for durable detail instead of copying package/slice trace tables or active execution diaries

## Package And Slice Trace Ownership

Package Trace and Slice Trace detail belongs here, in the relevant family dossier, in an active Branch Runtime Engineering Plan, or in an explicitly folded compact branch receipt.

Family vision belongs in `Docs/family_visions/` when the durable content is product direction or reusable USER-accepted design standard rather than implementation trace/proof.

When PR Readiness fold-down promotes branch lessons into this layer, preserve:

- package/slice IDs and admission posture
- implemented or deferred user-facing scope
- durable validation/proof references
- future-gated items and approval boundaries
- reusable implementation lessons and helper/validator references

Do not promote:

- live `HEAD`, `origin/main`, ahead/behind, dirty-state, PR/review, tag, or latest-release facts
- watcher runtime state
- stale current-phase wording from a merged branch
- release-window PR lists that can be derived from GitHub for Release Readiness

## Broad Family Routing Overlay

The live backlog routes through broad FAM IDs. Legacy `FB-###` workstream filenames below are durable historical evidence paths only.

| FAM ID | Package ID | Broad Family | Legacy Workstream/Dossier Routing |
| --- | --- | --- | --- |
| `FAM-001` | `PKG-001` | Boot Interface | `FB-042` family dossier plus `FB-043` through `FB-049` historical pass/evidence records |
| `FAM-003` | `PKG-003` | Interaction and Actions | `FB-027` family dossier plus `FB-036`, `FB-037`, `FB-038`, `FB-041`, and PR #109 historical evidence |
| `FAM-004` | `PKG-004` | Voice and Audio | `FB-030` promoted workstream record and PR #108 merge evidence |
| `FAM-006` | `PKG-006` | Monitoring and HUD | `FB-040` historical architecture proof plus durable product/admission receipt in `Docs/branch_records/feature_fam_006_monitoring_hud_product_surface.md`; current Workstream authority resolves through the matching external operational record |

## Minimum Durable Traceability Content

Keep identity, approved objective/scope, current-owner pointer, implemented delta, actual affected proof, accepted deferrals, material artifact/reuse references and next real boundary. Include applicable USER/UTS evidence and closeout receipts. Link preserved historical evidence; do not duplicate the mutable external state or require a per-seam diary or second ledger.


## Current Canonical Workstream Records

### Active

Active in this index identifies maintained product contracts and durable proof records, not live operational authority. Current task, phase and executable branch assignment must resolve through the matching external record.

None.

### Merged / Release Debt Owners

Merged / Release Debt Owners are promoted implementation workstreams whose implementation branch is merge-target complete but whose public release packaging has not yet cleared release debt.
These records are not active implementation branch owners after merge.

The retained index snapshot lists no promoted workstream release-debt record. Resolve current release-debt ownership and acceptance through the applicable release owner and live Git/GitHub evidence.

Historical branch release-debt receipt: `Docs/branch_records/feature_fam_006_dashboard_render_layout_hardening.md` records PR #129 FAM-006 Dashboard render/layout hardening as merged-unreleased release debt after `v1.7.0-prebeta`.

### Closed

- `Docs/workstreams/FB-030_orin_voice_audio_direction_refinement.md`

### Family Anchor Records

- `Docs/workstreams/FB-042_desktop_entrypoint_runtime_refinement.md`
- `Docs/workstreams/FB-027_interaction_system_baseline.md`

### Historical Pass Alias Records

These records are no longer standalone backlog items. They are historical family-pass source records routed through the family dossier and preserved canonical workstream docs.

#### FB-042 Family

- `Docs/workstreams/FB-043_top_level_entrypoint_handoff_refinement.md`
- `Docs/workstreams/FB-044_boot_desktop_handoff_outcome_refinement.md`
- `Docs/workstreams/FB-045_active_session_relaunch_outcome_refinement.md`
- `Docs/workstreams/FB-046_active_session_relaunch_reacquisition.md`
- `Docs/workstreams/FB-047_active_session_relaunch_decline_preservation.md`
- `Docs/workstreams/FB-048_active_session_relaunch_signal_failure_and_wait_timeout_truth.md`

#### FB-027 Family

- `Docs/workstreams/FB-036_saved_action_authoring.md`
- `Docs/workstreams/FB-041_deterministic_callable_group_execution_layer.md`
- `Docs/workstreams/FB-037_built_in_actions_and_settings_expansion.md`
- `Docs/workstreams/FB-038_taskbar_tray_quick_task_ux.md`

### Other Closed Workstreams

These closed support, architecture, and governance workstreams are source-of-truth trace records only. They do not become selectable backlog identities again unless the USER explicitly approves a future major release/support lane.

- `Docs/workstreams/FB-005_workspace_and_folder_organization.md`
- `Docs/workstreams/FB-029_orin_identity_licensing_hardening.md`
- `Docs/workstreams/FB-015_boot_and_desktop_phase_boundary_model.md`
- `Docs/workstreams/FB-004_future_boot_orchestrator_layer.md`
- `Docs/workstreams/FB-032_nexus_era_vision_and_source_of_truth_migration.md`
- `Docs/workstreams/FB-031_nexus_desktop_ai_ui_ux_overhaul_planning.md`
- `Docs/workstreams/FB-040_monitoring_thermals_performance_hud_surface.md`
- `Docs/workstreams/FB-039_external_trigger_plugin_integration_architecture.md`
- `Docs/workstreams/FB-035_release_context_fallback_hardening.md`
- `Docs/workstreams/FB-034_recoverable_diagnostics.md`
- `Docs/workstreams/FB-025_boot_desktop_milestone_taxonomy_clarification.md`
- `Docs/workstreams/FB-033_startup_snapshot_harness_follow_through.md`
- `Docs/workstreams/FB-028_history_state_relocation.md`

## Family Dossier Records

Family dossiers are additive lifetime traceability surfaces for family anchors.
Use them to gather long-lived family routing and migration indexes without rewriting the underlying historical workstream records in one pass.

- `Docs/workstreams/FB-042_desktop_startup_runtime_family_dossier.md`
- `Docs/workstreams/FB-027_interaction_shared_action_family_dossier.md`

## Naming Pattern

Use:

- `Docs/workstreams/FB-XXX_slug.md`

for backlog-backed canonical workstream records.

Use:

- `Docs/workstreams/FB-XXX_slug_family_dossier.md`

for family-dossier records that layer over an existing family anchor without replacing its historical workstream docs.
