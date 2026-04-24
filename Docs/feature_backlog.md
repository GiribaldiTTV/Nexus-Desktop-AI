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

None.

## Active Promoted Workstream

- `Docs/workstreams/FB-042_desktop_entrypoint_runtime_refinement.md`

FB-042 Desktop entrypoint runtime refinement now owns merged-unreleased release debt for `v1.6.7-prebeta`. Latest public prerelease truth remains `v1.6.6-prebeta`; `Repo State` is `No Active Branch`; WS-1 desktop shortcut launch-path runtime refinement is complete and validated; H-1 launch-path hardening is complete and green; LV-1 is complete with real desktop shortcut evidence and a narrow User Test Summary waiver; and file-frozen Release Readiness is next on updated `main`, while broader `main.py` reshaping plus broader workspace follow-through remain explicitly deferred to a later bounded successor lane.
Released baseline truth is aligned: FB-040 is released and closed in `v1.6.0-prebeta`, FB-031 is released and closed in `v1.6.1-prebeta`, FB-032 is released and closed in `v1.6.2-prebeta`, FB-004 is released and closed in `v1.6.3-prebeta`, FB-015 plus FB-029 are released and closed in `v1.6.4-prebeta`, FB-030 is released and closed in `v1.6.5-prebeta`, and FB-005 is now released and closed in `v1.6.6-prebeta`.
FB-039 is released and closed in `v1.5.0-prebeta`.
FB-038 remains released and closed in `v1.4.1-prebeta`.

## Current Branch Readiness Posture

Merged-Unreleased Release-Debt Owner: FB-042 Desktop entrypoint runtime refinement.
Repo State: No Active Branch.
Latest Public Prerelease: v1.6.6-prebeta.
Latest Public Release Commit: deeaa691a79dd01897f6aed82f087970db7019b3.
Latest Public Prerelease Publication: https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.6-prebeta.
Latest Public Prerelease Title: Pre-Beta v1.6.6.
Release Debt: Active after merge until `v1.6.7-prebeta` is published, validated, and post-release canon closure completes.
Current Active Workstream: None.
Current Active Workstream Before Merge: FB-042 Desktop entrypoint runtime refinement.
Active Branch: None.
Active Branch Before Merge: feature/fb-042-desktop-entrypoint-runtime-refinement.
Selected Next Workstream: FB-043 Top-level desktop entrypoint ownership and main.py handoff refinement.
Historical Branch Readiness State: Complete on `feature/fb-005-workspace-path-planning`.
Current Branch Readiness State: Complete on `feature/fb-042-desktop-entrypoint-runtime-refinement`.
Historical Workstream State: WS-1 `desktop/orin_desktop_test.py` -> `dev/desktop/orin_desktop_test.py` is complete.
Merged-Unreleased Workstream State: WS-1 desktop shortcut launch-path runtime refinement is complete and validated. H-1 launch-path hardening is complete and green. LV-1 is complete. PR Readiness is complete, and the merge-target package is now routed to file-frozen Release Readiness for `v1.6.7-prebeta`.
Historical Hardening State: Complete on `feature/fb-005-workspace-path-planning`.
Historical Live Validation State: Complete on `feature/fb-005-workspace-path-planning`.
PR Readiness State: Complete on `feature/fb-042-desktop-entrypoint-runtime-refinement`; live PR state is recorded in the canonical FB-042 workstream doc.
Release Execution State: `v1.6.6-prebeta` is live at https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.6-prebeta on commit `deeaa691a79dd01897f6aed82f087970db7019b3`.
Admitted Workstream Chain: WS-1 desktop shortcut launch-path runtime refinement is complete and validated. No WS-2 or later seam is admitted yet.

## Backlog Governance Sync

Last Reviewed: 2026-04-24 during FB-042 LV-1 WS-1 live validation.

Open-candidate priority review:

