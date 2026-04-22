# Nexus Feature Backlog

This file is the controlled registry for tracked work, deferred planning items, historical implemented items, and future promoted bug identities.

Rules:

- ideas must not be implemented immediately
- ideas must not silently expand current scope
- backlog identity remains controlled and approval-gated
- `Status` is the delivery or work field
- `Record State` is the canonical-record lifecycle field
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

- `Docs/workstreams/FB-039_external_trigger_plugin_integration_architecture.md`

## Active Promoted Workstream

FB-039 External trigger and plugin integration architecture.

Main-facing canon is no longer in steady-state `No Active Branch`; FB-039 Workstream is active on `feature/fb-039-external-trigger-plugin-integration-architecture`.
FB-038 remains released and closed in `v1.4.1-prebeta`.

## Merged-Unreleased Release-Debt Owner

None.

## Registry Items

### [ID: FB-004] Future boot orchestrator layer

Status: Deferred (planning groundwork complete enough to pause)
Record State: Registry-only
Priority: High
Release Stage: Slice-staged
Target Version: v2.0
Summary: Preserve the future top-level boot-orchestrator direction above the desktop launcher without authorizing runtime delivery yet.
Why it matters: Keeps the longer-term boot-to-desktop product direction explicit while current desktop and diagnostics work stays bounded.

### [ID: FB-005] Workspace and folder organization

Status: Deferred (partial implementation through Step 4)
Record State: Registry-only
Priority: Low
Release Stage: Slice-staged
Target Version: v2.0
Summary: Continue workspace organization only through explicitly approved path-sensitive slices.
Why it matters: Keeps folder and ownership cleanup deliberate instead of letting it blur into unrelated feature work.

### [ID: FB-015] Boot and desktop phase-boundary model

Status: Deferred (rev1a clarification complete enough to pause)
Record State: Registry-only
Priority: Medium
Release Stage: Slice-staged
Target Version: v2.0
Summary: Preserve the future boot and desktop phase-boundary model above the already-closed milestone taxonomy work.
Why it matters: Keeps boot-versus-desktop ownership planning explicit without reopening the closed taxonomy milestone by inertia.

### [ID: FB-029] ORIN legal-safe rebrand, future ARIA persona option, and repo licensing hardening

Status: Deferred
Record State: Registry-only
Priority: High
Release Stage: pre-Beta
Target Version: v2.2.1
Summary: Track future ORIN-era naming, persona, and licensing hardening work without treating the local rebrand overlay as merged truth.
Why it matters: Product identity, legal posture, and repo ownership still need durable future treatment, but not by accidental carry-forward.

### [ID: FB-030] ORIN voice/audio direction refinement

Status: Deferred
Record State: Registry-only
Priority: Medium
Release Stage: pre-Beta
Target Version: TBD
Summary: Preserve future ORIN voice-direction refinement as its own bounded persona-facing lane.
Why it matters: Voice identity should be intentional and should not piggyback on unrelated runtime or canon work.

### [ID: FB-031] Nexus Desktop AI UI/UX overhaul planning

Status: Deferred
Record State: Registry-only
Priority: Medium
Release Stage: pre-Beta
Target Version: TBD
Summary: Preserve future UI/UX overhaul planning as a deliberate design lane rather than piecemeal visual drift.
Why it matters: The Nexus-era visual language should be planned coherently when the repo is ready for that design pass.

### [ID: FB-032] Nexus-era vision and source-of-truth migration

Status: Deferred
Record State: Registry-only
Priority: Medium
Release Stage: pre-Beta
Target Version: TBD
Summary: Track the broader Nexus-era vision and source-of-truth migration above the current phase-one canon foundation rebuild.
Why it matters: The repo still needs deeper identity and wording normalization after the foundation layer is rebuilt.

### [ID: FB-039] External trigger and plugin integration architecture

Status: Workstream
Record State: Promoted
Priority: Medium
Release Stage: pre-Beta
Target Version: TBD
Branch: feature/fb-039-external-trigger-plugin-integration-architecture
Canonical Workstream Doc: Docs/workstreams/FB-039_external_trigger_plugin_integration_architecture.md
Minimal Scope: Workstream WS-24 follow-on boundary review is recorded after the WS-1 through WS-5 architecture chain, WS-6 intake skeleton, WS-7 registration/follow-through seam, WS-8 validation/user-test alignment, WS-9 boundary review, WS-10 lifecycle transitions, WS-11 validation tightening, WS-12 boundary review, WS-13 internal decision evidence snapshot, WS-14 validation tightening, WS-15 boundary review, WS-16 internal state snapshot, WS-17 validation tightening, WS-18 boundary review, WS-19 internal readiness inspection, WS-20 validation tightening, WS-21 boundary review, WS-22 internal registry readiness sweep, and WS-23 validation tightening. The runtime surface remains internal-only and in-memory, defaults to reject/defer, and does not wire external listeners, protocols, transports, payload schemas, plugin host, settings UI, saved-action execution, callable-group execution, persistence, audit-log format, runtime marker schema, or release packaging. Any next runtime seam requires a later bounded Workstream admission with exact affected files, validation gates, cleanup expectations, and User Test Summary classification.
Summary: Track future plugin and integration lifecycle design for external trigger surfaces such as Stream Deck and other installed integration points.
Why it matters: Plugin-backed action triggering needs explicit lifecycle, safety, and ownership boundaries before it becomes part of the product.

### [ID: FB-040] Monitoring, thermals, and performance HUD surface

Status: Deferred
Record State: Registry-only
Priority: Medium
Release Stage: pre-Beta
Target Version: TBD
Summary: Track future runtime monitoring and HUD surfaces for GPU / CPU thermals and performance, including possible plugin-fed telemetry inputs.
Why it matters: Monitoring overlays are a separate runtime and status surface and should not be bolted onto the saved-action system without an explicit product boundary.

## Closed Canonical Workstreams

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
