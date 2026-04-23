# Nexus Feature Backlog

This file is the controlled registry for tracked work, deferred planning items, historical implemented items, and future promoted bug identities.

Rules:

- ideas must not be implemented immediately
- ideas must not silently expand current scope
- backlog identity remains controlled and approval-gated
- `Status` is the delivery or work field
- `Record State` is the canonical-record lifecycle field
- `Priority` is the primary backlog selection signal for open candidate work
- `Target Version` is not an open-backlog selection field and must not be used to rank, select, defer, or skip open backlog candidates
- open `Registry-only` and active `Promoted` entries should not carry `Target Version`; release target truth is assigned later through roadmap, workstream, PR Readiness, and Release Readiness governance when release-bearing work exists
- closed, released, implemented, or release-debt entries may preserve `Target Version` as historical release evidence
- if `Status` is `Deferred`, the entry must also state `Deferred Since:`, `Deferred Because:`, and `Selection / Unblock:` so next-workstream selection can evaluate it without guessing
- allowed `Record State` values are `Registry-only`, `Promoted`, and `Closed`
- if `Record State` is not `Registry-only`, `Canonical Workstream Doc` must exist
- backlog entries keep the short registry story, not the full execution story

Record-state meaning:

- `Registry-only` = tracked identity only; no canonical workstream execution record is required yet
- `Promoted` = canonical workstream doc required and used as the durable execution and traceability record while the lane is active
- `Closed` = canonical workstream doc remains stable historical lane truth after closure

Historical note:

- older implemented entries may preserve older Jarvis-era titles as historical identity
- those preserved titles are not current runtime-path claims

## Promoted Canonical Workstreams

- `Docs/workstreams/FB-015_boot_and_desktop_phase_boundary_model.md`

## Active Promoted Workstream

FB-015 Boot and desktop phase-boundary model is the active promoted workstream on `feature/fb-015-boot-desktop-phase-boundary-model`.

Main-facing canon is aligned to post-release truth: FB-040 is released and closed in `v1.6.0-prebeta`, FB-031 is released and closed in `v1.6.1-prebeta`, FB-032 is released and closed in `v1.6.2-prebeta`, FB-004 is released and closed in `v1.6.3-prebeta`, and release debt is clear. FB-015 is now in Workstream on `feature/fb-015-boot-desktop-phase-boundary-model`; WS-1 current boot/desktop boundary inventory and ownership map is complete, and WS-2 lifecycle and phase-boundary state framing is admitted next.
FB-039 is released and closed in `v1.5.0-prebeta`.
FB-038 remains released and closed in `v1.4.1-prebeta`.

## Merged-Unreleased Release-Debt Owner

Merged-Unreleased Release-Debt Owner: None.
Repo State: FB-015 Workstream active on `feature/fb-015-boot-desktop-phase-boundary-model`; WS-1 is complete and WS-2 is next.
Latest Public Prerelease: v1.6.3-prebeta.
Latest Public Release Commit: 9f5ae9a78c7dbff79322089bca370fa49da38598.
Latest Public Prerelease Publication: https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.3-prebeta.
Latest Public Prerelease Title: Pre-Beta v1.6.3.
Release Debt: Clear after FB-004 release execution and live release validation.
Post-Release Truth: FB-004 is Released / Closed in v1.6.3-prebeta; release debt is clear; FB-015 is the active promoted Workstream with WS-1 complete.
Selected Next Workstream: None while FB-015 is active.
Next-Branch Creation Gate: Not applicable while FB-015 is active; successor selection belongs to later PR Readiness.

## Backlog Governance Sync

Last Reviewed: 2026-04-23 during FB-015 WS-1.

Open-candidate priority review:

- FB-004 is released and closed in `v1.6.3-prebeta`; it is no longer an active or selected-next branch candidate.
- FB-029 remains `High`, but its own selection/unblock rule requires explicit product/legal identity approval before it can be selected; it is not a routine next branch by priority alone.
- FB-015 remains `High`, is promoted, and is the active Workstream with WS-1 complete because boot/desktop phase-boundary follow-through is the highest-priority routine technical successor after FB-004.
- FB-030 remains `Medium` because it requires an explicit voice/audio design goal and must not enter as incidental persona or runtime cleanup.
- FB-005 remains `Low` because remaining workspace movement is path-sensitive and requires explicit workspace/path approval.