- FB-004 is released and closed in `v1.6.3-prebeta`; it is no longer an active or selected-next branch candidate.
- FB-015 is released and closed in `v1.6.4-prebeta`; it no longer owns release debt or active branch truth.
- FB-029 is released and closed in `v1.6.4-prebeta`; it no longer owns release debt or active branch truth.
- FB-030 remains `Medium` as historical planning priority, but it is now Released / Closed in `v1.6.5-prebeta` and no longer owns release debt or active branch truth.
- FB-005 remains `Low` as historical workspace priority, but it is now Released / Closed in `v1.6.6-prebeta` and no longer owns release debt or selected-next truth.
- FB-042 now owns merged-unreleased release debt for `v1.6.7-prebeta`; the bounded runtime/user-facing launch-path slice is complete, and merge-target canon is in `No Active Branch` posture for release packaging.
- FB-043 is selected next as the smallest runtime-bearing successor lane and remains branch-not-created until FB-042 release packaging clears.

Current-branch clarity: latest public prerelease is `v1.6.6-prebeta`; FB-005 is Released / Closed and release debt is clear; FB-042 now owns merged-unreleased release debt for `v1.6.7-prebeta` with `Repo State: No Active Branch`; and FB-043 is selected next as a branch-not-created runtime/user-facing successor lane focused on top-level desktop entrypoint ownership and `main.py` handoff refinement.

## Registry Items

### [ID: FB-005] Workspace and folder organization

Status: Released (v1.6.6-prebeta)
Record State: Closed
Priority: Low
Release Stage: Released
Target Version: v1.6.6-prebeta
Release Title: Pre-Beta v1.6.6
Deferred Since: v2.0 closeout after the Step 4 workspace slice; the earlier first workspace slice is preserved in v1.9.0 closeout history.
Deferred Because: remaining workspace movement is path-sensitive and can break imports, launcher routes, logs, or user-facing entrypoints if treated as casual cleanup.
Selection / Unblock: Implemented for the first bounded slice. `feature/fb-005-workspace-path-planning` completed the admitted WS-1 relocation `desktop/orin_desktop_test.py` -> `dev/desktop/orin_desktop_test.py`, the branch merged through PR #83, and `v1.6.6-prebeta` is now published and validated.
Branch: feature/fb-005-workspace-path-planning
Canonical Workstream Doc: Docs/workstreams/FB-005_workspace_and_folder_organization.md
Branch Readiness: Complete. The branch objective, target end-state, approved workspace/path slice, validation contract, User Test Summary strategy, later-phase expectations, and first Workstream seam are recorded in the canonical workstream doc.
Workstream: WS-1 `desktop/orin_desktop_test.py` -> `dev/desktop/orin_desktop_test.py` is complete. H-1 is complete. LV-1 is complete. No WS-2 is admitted yet; later slices remain explicit approval gates.
PR Readiness: Complete. PR-1 merge-target canon completeness, PR-2 selected-next workstream selection, and PR-3 live PR creation plus validation are complete; PR #83 merged into `main` at `873c9b6801802a05bbcef074595e632c0ec9f1d2`.
Release Readiness: Complete. `main` validated green for `v1.6.6-prebeta` release packaging before release execution.
Release Execution: `v1.6.6-prebeta` is live at https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.6-prebeta on commit `deeaa691a79dd01897f6aed82f087970db7019b3`.
Release Target: v1.6.6-prebeta
Release Floor: patch prerelease
Version Rationale: FB-005 delivers a bounded dev-only workspace/path implementation slice and direct path-truth sync with no change to shipped runtime entrypoints, launcher paths, audio paths, logs, visual assets, installer behavior, or user-facing desktop behavior, so patch prerelease remains the correct floor.
Release Scope: WS-1 dev-only desktop test harness relocation from `desktop/orin_desktop_test.py` to `dev/desktop/orin_desktop_test.py`, local path-math preservation, direct workspace-layout truth sync, hardening corrections, Live Validation waivers, PR package history, and release publication for the first admitted FB-005 slice only.
Release Artifacts: Tag v1.6.6-prebeta; release title Pre-Beta v1.6.6; rich Markdown release notes summarize the bounded FB-005 WS-1 workspace slice, validation evidence, non-user-facing release posture, and selected-next planning lane without repeating the release title inside the notes body, and GitHub-generated `## What's Changed` plus `**Full Changelog**:` must be included.
Post-Release Truth: FB-005 is Released / Closed in v1.6.6-prebeta; release debt is clear; and FB-042 is the active promoted implementation workstream on `feature/fb-042-desktop-entrypoint-runtime-refinement`, with Branch Readiness complete and WS-1 desktop shortcut launch-path runtime refinement complete / validated.
Selected Next Workstream: FB-043 Top-level desktop entrypoint ownership and main.py handoff refinement
Next-Branch Creation Gate: After FB-042 merges, `v1.6.7-prebeta` is published and validated, updated `main` is revalidated, and FB-043 Branch Readiness admits one bounded runtime-bearing top-level entrypoint slice; branch creation remains blocked until then.
Minimal Scope: Complete only the admitted WS-1 dev-only desktop test harness relocation from `desktop/orin_desktop_test.py` to `dev/desktop/orin_desktop_test.py`, with direct reference sync and no broader workspace movement.
Summary: Continue workspace organization only through explicitly approved path-sensitive slices, beginning with the now-completed dev-only desktop test harness move.
Why it matters: Keeps folder and ownership cleanup deliberate instead of letting it blur into unrelated feature work.

### [ID: FB-042] Desktop entrypoint runtime refinement

Status: Merged unreleased
Record State: Promoted
Priority: Low
Release Stage: Merged unreleased
Target Version: v1.6.7-prebeta
Selection / Unblock: Reoriented on the current branch lineage from a planning-only Step 5 bucket into a runtime-bearing implementation lane so FB-042 could begin with real desktop entrypoint/user-facing progress instead of another docs-only Workstream. Branch Readiness is complete, the branch is renamed to match the admitted work, WS-1 desktop shortcut launch-path runtime refinement is complete and validated, and merge-target canon is now packaged for `v1.6.7-prebeta`.
Branch: feature/fb-042-desktop-entrypoint-runtime-refinement
Canonical Workstream Doc: Docs/workstreams/FB-042_desktop_entrypoint_runtime_refinement.md
Branch Readiness: Complete. Planning/framing now happens before Workstream, and the admitted WS-1 slice is recorded with owned paths, non-goals, validation coverage, rollback limits, and user-facing shortcut contract in the canonical workstream doc.
Workstream: Complete through WS-1. WS-1 desktop shortcut launch-path runtime refinement is complete and validated on the real `launch_orin_desktop.vbs` -> `desktop/orin_desktop_launcher.pyw` -> `desktop/orin_desktop_main.py` path, H-1 hardening is complete, LV-1 is complete, and PR Readiness is complete.
Branch Meaning: Historical source-branch execution owned the real desktop entrypoint/runtime launch path. Merge-target canon after PR packaging is `No Active Branch`, while FB-042 carries merged-unreleased release debt for `v1.6.7-prebeta`.
Release Target: v1.6.7-prebeta
Release Floor: patch prerelease
Version Rationale: FB-042 delivers a bounded runtime/user-facing launch-path reliability and startup-error-handling refinement on the existing desktop entrypoint path, but it does not introduce a new product lane, broader runtime family, or materially expanded capability beyond the shipped launch chain.
Release Scope: WS-1 launch-path fallback hardening in `launch_orin_desktop.vbs`, direct user-facing startup failure dialog handling when no usable windowed Python launcher exists, launch-chain validator expansion across default and forced-fallback VBS paths, H-1 fallback-contract correction for `py -0p` / Python 3 launcher proof, real desktop shortcut validation evidence, PR package history, and merged-unreleased release-debt truth for the bounded FB-042 runtime slice only.
Release Artifacts: Tag v1.6.7-prebeta; release title Pre-Beta v1.6.7; rich Markdown release notes summarize the bounded FB-042 desktop launch-path runtime refinement, fallback hardening, real shortcut evidence, and selected-next top-level entrypoint successor lane without repeating the release title inside the notes body, and GitHub-generated `## What's Changed` plus `**Full Changelog**:` must be included.
Post-Release Truth: FB-042 is Released / Closed in `v1.6.7-prebeta` after publication and validation; release debt then clears, and FB-043 Branch Readiness may begin only after updated `main` is revalidated and one bounded runtime-bearing top-level desktop entrypoint slice is admitted.
Selected Next Workstream: FB-043 Top-level desktop entrypoint ownership and main.py handoff refinement
Next-Branch Creation Gate: After FB-042 merges, `v1.6.7-prebeta` is published and validated, updated `main` is revalidated, and FB-043 Branch Readiness admits one bounded runtime-bearing top-level entrypoint slice; branch creation remains blocked until then.
Minimal Scope: Execute only WS-1 desktop shortcut launch-path runtime refinement across `launch_orin_desktop.vbs`, `desktop/orin_desktop_launcher.pyw`, `desktop/orin_desktop_main.py`, and `dev/orin_desktop_entrypoint_validation.py`, while keeping `main.py`, broader workspace follow-through, audio, logs, visual assets, and installer redesign out of scope.
Summary: Start FB-042 on the real desktop launch path users actually touch instead of reopening a broader planning-only Step 5 bucket.
Why it matters: Creates actual runtime/user-facing follow-through now while keeping larger entrypoint and workspace reshaping bounded and explicit.