Next-branch clarity: no successor branch is selected while FB-015 is active. Successor selection belongs to later FB-015 PR Readiness.

## Registry Items

### [ID: FB-005] Workspace and folder organization

Status: Deferred (since v2.0 closeout; Step 4 is complete and Step 5 or broader workspace moves need explicit path-sensitive approval)
Record State: Registry-only
Priority: Low
Release Stage: Slice-staged
Deferred Since: v2.0 closeout after the Step 4 workspace slice; the earlier first workspace slice is preserved in v1.9.0 closeout history.
Deferred Because: remaining workspace movement is path-sensitive and can break imports, launcher routes, logs, or user-facing entrypoints if treated as casual cleanup.
Selection / Unblock: Select only when the next approved lane is a bounded workspace/path slice with exact file/path ownership, migration limits, validation coverage, and rollback instructions.
Summary: Continue workspace organization only through explicitly approved path-sensitive slices.
Why it matters: Keeps folder and ownership cleanup deliberate instead of letting it blur into unrelated feature work.

### [ID: FB-015] Boot and desktop phase-boundary model

Status: Active
Record State: Promoted
Priority: High
Release Stage: Slice-staged
Deferred Since: v2.0 closeout after the FB-015 rev1a phase-boundary clarification.
Deferred Because: the boot/desktop ownership model is clarified at planning level, but no later implementation-facing boundary change has been admitted.
Selection / Unblock: Select when a concrete boot, desktop, startup, trust, or orchestration lane is blocked by unresolved ownership boundaries; Branch Readiness must name the exact ambiguity it resolves.
Priority Review: Raised to High during the FB-004 pre-PR docs governance sync because boot/desktop phase-boundary follow-through is the clearest routine technical successor after FB-004 unless an explicitly approved product/legal, voice, or workspace lane supersedes it.
Branch: feature/fb-015-boot-desktop-phase-boundary-model
Canonical Workstream Doc: Docs/workstreams/FB-015_boot_and_desktop_phase_boundary_model.md
Branch Readiness: Complete. The branch objective, target end-state, seam families, validation contract, User Test Summary strategy, later-phase expectations, and first Workstream seam are recorded in the canonical workstream doc.
Workstream: WS-1 current boot/desktop boundary inventory and ownership map is complete; WS-2 lifecycle and phase-boundary state framing is admitted next.
Minimal Scope: Complete the bounded docs/canon seam chain for current boot/desktop phase-boundary ambiguity, starting with current boundary inventory and ownership mapping before lifecycle framing or implementation-admission rules are extended.
Summary: Preserve the future boot and desktop phase-boundary model above the already-closed milestone taxonomy work.
Why it matters: Keeps boot-versus-desktop ownership planning explicit without reopening the closed taxonomy milestone by inertia.

### [ID: FB-029] ORIN legal-safe rebrand, future ARIA persona option, and repo licensing hardening

Status: Deferred (pending explicit product/legal identity decision; not selectable as routine wording cleanup)
Record State: Registry-only
Priority: High
Release Stage: pre-Beta
Deferred Since: current pre-Beta identity backlog registration before FB-032 promotion.
Deferred Because: legal-safe naming, ORIN/ARIA persona posture, and licensing hardening need explicit product/legal approval and must not ride along with source-of-truth migration, UI, runtime, or release work.
Selection / Unblock: Select only after the user explicitly approves identity/legal hardening as the next lane; Branch Readiness must separate naming, licensing, persona, release, and runtime non-goals before edits begin.
Summary: Track future ORIN-era naming, persona, and licensing hardening work without treating the local rebrand overlay as merged truth.
Why it matters: Product identity, legal posture, and repo ownership still need durable future treatment, but not by accidental carry-forward.

### [ID: FB-030] ORIN voice/audio direction refinement

Status: Deferred (pending explicit voice/persona direction lane; not selectable as incidental runtime or canon cleanup)
Record State: Registry-only
Priority: Medium
Release Stage: pre-Beta
Deferred Since: current pre-Beta voice/persona backlog registration before FB-032 promotion.
Deferred Because: ORIN voice identity needs a deliberate persona-facing direction pass; current voice harness, shutdown-voice, and source-of-truth work do not admit broader voice redesign or execution behavior.
Selection / Unblock: Select only with an explicit voice/audio design goal, affected-surface map, validation boundary, and non-goals separating persona direction from runtime execution.
Summary: Preserve future ORIN voice-direction refinement as its own bounded persona-facing lane.
Why it matters: Voice identity should be intentional and should not piggyback on unrelated runtime or canon work.

## Closed Canonical Workstreams

### [ID: FB-004] Future boot orchestrator layer

Status: Released (v1.6.3-prebeta)
Record State: Closed
Priority: High
Release Stage: Slice-staged
Target Version: v1.6.3-prebeta
Release Title: Pre-Beta v1.6.3
Branch: feature/fb-004-future-boot-orchestrator-layer
Canonical Workstream Doc: Docs/workstreams/FB-004_future_boot_orchestrator_layer.md
Branch Readiness: Complete. The branch objective, target end-state, seam families, validation contract, User Test Summary strategy, later-phase expectations, and first Workstream seam are recorded in the canonical workstream doc.
Workstream: WS-1 current boot-to-desktop source map and ownership boundary, WS-2 lifecycle and orchestration-state framing, and WS-3 validation and admission contract are complete.
Hardening: H-1 boot-orchestrator pressure test is complete. Diagnostics-root canon aligns with runtime-root launcher truth, and stale launcher regression helper reuse is repair-gated.
Live Validation: LV-1 repo-truth alignment, user-facing shortcut applicability, User Test Summary applicability, desktop export applicability, cleanup posture, and waiver handling are complete.
PR Readiness: Merge-target canon, post-merge release-debt truth, selected-next workstream truth, PR package details, and live PR validation were recorded before PR #74 merged.
Release Execution: `v1.6.3-prebeta` is live at https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.3-prebeta on commit `9f5ae9a78c7dbff79322089bca370fa49da38598`.
Release Target: v1.6.3-prebeta
Release Floor: patch prerelease
Version Rationale: FB-004 was a docs/canon-only architecture and admission milestone with no executable, runtime, operator-facing, user-facing, or materially expanded product capability.
Release Scope: Future boot-orchestrator source map, lifecycle/state framing, ownership boundaries, diagnostics evidence-root correction, rollback boundaries, stale launcher helper caveat, implementation admission contract, hardening, Live Validation waivers, backlog governance sync, and PR Readiness merge-target canon.
Release Artifacts: Tag v1.6.3-prebeta; release title Pre-Beta v1.6.3; rich Markdown release notes summarize the FB-004 boot-orchestrator planning frame, validation/admission contract, diagnostics-root correction, waiver posture, backlog sync, and selected-next branch gate with GitHub-generated What's Changed and Full Changelog sections.
Post-Release Truth: FB-004 is Released / Closed in v1.6.3-prebeta; release debt is clear; FB-015 Branch Readiness may continue on `feature/fb-015-boot-desktop-phase-boundary-model` after updated-main revalidation and the repo-level admission gate pass.
Summary: Preserved the future top-level boot-orchestrator direction above the desktop launcher without authorizing runtime delivery yet.
Why it matters: Keeps the longer-term boot-to-desktop product direction explicit while current desktop and diagnostics work stays bounded.

### [ID: FB-032] Nexus-era vision and source-of-truth migration