### [ID: FB-043] Top-level desktop entrypoint ownership and main.py handoff refinement

Status: Selected
Record State: Registry-only
Priority: High
Selection / Unblock: Select after FB-042 because the next highest-value runtime-bearing follow-through is the still-ambiguous top-level desktop entrypoint handoff across `main.py` and the shipped launcher chain. Branch Readiness must keep planning/framing bounded and end by admitting one runtime/user-facing implementation seam rather than another docs-only lane.
Branch: Not created
Canonical Workstream Doc: Not created yet
Branch Readiness: Not started. It must record affected-surface ownership across `main.py`, `launch_orin_desktop.vbs`, `desktop/orin_desktop_launcher.pyw`, `desktop/orin_desktop_main.py`, and `dev/orin_desktop_entrypoint_validation.py`, then admit one bounded runtime-bearing slice.
Next Workstream: Selected
Minimal Scope: Complete Branch Readiness for a bounded top-level desktop entrypoint ownership and handoff refinement slice across `main.py`, `launch_orin_desktop.vbs`, `desktop/orin_desktop_launcher.pyw`, `desktop/orin_desktop_main.py`, and `dev/orin_desktop_entrypoint_validation.py`, then admit one implementation seam that reduces top-level handoff ambiguity without widening into `Audio/`, `logs/`, `jarvis_visual/`, installer work, or broader workspace reshaping.
Summary: Continue the desktop entrypoint runtime lane by clarifying and tightening top-level ownership and handoff on the shipped launch path.
Why it matters: Builds directly on FB-042's user-facing launch-path improvement and keeps the next branch implementation-bearing instead of slipping back into planning-only governance work.

### [ID: FB-015] Boot and desktop phase-boundary model