Status: Released (v1.6.2-prebeta)
Record State: Closed
Priority: Medium
Release Stage: pre-Beta
Target Version: v1.6.2-prebeta
Release Title: Pre-Beta v1.6.2
Branch: feature/fb-032-nexus-era-vision-source-of-truth-migration
Canonical Workstream Doc: Docs/workstreams/FB-032_nexus_era_vision_and_source_of_truth_migration.md
Workstream: WS-1 current-vs-historical source-of-truth inventory and naming policy, WS-2 classification and mapping of canonical vs historical surfaces, and WS-3 validation and admission contract for controlled migration execution are complete.
Hardening: H-1 source-of-truth migration frame pressure test is complete.
Live Validation: LV-1 repo-truth alignment, user-facing shortcut applicability, User Test Summary applicability, desktop export applicability, cleanup posture, and waiver handling are complete.
PR Readiness: PR-1 merge-target canon, PR-2 durable branch truth, and PR-3 live PR validation are complete; PR #73 merged cleanly into `main`.
Release Execution: `v1.6.2-prebeta` is live at https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.2-prebeta on commit `e282072769ec25694928293ce51e144d6a37f611`.
Branch Readiness Governance Repair: GitHub release notes across the live release history were standardized to Markdown release bodies that do not repeat the release title as a leading H1 and that include generated `## What's Changed` and `**Full Changelog**:` sections; Release Readiness governance and validator coverage now require that format before future release execution can be treated as complete.
Minimal Scope: FB-032 kept Nexus-era source-of-truth migration controlled by current-vs-historical naming policy, canonical vs historical surface classification, AI/UI identity routing, canon migration admission rules, and explicit non-goals before any wording migration, persona work, runtime behavior, UI implementation, rebrand execution, or release work is considered.
Release Target: v1.6.2-prebeta
Release Floor: patch prerelease
Version Rationale: FB-032 was architecture-only and canon-only planning, admission, validation, and governance work with no executable, runtime, operator-facing, user-facing, or materially expanded product capability.
Release Scope: Architecture-only Nexus-era source-of-truth inventory, naming policy, surface classification, controlled migration admission contract, governance repairs, hardening, Live Validation waivers, and PR Readiness merge-target canon.
Release Artifacts: Tag v1.6.2-prebeta; release title Pre-Beta v1.6.2; inclusion-only release notes summarize the FB-032 migration frame and governance/validation outcomes.
Post-Release Truth: FB-032 is Released / Closed in v1.6.2-prebeta; release debt is clear; FB-004 is Released / Closed in `v1.6.3-prebeta`, and FB-015 Branch Readiness is selected next on `feature/fb-015-boot-desktop-phase-boundary-model`.
Summary: Preserved the broader Nexus-era vision and source-of-truth migration foundation above future controlled migration work.
Why it matters: The repo now has a controlled identity, naming, and source-of-truth migration frame before deeper wording or implementation normalization begins.

### [ID: FB-031] Nexus Desktop AI UI/UX overhaul planning

Status: Released (v1.6.1-prebeta)
Record State: Closed
Priority: Medium
Release Stage: pre-Beta
Target Version: v1.6.1-prebeta
Release Title: Pre-Beta v1.6.1
Branch: feature/fb-031-nexus-desktop-ai-ui-ux-overhaul-planning
Canonical Workstream Doc: Docs/workstreams/FB-031_nexus_desktop_ai_ui_ux_overhaul_planning.md
Minimal Scope: Define the Nexus-era UI/UX overhaul planning boundary, source map, visual-language ownership, lifecycle/interaction-state framing, validation contract, and explicit non-goals before any UI implementation, runtime behavior, settings work, launcher work, or release work is considered.
Release Target: v1.6.1-prebeta
Release Floor: patch prerelease
Version Rationale: FB-031 is architecture-only UI/UX planning and implementation-admission canon with no executable, runtime, operator-facing, user-facing, or materially expanded product capability; per governance, architecture-only planning/admission work used patch prerelease advancement from v1.6.0-prebeta to v1.6.1-prebeta.
Release Scope: Architecture-only Nexus Desktop AI UI/UX source map, visual-language ownership vocabulary, lifecycle and interaction-state framing, future UI implementation admission contract, hardening pressure test, Live Validation repo-truth and waiver classification, PR Readiness merge-target canon, and PR-R1 release-floor validator repair.
Release Artifacts: Tag v1.6.1-prebeta; release title Pre-Beta v1.6.1; inclusion-only release notes summarize the FB-031 UI/UX architecture milestone, source-map and lifecycle/state boundaries, validation/admission contract, hardening result, Live Validation waivers, clean branch history, and PR-R1 validator repair.
Post-Release Truth: FB-031 is Released / Closed in v1.6.1-prebeta; release debt is clear; FB-032 PR Readiness is green on PR #73.
Summary: Preserved Nexus-era UI/UX overhaul planning as a deliberate design lane rather than piecemeal visual drift.
Why it matters: The Nexus-era visual language should be planned coherently before any later UI implementation pass.

### [ID: FB-040] Monitoring, thermals, and performance HUD surface

Status: Released (v1.6.0-prebeta)
Record State: Closed
Priority: Medium
Release Stage: pre-Beta
Target Version: v1.6.0-prebeta
Release Title: Pre-Beta v1.6.0
Branch: feature/fb-040-monitoring-thermals-performance-hud-surface
Canonical Workstream Doc: Docs/workstreams/FB-040_monitoring_thermals_performance_hud_surface.md
Release Target: v1.6.0-prebeta
Release Floor: minor prerelease (historical published tag; future architecture-only milestones must not use minor solely because they define a planning lane)
Version Rationale: FB-040 was published as `v1.6.0-prebeta`; post-release repair records the live release as canonical while governance now treats architecture-only, non-user-facing planning/admission milestones as patch-floor by default unless they deliver an executable or user-facing capability lane.
Release Scope: Architecture-only monitoring and thermal source mapping, ownership vocabulary, lifecycle/trust-safety framing, validation/admission contract definition, hardening pressure test, and Live Validation waiver truth for the current non-user-facing milestone.
Release Artifacts: Tag v1.6.0-prebeta; release title Pre-Beta v1.6.0; inclusion-only release notes summarize the FB-040 monitoring and thermal architecture milestone, source-map boundaries, lifecycle/trust-safety handling, validation/admission contract, hardening result, and Live Validation waivers.
Post-Release Truth: FB-040 is Released / Closed in v1.6.0-prebeta; release debt is clear; FB-031 Branch Readiness is admitted on `feature/fb-031-nexus-desktop-ai-ui-ux-overhaul-planning`.
Version Drift Note: FB-040 advanced the public prerelease from `v1.5.0-prebeta` to `v1.6.0-prebeta`; because the delivered milestone was architecture-only and non-user-facing, future equivalent milestones must use patch prerelease advancement unless a true runtime, executable, or user-facing capability lane is delivered.
Summary: Track future runtime monitoring and HUD surfaces for GPU / CPU thermals and performance, including possible plugin-fed telemetry inputs.
Why it matters: Monitoring overlays are a separate runtime and status surface and should not be bolted onto the saved-action system without an explicit product boundary.

### [ID: FB-039] External trigger and plugin integration architecture

Status: Released (v1.5.0-prebeta)
Record State: Closed
Priority: Medium
Release Stage: pre-Beta
Target Version: v1.5.0-prebeta
Release Title: Pre-Beta v1.5.0
Branch: feature/fb-039-external-trigger-plugin-integration-architecture
Canonical Workstream Doc: Docs/workstreams/FB-039_external_trigger_plugin_integration_architecture.md
Release Target: v1.5.0-prebeta
Release Floor: minor prerelease
Version Rationale: FB-039 created the external trigger and plugin integration architecture lane with an internal trigger intake boundary, so it was a new pre-Beta capability lane rather than patch-only UX, sequencing, or governance repair.
Release Scope: Internal-only external trigger intake architecture and runtime boundary, including source map, ownership vocabulary, lifecycle/trust framing, in-memory registration, bounded invocation follow-through, lifecycle transitions, decision evidence, boundary snapshots, readiness inspection, readiness sweep, readiness summary, and readiness detail snapshot.
Release Artifacts: Tag v1.5.0-prebeta; release title Pre-Beta v1.5.0; inclusion-only release notes summarize the FB-039 internal-only trigger intake milestone, capabilities, system behavior, validation evidence, and Live Validation waivers.
Post-Release Truth: FB-039 is Released / Closed in v1.5.0-prebeta; release debt is clear; FB-040 Branch Readiness is admitted on `feature/fb-040-monitoring-thermals-performance-hud-surface`.
Summary: Track future plugin and integration lifecycle design for external trigger surfaces such as Stream Deck and other installed integration points.
Why it matters: Plugin-backed action triggering needs explicit lifecycle, safety, and ownership boundaries before it becomes part of the product.

### [ID: FB-038] Taskbar / tray quick-task UX and Create Custom Task surface

Status: Released (v1.4.1-prebeta)
Record State: Closed
Priority: Medium
Release Stage: pre-Beta
Target Version: v1.4.1-prebeta
Release Title: Pre-Beta v1.4.1
Canonical Workstream Doc: Docs/workstreams/FB-038_taskbar_tray_quick_task_ux.md
Summary: Released the FB-038 tray quick-task UX milestone, including tray identity/discoverability, tray Open Command Overlay, tray Create Custom Task dialog-open/no-write route, tray-origin create completion through the existing FB-036 authoring path, catalog reload and exact-match resolution, confirm/result execution, and startup first-visible Core Visualization sequencing repair.
Why it matters: Taskbar and tray interaction now has an explicit released UX lane that remains bounded to the shared action model rather than becoming a parallel authoring or launcher surface.

### [ID: FB-037] Curated built-in system actions and Nexus settings expansion