Status: Released (v1.6.4-prebeta)
Record State: Closed
Priority: High
Release Stage: Slice-staged
Target Version: v1.6.4-prebeta
Release Title: Pre-Beta v1.6.4
Deferred Since: v2.0 closeout after the FB-015 rev1a phase-boundary clarification.
Deferred Because: the boot/desktop ownership model is clarified at planning level, but no later implementation-facing boundary change has been admitted.
Selection / Unblock: Select when a concrete boot, desktop, startup, trust, or orchestration lane is blocked by unresolved ownership boundaries; Branch Readiness must name the exact ambiguity it resolves.
Priority Review: Raised to High during the FB-004 pre-PR docs governance sync because boot/desktop phase-boundary follow-through is the clearest routine technical successor after FB-004 unless an explicitly approved product/legal, voice, or workspace lane supersedes it.
Branch: feature/fb-015-boot-desktop-phase-boundary-model
Canonical Workstream Doc: Docs/workstreams/FB-015_boot_and_desktop_phase_boundary_model.md
Branch Readiness: Complete. The branch objective, target end-state, seam families, validation contract, User Test Summary strategy, later-phase expectations, and first Workstream seam are recorded in the canonical workstream doc.
Workstream: WS-1 current boot/desktop boundary inventory and ownership map, WS-2 lifecycle and phase-boundary state framing, and WS-3 validation and admission contract for future boot/desktop boundary implementation are complete.
Hardening: H-1 pressure test of the boot/desktop boundary inventory and ownership map, lifecycle and phase-boundary state framing, and future implementation admission contract is complete.
Live Validation: LV-1 repo-truth alignment, user-facing shortcut applicability, User Test Summary applicability, desktop export applicability, cleanup posture, and waiver handling are complete.
PR Readiness: PR-1 merge-target canon completeness, PR-2 selected-next workstream selection, and PR-3 live PR creation plus authenticated PR state validation are complete; PR #75 merged cleanly into `main` at `3e821e07ff91d814fd7aba9b50819f97d700a301`.
Release Readiness: Complete. `main` validated green for `v1.6.4-prebeta` release packaging before release execution.
Release Execution: `v1.6.4-prebeta` is live at https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.4-prebeta on commit `d2268b71feefa062c8117eae29f8ec17879a724f`.
Release Target: v1.6.4-prebeta
Release Floor: patch prerelease
Version Rationale: FB-015 remains a docs/canon-only boundary inventory, ownership, lifecycle, and implementation-admission milestone with no new executable, runtime, operator-facing, user-facing, or materially expanded product capability.
Release Scope: Boot and desktop phase-boundary inventory, ownership map, lifecycle/state framing, implementation admission contract, hardening corrections, Live Validation waivers, PR package history, post-merge canon repair, and merged-unreleased release-debt truth.
Release Artifacts: Tag v1.6.4-prebeta; release title Pre-Beta v1.6.4; rich Markdown release notes summarize the FB-015 boundary model and governance results without repeating the release title inside the notes body, and GitHub-generated `## What's Changed` plus `**Full Changelog**:` must be included.
Post-Release Truth: FB-015 is Released / Closed in v1.6.4-prebeta; FB-029 is also Released / Closed in the same package; FB-030 is Released / Closed in v1.6.5-prebeta; FB-005 is Released / Closed in v1.6.6-prebeta; FB-042 owns merged-unreleased release debt for `v1.6.7-prebeta`; `Repo State` is `No Active Branch`; and FB-043 is selected next as the branch-not-created top-level desktop entrypoint successor lane.
Minimal Scope: Complete the bounded docs/canon seam chain for current boot/desktop phase-boundary ambiguity, starting with current boundary inventory and ownership mapping before lifecycle framing or implementation-admission rules are extended.
Summary: Preserve the future boot and desktop phase-boundary model above the already-closed milestone taxonomy work.
Why it matters: Keeps boot-versus-desktop ownership planning explicit without reopening the closed taxonomy milestone by inertia.

### [ID: FB-029] ORIN legal-safe rebrand, future ARIA persona option, and repo licensing hardening