Status: Released (v1.4.0-prebeta)
Record State: Closed
Priority: High
Release Stage: pre-Beta
Target Version: v1.4.0-prebeta
Canonical Workstream Doc: Docs/workstreams/FB-037_built_in_actions_and_settings_expansion.md
Summary: Released the first curated Windows utility built-in catalog under the shared action model, including Task Manager, Calculator, Notepad, and Paint while preserving saved-action override authority, authoring collision protection, confirm/result surfaces, and callable-group behavior.
Why it matters: Standard product actions now feel native and inspectable under the shared action model instead of being pushed into user-defined saved actions as ad hoc customization. Common Windows actions ship as first-class built-ins, while saved actions remain the seam for personal or non-standard tasks.

### [ID: FB-041] Deterministic callable-group execution layer

Status: Released (v1.3.1-prebeta)
Record State: Closed
Priority: High
Release Stage: pre-Beta
Target Version: v1.3.1-prebeta
Canonical Workstream Doc: Docs/workstreams/FB-041_deterministic_callable_group_execution_layer.md
Summary: Released the first bounded callable-group follow-through execution layer for deterministic linear member execution in stored order with stop-on-failure, terminal success or failure propagation, and runtime progression markers.
Why it matters: FB-041 closes the released FB-036 callable-group execution follow-through by supporting full stored-order group execution without reopening authoring, changing single-action behavior, or widening into scheduling, branching, retries, nested groups, or parallelism.

### [ID: FB-036] Limited saved-action authoring and type-first custom task UX

Status: Released (v1.3.0-prebeta)
Record State: Closed
Priority: High
Release Stage: pre-Beta
Target Version: v1.3.0-prebeta
Canonical Workstream Doc: Docs/workstreams/FB-036_saved_action_authoring.md
Summary: Released the bounded custom-task authoring, callable-group management, inline group quick-create, and exact-green validation hardening milestone above the locked FB-027 interaction baseline.
Why it matters: Nexus now supports deliberate in-product custom-task and callable-group authoring without reopening the typed-first overlay contract, widening into Action Studio, or weakening exact-match resolution boundaries.

### [ID: FB-027] Interaction system baseline and shared action model

Status: Released (v1.2.9-prebeta)
Record State: Closed
Priority: High
Release Stage: pre-Beta
Target Version: v1.2.9-prebeta
Canonical Workstream Doc: Docs/workstreams/FB-027_interaction_system_baseline.md
Summary: Lock the typed-first interaction baseline and deliver bounded shared-action follow-through through the released URL-target milestone plus the later released saved-action inventory and guided-access milestone.
Why it matters: Future interaction work needs one authoritative baseline and truthful released-state posture so the URL-target milestone and the later inventory-and-guided-access milestone remain visible as bounded released steps rather than drifting back into ambiguous follow-through language.

### [ID: FB-025] Boot and desktop milestone taxonomy clarification

Status: Released (v1.2.5-prebeta)
Record State: Closed
Priority: Low
Release Stage: pre-Beta
Target Version: v1.2.5-prebeta
Canonical Workstream Doc: Docs/workstreams/FB-025_boot_desktop_milestone_taxonomy_clarification.md
Summary: Clarified shared milestone taxonomy between `BOOT_MAIN|...` and `RENDERER_MAIN|...` without collapsing ownership.
Why it matters: Keeps boot and desktop evidence easier to compare while preserving separate ownership boundaries.

### [ID: FB-028] Relocate launcher history state out of root logs

Status: Released (v1.2.3-prebeta)
Record State: Closed
Priority: Medium
Release Stage: pre-Beta
Target Version: v1.2.3-prebeta
Canonical Workstream Doc: Docs/workstreams/FB-028_history_state_relocation.md
Summary: Moved launcher-owned historical state out of the live root logs tree into a dedicated state location.
Why it matters: Keeps historical state out of user-visible runtime logs while preserving behavior and fallback rules.

### [ID: FB-033] Dev-only startup snapshot harness follow-through

Status: Released (v1.2.4-prebeta)
Record State: Closed
Priority: Medium
Release Stage: pre-Beta
Target Version: v1.2.4-prebeta
Canonical Workstream Doc: Docs/workstreams/FB-033_startup_snapshot_harness_follow_through.md
Summary: Stabilized the env-gated startup snapshot harness as bounded dev-only debugging infrastructure.
Why it matters: Preserves a repeatable startup evidence path without turning it into normal user-facing behavior.

### [ID: FB-034] Recoverable incident diagnostics surface and failure-class follow-through

Status: Released (v1.2.6-prebeta)
Record State: Closed
Priority: Medium
Release Stage: pre-Beta
Target Version: v1.2.6-prebeta
Canonical Workstream Doc: Docs/workstreams/FB-034_recoverable_diagnostics.md
Summary: Closed the first recoverable-diagnostics milestone for one explicitly bounded repeated-identical `launch_failed` incident class.
Why it matters: Makes the Class 2/Class 3 boundary explicit without widening diagnostics policy or breaking the manual-reporting boundary.

### [ID: FB-035] Support-report release-context fallback hardening

Status: Released (v1.2.7-prebeta)
Record State: Closed
Priority: Medium
Release Stage: pre-Beta
Target Version: v1.2.7-prebeta
Canonical Workstream Doc: Docs/workstreams/FB-035_release_context_fallback_hardening.md
Summary: Hardened support-report fallback release-context derivation so generated artifacts use released-canon truth when `.git` metadata is unavailable.
Why it matters: Prevents support bundles and issue drafts from reporting an unreleased higher planned prerelease.

## Historical Implemented Registry-Only Items

### [ID: FB-001] Repeated identical crash early escalation

Status: Implemented (v1.6.0)
Record State: Registry-only
Priority: Medium
Target Version: v1.6.0
Summary: Early launcher escalation for repeated identical non-`STARTUP_ABORT` crash outcomes.
Why it matters: Prevents stable repeated crash evidence from being masked by unnecessary retries.

### [ID: FB-002] Mixed failure-pattern policy

Status: Implemented (v1.6.0)
Record State: Registry-only
Priority: Medium
Target Version: v1.6.0
Summary: Conservative launcher handling for mixed crash and abort failure sequences.
Why it matters: Keeps mixed-pattern outcomes classified without overstating them as stronger than repeated identical failures.

### [ID: FB-003] Retry limit and diagnostics escalation policy

Status: Implemented (v1.9.0 rev1)
Record State: Registry-only
Priority: Medium
Target Version: v1.9.0
Summary: Defined retry exhaustion and diagnostics-entry policy for repeated `STARTUP_ABORT` and repeated identical crash outcomes.
Why it matters: Makes launcher escalation predictable and evidence-based.

### [ID: FB-006] Threshold-based recovery outcome summary refinement

Status: Implemented (v1.6.0)
Record State: Registry-only
Priority: Low
Target Version: v1.6.0
Summary: Refined launcher summary wording for threshold-based early escalation outcomes.
Why it matters: Keeps final failed-run reporting aligned with the actual recovery path.

### [ID: FB-007] Max-attempt identical-failure attempt-pattern correction

Status: Implemented (v1.6.0)
Record State: Registry-only
Priority: Low
Target Version: v1.6.0
Summary: Corrected final attempt-pattern reporting for max-attempt identical failures.
Why it matters: Prevents stable repeated failures from being described as varied.

### [ID: FB-008] Shutdown voice degradation effect

Status: Implemented (v2.2.0 rev2)
Record State: Registry-only
Priority: Low
Target Version: v2.2.0
Summary: Tuned the shutdown-only voice path so the final line sounds more like controlled power loss.
Why it matters: Improves late-shutdown presentation without widening diagnostics behavior.

### [ID: FB-009] Align crash-origin mixed markers with stable repeated-failure summaries

Status: Implemented (v1.6.0)
Record State: Registry-only
Priority: Low
Target Version: v1.6.0
Summary: Aligned mixed-pattern classification with final repeated-failure summaries when cause stayed identical.
Why it matters: Keeps summary and classification evidence consistent.

### [ID: FB-010] v1.6.0 closeout and documentation sync

Status: Implemented (v1.6.0)
Record State: Registry-only
Priority: Medium
Target Version: v1.6.0
Summary: Historical closeout and documentation sync for the finalized `v1.6.0` orchestration layer.
Why it matters: Preserved the old baseline before later historical-memory work.

### [ID: FB-011] Historical memory contract

Status: Implemented (v1.7.0)
Record State: Registry-only
Priority: High
Target Version: v1.7.0
Summary: Defined the contract for passive cross-run historical memory before implementation.
Why it matters: Keeps later history and advisory work deterministic and explainable.

### [ID: FB-012] Failure fingerprint and recurrence model