Status: Released (v1.6.4-prebeta)
Record State: Closed
Priority: High
Release Stage: pre-Beta
Target Version: v1.6.4-prebeta
Release Title: Pre-Beta v1.6.4
Deferred Since: current pre-Beta identity backlog registration before FB-032 promotion.
Deferred Because: legal-safe naming, ORIN/ARIA persona posture, and licensing hardening need explicit product/legal approval for implementation-facing execution and must not ride along with source-of-truth migration, UI, runtime, or release work.
Selection / Unblock: FB-029 is admitted only as a docs/canon-only planning milestone on this branch. Any implementation-facing naming, licensing, persona, release, or runtime edit still requires explicit product/legal approval and must remain out of scope unless a later legal surface admits it.
Branch: feature/fb-029-orin-identity-licensing-hardening
Canonical Workstream Doc: Docs/workstreams/FB-029_orin_identity_licensing_hardening.md
Branch Readiness: Complete. The branch objective, target end-state, seam families, validation contract, User Test Summary strategy, later-phase expectations, and first Workstream seam are recorded in the canonical workstream doc.
Workstream: WS-1 current identity, persona-option, and licensing source-of-truth inventory, WS-2 canonical vs historical identity, persona-option, and licensing boundary framing, and WS-3 validation and admission contract for future identity and licensing implementation are complete.
Hardening: H-1 pressure test of identity inventory, persona-option framing, licensing boundary framing, and future implementation admission rules is complete.
Live Validation: LV-1 repo-truth alignment, user-facing shortcut applicability, User Test Summary applicability, desktop export applicability, cleanup posture, and waiver handling are complete.
PR Readiness: PR-1 merge-target canon completeness, PR-2 selected-next workstream selection, and PR-3 live PR creation plus authenticated PR state validation are complete; PR #76 merged cleanly into `main` at `0897fab768dc07385f83fab81434ba7926ecc4a1`.
Release Readiness: Included in the validated inherited `v1.6.4-prebeta` package on `main` while FB-015 remained the sole release-debt owner before publication.
Release Execution: `v1.6.4-prebeta` is live at https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.4-prebeta on commit `d2268b71feefa062c8117eae29f8ec17879a724f`.
Release Target: v1.6.4-prebeta
Release Floor: patch prerelease
Version Rationale: FB-029 remains a docs/canon-only identity, persona-option, and licensing-planning milestone with no new executable, runtime, operator-facing, user-facing, or materially expanded product capability.
Release Scope: Identity source-of-truth inventory, persona-option boundary framing, licensing boundary framing, implementation admission contract, hardening corrections, Live Validation waivers, PR package history, merged-unreleased package-state repair, and post-merge current-state cleanup.
Release Artifacts: Tag v1.6.4-prebeta; release title Pre-Beta v1.6.4; rich Markdown release notes summarize the FB-015 boundary model and the FB-029 identity/licensing planning frame without repeating the release title inside the notes body, and GitHub-generated `## What's Changed` plus `**Full Changelog**:` must be included.
Post-Release Truth: FB-029 is Released / Closed in v1.6.4-prebeta; FB-015 is also Released / Closed in the same package; FB-030 is Released / Closed in v1.6.5-prebeta; FB-005 is Released / Closed in v1.6.6-prebeta; FB-042 owns merged-unreleased release debt for `v1.6.7-prebeta`; `Repo State` is `No Active Branch`; and FB-043 is selected next as the branch-not-created top-level desktop entrypoint successor lane.
Minimal Scope: Define the Branch Readiness frame for legal-safe ORIN naming, optional future ARIA persona posture, and repo licensing hardening before any naming, licensing, release, runtime, or persona-facing edits begin; Workstream remains docs/canon only unless a later legal surface explicitly widens scope.
Summary: Track future ORIN-era naming, persona, and licensing hardening work without treating the local rebrand overlay as merged truth.
Why it matters: Product identity, legal posture, and repo ownership still need durable future treatment, but not by accidental carry-forward.

### [ID: FB-030] ORIN voice/audio direction refinement