Status: Implemented (v1.8.0)
Record State: Registry-only
Priority: High
Target Version: v1.8.0
Summary: Defined how recurring outcomes are recognized across launches without reopening closed runtime classification.
Why it matters: Cross-run recurrence needs stable fingerprint rules to stay trustworthy.

### [ID: FB-013] Advisory provenance and confidence semantics

Status: Implemented (v1.8.0)
Record State: Registry-only
Priority: Medium
Target Version: v1.8.0
Summary: Defined provenance and confidence semantics for advisory outputs.
Why it matters: Keeps advisory intelligence explanatory instead of becoming hidden policy.

### [ID: FB-014] Multi-run orchestration regression harness

Status: Implemented (v1.8.0 rev1)
Record State: Registry-only
Priority: Medium
Target Version: v1.8.0
Summary: Added a multi-run regression harness for orchestration and historical-memory validation.
Why it matters: Gives repeated-run behavior a bounded regression surface.

### [ID: FB-016] Recorder-only historical memory groundwork

Status: Implemented (v1.7.0)
Record State: Registry-only
Priority: High
Target Version: v1.7.0
Summary: Established recorder-only groundwork for passive historical memory.
Why it matters: Kept early history capture bounded before broader interpretation layers arrived.

### [ID: FB-017] Support bundle and GitHub issue prefill

Status: Implemented (v1.9.0 rev1)
Record State: Registry-only
Priority: Medium
Target Version: v1.9.0
Summary: Added support-bundle creation and issue-prefill groundwork around diagnostics workflows.
Why it matters: Improved manual triage and reporting without automatic submission.

### [ID: FB-018] Voice-path regression validation harness

Status: Implemented (v1.9.0 rev1)
Record State: Registry-only
Priority: Medium
Target Version: v1.9.0
Summary: Added bounded regression coverage for voice-path behavior.
Why it matters: Protects shutdown and diagnostics voice behavior from silent regression.

### [ID: FB-019] Support bundle to repro triage helper

Status: Implemented (v1.9.0 rev1)
Record State: Registry-only
Priority: Medium
Target Version: v1.9.0
Summary: Added a helper path for turning support-bundle artifacts into reproducible triage input.
Why it matters: Improves internal debugging flow without changing product behavior.

### [ID: FB-020] Dev Toolkit utility split and dev-only evidence roots

Status: Implemented (v2.0 rev2)
Record State: Registry-only
Priority: High
Target Version: v2.0
Summary: Split Dev Toolkit utilities and formalized dev-only evidence roots.
Why it matters: Keeps internal debugging surfaces structured and separate from live runtime logs.

### [ID: FB-021] Dev-only Boot Jarvis test lane

Status: Implemented (v2.1.0 rev1)
Record State: Registry-only
Priority: High
Target Version: v2.1.0
Summary: Added the first dev-only boot test lane for controlled boot-path validation.
Why it matters: Made boot-path validation explicit and reusable inside the toolkit surface.

### [ID: FB-022] Boot & Transition Checks Dev Toolkit surfacing

Status: Implemented (v2.1.0 rev2)
Record State: Registry-only
Priority: Medium
Target Version: v2.1.0
Summary: Surfaced Boot and Transition Checks inside the Dev Toolkit.
Why it matters: Made transition validation easier to run without ad hoc helper discovery.

### [ID: FB-023] Desktop renderer observability gap closure

Status: Implemented (v2.1.0 rev3)
Record State: Registry-only
Priority: High
Target Version: v2.1.0
Summary: Closed key renderer observability gaps needed for desktop-startup investigation.
Why it matters: Strengthened evidence quality for renderer-owned behavior without broad redesign.

### [ID: FB-024] Boot harness edge-path observability refinement

Status: Implemented (v2.1.0 rev4)
Record State: Registry-only
Priority: Medium
Target Version: v2.1.0
Summary: Refined boot-harness observability for edge-path behavior.
Why it matters: Improved branch and validation clarity for boot edge cases.

### [ID: FB-026] Dev Toolkit uploaded-bundle intake surface

Status: Implemented (v2.2.0 rev1)
Record State: Registry-only
Priority: Medium
Target Version: v2.2.0
Summary: Added a dedicated Dev Toolkit intake surface for uploaded support bundles and extracted folders.
Why it matters: Makes internal bundle triage feel like one coherent tooling surface.