Status: Released (v1.6.5-prebeta)
Record State: Closed
Priority: Medium
Release Stage: pre-Beta
Target Version: v1.6.5-prebeta
Deferred Since: current pre-Beta voice/persona backlog registration before FB-032 promotion.
Deferred Because: ORIN voice identity needs a deliberate persona-facing direction pass; current voice harness, shutdown-voice, and source-of-truth work do not admit broader voice redesign or execution behavior.
Selection / Unblock: Admitted. The canonical workstream doc now records the explicit voice/audio design goal, affected-surface map, validation boundary, and non-goals separating persona direction from runtime execution.
Branch: feature/fb-030-orin-voice-audio-direction-refinement
Canonical Workstream Doc: Docs/workstreams/FB-030_orin_voice_audio_direction_refinement.md
Branch Readiness: Complete. The branch objective, target end-state, voice/audio design goal, affected-surface map, seam families, validation contract, User Test Summary strategy, later-phase expectations, and first Workstream seam are recorded in the canonical workstream doc.
Workstream: WS-1 current voice/audio surface inventory and ownership map, WS-2 lifecycle and persona-state framing for voice/audio transitions, and WS-3 validation and admission contract for future voice/audio implementation are complete.
Hardening: H-1 pressure test of the voice/audio ownership map, lifecycle/persona-state framing, implementation-admission contract, duplicate-trigger risks, and cross-path conflicts is complete.
Live Validation: LV-1 repo-truth alignment, user-facing shortcut applicability, User Test Summary applicability, desktop export applicability, cleanup posture, and waiver handling are complete.
PR Readiness: PR-1 merge-target canon completeness, PR-2 selected-next workstream selection, and PR-3 live PR creation plus authenticated PR state validation are complete; PR #81 merged cleanly into `main` at `c23adc70e17683d40770bf29571928af95935576`.
Release Readiness: Complete. `main` validated green for `v1.6.5-prebeta` release packaging before release execution.
Release Execution: `v1.6.5-prebeta` is live at https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.5-prebeta on commit `7c2933d6427feb08a1139ba7f5ba2393eb61f1e1`.
Release Target: v1.6.5-prebeta
Release Title: Pre-Beta v1.6.5
Release Floor: patch prerelease
Version Rationale: FB-030 remains a docs/canon-only voice/audio planning and admission milestone with no new executable, runtime, operator-facing, user-facing, or materially expanded product capability.
Release Scope: Voice/audio trigger-surface inventory, playback-authority inventory, transcript/telemetry/history ownership map, lifecycle and persona-state framing, implementation admission contract, hardening corrections, Live Validation waivers, selected-next workspace/path gate, and PR package history.
Release Artifacts: Tag v1.6.5-prebeta; release title Pre-Beta v1.6.5; rich Markdown release notes summarize the FB-030 voice/audio direction planning frame without repeating the release title inside the notes body, and GitHub-generated `## What's Changed` plus `**Full Changelog**:` must be included.
Post-Release Truth: FB-030 is Released / Closed in v1.6.5-prebeta; FB-005 is Released / Closed in v1.6.6-prebeta; FB-042 owns merged-unreleased release debt for `v1.6.7-prebeta`; `Repo State` is `No Active Branch`; and FB-043 is selected next as the branch-not-created top-level desktop entrypoint successor lane.
Selected Next Workstream: FB-043 Top-level desktop entrypoint ownership and main.py handoff refinement
Next-Branch Creation Gate: After FB-042 merges, `v1.6.7-prebeta` is published and validated, updated `main` is revalidated, and FB-043 Branch Readiness admits one bounded runtime-bearing top-level entrypoint slice; branch creation remains blocked until then.
Minimal Scope: Complete the bounded docs/canon voice/audio planning seam chain: current surface inventory and ownership mapping, lifecycle/persona-state framing, and the implementation admission contract before runtime voice/audio changes are considered.
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
