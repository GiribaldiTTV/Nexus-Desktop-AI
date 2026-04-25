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

- latest public prerelease: `v1.6.8-prebeta`
- latest public release commit: `5e695af5fada05e4ad6b25731bce328ede8a09ee`
- latest public prerelease publication: `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.8-prebeta`
- latest public prerelease title: `Pre-Beta v1.6.8`
- merged unreleased non-doc implementation debt exists: yes
- the latest public released implementation milestone is FB-043 Top-level desktop entrypoint ownership and `main.py` handoff refinement in `v1.6.8-prebeta`; FB-042 Desktop entrypoint runtime refinement remains released in `v1.6.7-prebeta`; FB-005 Workspace and folder organization remains released in `v1.6.6-prebeta`; FB-030 ORIN voice/audio direction refinement remains released in `v1.6.5-prebeta`; FB-015 Boot and desktop phase-boundary model plus FB-029 ORIN legal-safe rebrand, future ARIA persona option, and repo licensing hardening remain released in `v1.6.4-prebeta`
- current phase after `v1.6.8-prebeta` release closure: `Release Readiness`
- phase status after `v1.6.8-prebeta` release closure: FB-043 is Released / Closed in `v1.6.8-prebeta`; FB-044 is now the merged-unreleased release-debt owner for `v1.6.9-prebeta`; repo state is `No Active Branch`; the bounded FB-044 slice chain, Hardening, Live Validation, and PR Readiness are complete; and FB-045 is selected next as the branch-not-created runtime/user-facing successor lane.
- current active workstream: none
- current branch after `v1.6.8-prebeta` release closure: none
- next concern: execute file-frozen `Release Readiness` on updated `main` for the merged-unreleased FB-044 `v1.6.9-prebeta` package, then carry post-release canon closure on the next legal feature branch.

That means the released FB-027 interaction baseline, the released FB-036 authoring-and-callable-group milestone, the released FB-041 deterministic callable-group execution milestone, the released FB-037 built-in catalog milestone, the released FB-038 tray quick-task UX milestone, the released FB-039 external trigger intake architecture milestone, the released FB-040 monitoring/thermal architecture milestone, the released FB-031 UI/UX architecture milestone, the released FB-032 source-of-truth migration milestone, the released FB-004 future boot-orchestrator architecture milestone, the released FB-015 plus FB-029 planning milestones, the released FB-030 voice/audio planning milestone, and the released FB-005 bounded workspace-path slice are now part of the current public shared pre-Beta baseline.

## Current Branch Readiness Posture

Merged-Unreleased Release-Debt Owner: FB-044 Boot-to-desktop handoff outcome refinement.
Repo State: No Active Branch.

Latest Public Prerelease: v1.6.8-prebeta
Latest Public Release Commit: 5e695af5fada05e4ad6b25731bce328ede8a09ee
Latest Public Prerelease Publication: https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.8-prebeta
Latest Public Prerelease Title: Pre-Beta v1.6.8
Release Debt: Active after merge until `v1.6.9-prebeta` is published, validated, and post-release canon closure completes.
Current active workstream: None
Current Active Workstream Before Release: FB-044 Boot-to-desktop handoff outcome refinement
Current Active Branch: `None.`
Active Branch Before Release: `feature/fb-044-boot-desktop-handoff-outcome-refinement`
Current Active Branch Record: `None.`
Current Active Canonical Workstream Doc: `Docs/workstreams/FB-044_boot_desktop_handoff_outcome_refinement.md`
Historical Active Workstream Before Release: FB-043 Top-level desktop entrypoint ownership and main.py handoff refinement
Historical Active Branch Before Release: `feature/fb-043-top-level-entrypoint-handoff-refinement`
Earlier Historical Active Workstream Before Release: FB-042 Desktop entrypoint runtime refinement
Earlier Historical Active Branch Before Release: `feature/fb-042-desktop-entrypoint-runtime-refinement`
Selected Next Workstream: FB-045 Active-session relaunch outcome refinement.
Selected Next Record State: Registry-only.
Selected Next Implementation Branch: `Not created.`
Repair-Only Branch Handling: `feature/fb-043-release-debt-marker-repair` is a repair-only `feature/` branch and does not imply Branch Readiness admission or active branch truth for FB-043.
Historical Branch Readiness State: Complete on `feature/fb-043-top-level-entrypoint-handoff-refinement`.
Current Branch Readiness State: Complete on `feature/fb-044-boot-desktop-handoff-outcome-refinement`.
Historical Workstream State: FB-043 WS-1 `main.py` direct-launch handoff refinement, WS-2 explicit launch-intent refinement, H-1 entrypoint hardening, LV-1 live validation, PR Readiness, merge, and release publication are complete historical proof in `v1.6.8-prebeta`.
Merged-Unreleased Workstream State: FB-044 WS-1 `desktop-settled handoff outcome refinement`, H-1 settled-state hardening, LV-1 live validation, and PR-1 / PR-2 / PR-3 are complete and frozen for `v1.6.9-prebeta` release packaging.
Historical Hardening State: Complete on `feature/fb-043-top-level-entrypoint-handoff-refinement`.
Historical Live Validation State: Complete on `feature/fb-043-top-level-entrypoint-handoff-refinement`.
PR Readiness State: Complete on `feature/fb-044-boot-desktop-handoff-outcome-refinement`; live PR package state is recorded in the canonical FB-044 workstream doc.
Release Execution State: `v1.6.8-prebeta` is live at https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.6.8-prebeta on commit `5e695af5fada05e4ad6b25731bce328ede8a09ee`.
Current Branch Objective: complete the merged-unreleased FB-044 boot-to-desktop handoff outcome lane through `v1.6.9-prebeta` release packaging without widening into future boot-orchestrator implementation.
Next Legal Phase: Release Readiness.
Release Target: v1.6.9-prebeta
Release Title: Pre-Beta v1.6.9
Release Floor: patch prerelease
Version Rationale: FB-044 delivers a bounded runtime/user-facing boot-to-desktop settled-outcome refinement on the existing startup family without opening a new product lane or materially expanded runtime family.
Release Scope: completed FB-044 WS-1 desktop-settled handoff outcome refinement across `main.py`, `desktop/orin_desktop_launcher.pyw`, `desktop/orin_desktop_main.py`, `dev/orin_boot_transition_verification.py`, and `dev/orin_desktop_entrypoint_validation.py`, plus H-1 settled-state hardening, LV-1 real desktop shortcut evidence, PR package history, merged-unreleased release-debt truth, and selected-next FB-045 successor lock for the bounded runtime/user-facing slice only.
Release Artifacts: Tag v1.6.9-prebeta; release title Pre-Beta v1.6.9; rich Markdown release notes summarize the bounded FB-044 boot-to-desktop settled-outcome refinement, real shortcut evidence, rollback-hardening result, and the FB-045 successor lane without repeating the release title inside the notes body, and GitHub-generated `## What's Changed` plus `**Full Changelog**:` must be included.
Post-Release Truth: FB-044 is Released / Closed in `v1.6.9-prebeta` after publication and validation; release debt then clears; and FB-045 Branch Readiness may begin only after updated `main` is revalidated and the first bounded runtime/user-facing relaunch slice is admitted.
Next-Branch Creation Gate: After FB-044 merges, `v1.6.9-prebeta` is published and validated, updated `main` is revalidated, and FB-045 Branch Readiness admits the first bounded runtime/user-facing relaunch slice; branch creation remains blocked until then.
Active Workstream Chain: None. After merge, FB-044 becomes the merged-unreleased release-debt owner for `v1.6.9-prebeta`, repo state is `No Active Branch`, and `Release Readiness` is next.

## Merged-Unreleased Release-Debt Owner

### FB-044 Boot-to-desktop handoff outcome refinement

- status: `merged unreleased`
- record state: `Promoted`
- priority: `High`
- canonical workstream doc: `Docs/workstreams/FB-044_boot_desktop_handoff_outcome_refinement.md`
- historical source branch: `feature/fb-044-boot-desktop-handoff-outcome-refinement`
- phase status: Merged unreleased for `v1.6.9-prebeta`; Workstream, Hardening, Live Validation, and PR Readiness are complete; repo state is `No Active Branch`; and FB-045 remains selected next, `Registry-only`, and branch-not-created.
- next legal seam: `Release Readiness` on updated `main`
Release Target: v1.6.9-prebeta
Release Floor: patch prerelease
Version Rationale: FB-044 delivers a bounded runtime/user-facing boot-to-desktop settled-outcome refinement on the existing startup family without opening a new product lane or materially expanded runtime family.
Release Scope: completed FB-044 WS-1 desktop-settled handoff outcome refinement, H-1 settled-state hardening, LV-1 real desktop shortcut evidence, PR package history, merged-unreleased release-debt truth, and selected-next FB-045 successor lock for the bounded runtime/user-facing slice only.
Release Artifacts: Tag v1.6.9-prebeta; release title Pre-Beta v1.6.9; rich Markdown release notes summarize the bounded FB-044 boot-to-desktop settled-outcome refinement, rollback-hardening result, real shortcut evidence, and the FB-045 successor lane without repeating the release title inside the notes body, and GitHub-generated `## What's Changed` plus `**Full Changelog**:` must be included.
Post-Release Truth: FB-044 is Released / Closed in `v1.6.9-prebeta` after publication and validation; release debt then clears; and FB-045 Branch Readiness may begin only after updated `main` is revalidated and the first bounded runtime/user-facing relaunch slice is admitted.

## Selected Next Workstream

- ID: `FB-045`
- Title: `Active-session relaunch outcome refinement`
- Record State: `Registry-only`
- Priority: `High`
- Minimal Scope: Admit the first bounded runtime/user-facing relaunch refinement slice across `main.py`, `desktop/orin_desktop_launcher.pyw`, `desktop/orin_desktop_main.py`, `dev/orin_boot_transition_verification.py`, and `dev/orin_desktop_entrypoint_validation.py`, focused on active-session relaunch ownership, relaunch-settled proof, and rollback visibility, while keeping `Audio/`, `logs/`, `jarvis_visual/`, installer work, and broader future boot-orchestrator implementation out of scope.
- Branch: Not created
- Selection Basis: FB-045 is the smallest repo-grounded runtime/user-facing successor after FB-044 because startup ownership and authoritative settled proof are now explicit, but the active-session relaunch path still spans boot prompts, launcher prompts, runtime relaunch signals, and proof that the relaunched session returns to the same settled outcome cleanly.

## Latest Released Workstream Context

### FB-042 Desktop entrypoint runtime refinement

- status: `released`
- record state: `Closed`
- priority: `Low`
- canonical workstream doc: `Docs/workstreams/FB-042_desktop_entrypoint_runtime_refinement.md`
- branch: `feature/fb-042-desktop-entrypoint-runtime-refinement`
- phase status: Released / Closed in `v1.6.7-prebeta`; PR #86 merged into `main` at `bd25fff6afd089cdc758a0d598eb7a5df520b82b`; PR #87 cleared the final release-debt marker repair; the release is live on commit `8f53d163ad008f7508f55f593b15369749e3ec24`; FB-043 is Released / Closed in `v1.6.8-prebeta`; and FB-044 is now the active promoted workstream on `feature/fb-044-boot-desktop-handoff-outcome-refinement` with WS-1 complete, H-1 settled-state hardening complete, LV-1 live validation complete, and `PR Readiness` next.
- next legal seam: none; this record is now historical released truth.
Release Target: v1.6.7-prebeta
Release Floor: patch prerelease
Version Rationale: FB-042 delivers a bounded runtime/user-facing launch-path reliability and startup-error-handling refinement on the existing desktop entrypoint path without opening a new product lane or materially expanding the runtime family.
Release Scope: WS-1 launch-path fallback hardening in `launch_orin_desktop.vbs`, direct user-facing startup failure dialog handling when no usable windowed Python launcher exists, launch-chain validator expansion across default and forced-fallback VBS paths, H-1 launcher-fallback contract correction, real desktop shortcut validation evidence, and release publication for the bounded runtime slice only.
Release Artifacts: Tag v1.6.7-prebeta; release title Pre-Beta v1.6.7; rich Markdown release notes summarize the bounded FB-042 desktop launch-path runtime refinement, fallback hardening, real shortcut evidence, and the FB-043 successor lane without repeating the release title inside the notes body, and GitHub-generated `## What's Changed` plus `**Full Changelog**:` must be included.
Post-Release Truth: FB-042 is Released / Closed in `v1.6.7-prebeta`; FB-043 is Released / Closed in `v1.6.8-prebeta`; and FB-044 is now the active promoted workstream on `feature/fb-044-boot-desktop-handoff-outcome-refinement` with WS-1 complete, H-1 settled-state hardening complete, LV-1 live validation complete, and `PR Readiness` next.

### FB-043 Top-level desktop entrypoint ownership and main.py handoff refinement

- status: `released`
- record state: `Closed`
- priority: `High`
- canonical workstream doc: `Docs/workstreams/FB-043_top_level_entrypoint_handoff_refinement.md`
- branch: `feature/fb-043-top-level-entrypoint-handoff-refinement`
- phase status: Released / Closed in `v1.6.8-prebeta`; PR #88 merged into `main` at `5e695af5fada05e4ad6b25731bce328ede8a09ee`; the release is live; release debt is clear; and FB-044 now owns the active promoted workstream on `feature/fb-044-boot-desktop-handoff-outcome-refinement`.
- next legal seam: none; this record is now historical released truth.

### FB-005 Workspace and folder organization

- status: `released`
- record state: `Closed`
- priority: `Low`
- canonical workstream doc: `Docs/workstreams/FB-005_workspace_and_folder_organization.md`
- branch: `feature/fb-005-workspace-path-planning`
- phase status: Released / Closed in `v1.6.6-prebeta`; PR #83 merged into `main` at `873c9b6801802a05bbcef074595e632c0ec9f1d2`; the release is live on commit `deeaa691a79dd01897f6aed82f087970db7019b3`; FB-042 is Released / Closed in `v1.6.7-prebeta`; FB-043 is Released / Closed in `v1.6.8-prebeta`; and FB-044 is now the active promoted workstream on `feature/fb-044-boot-desktop-handoff-outcome-refinement` with WS-1 complete, H-1 settled-state hardening complete, LV-1 live validation complete, and `PR Readiness` next.
- next legal seam: none; this record is now historical released truth.
Release Target: v1.6.6-prebeta
Release Floor: patch prerelease
Version Rationale: FB-005 remains a bounded dev-only workspace/path implementation slice with no change to shipped runtime entrypoints, launcher paths, audio paths, logs, visual assets, installer behavior, or user-facing desktop behavior.
Release Scope: the historically released FB-005 WS-1 dev-only desktop test harness relocation from `desktop/orin_desktop_test.py` to `dev/desktop/orin_desktop_test.py`, local path-math preservation, direct workspace-layout truth sync, hardening corrections, Live Validation waivers, PR package history, and release publication for that bounded released slice.
Release Artifacts: Tag v1.6.6-prebeta; release title Pre-Beta v1.6.6; rich Markdown release notes summarize the bounded FB-005 WS-1 workspace slice, validation evidence, non-user-facing release posture, and selected-next planning lane without repeating the release title inside the notes body, and GitHub-generated `## What's Changed` plus `**Full Changelog**:` must be included.
Post-Release Truth: FB-005 is Released / Closed in `v1.6.6-prebeta`; FB-042 is Released / Closed in `v1.6.7-prebeta`; FB-043 is Released / Closed in `v1.6.8-prebeta`; and FB-044 is now the active promoted workstream on `feature/fb-044-boot-desktop-handoff-outcome-refinement` with WS-1 complete, H-1 settled-state hardening complete, LV-1 live validation complete, and `PR Readiness` next.

### FB-030 ORIN voice/audio direction refinement

- status: `released`
- record state: `Closed`
- priority: `Medium`
- canonical workstream doc: `Docs/workstreams/FB-030_orin_voice_audio_direction_refinement.md`
- branch: `feature/fb-030-orin-voice-audio-direction-refinement`
- phase status: Released / Closed in `v1.6.5-prebeta`; PR #81 merged into `main` at `c23adc70e17683d40770bf29571928af95935576`; PR #82 carried the post-merge canon repair; the release is live on commit `7c2933d6427feb08a1139ba7f5ba2393eb61f1e1`; FB-005 is Released / Closed in `v1.6.6-prebeta`; FB-042 is Released / Closed in `v1.6.7-prebeta`; FB-043 is Released / Closed in `v1.6.8-prebeta`; and FB-044 is now the active promoted workstream on `feature/fb-044-boot-desktop-handoff-outcome-refinement` with WS-1 complete, H-1 settled-state hardening complete, LV-1 live validation complete, and `PR Readiness` next.
- next legal seam: none; this record is now historical released truth.
Release Target: v1.6.5-prebeta
Release Floor: patch prerelease
Version Rationale: FB-030 remains a docs/canon-only voice/audio planning and admission milestone with no new executable, runtime, operator-facing, user-facing, or materially expanded product capability.
Release Scope: Voice/audio trigger-surface inventory, playback-authority inventory, transcript/telemetry/history ownership map, lifecycle and persona-state framing, implementation admission contract, hardening corrections, Live Validation waivers, selected-next workspace/path gate, and PR package history.
Release Artifacts: Tag v1.6.5-prebeta; release title Pre-Beta v1.6.5; rich Markdown release notes summarize the FB-030 voice/audio direction planning frame without repeating the release title inside the notes body, and GitHub-generated `## What's Changed` plus `**Full Changelog**:` must be included.
Post-Release Truth: FB-030 is Released / Closed in v1.6.5-prebeta; FB-005 is Released / Closed in v1.6.6-prebeta; FB-042 is Released / Closed in `v1.6.7-prebeta`; FB-043 is Released / Closed in `v1.6.8-prebeta`; and FB-044 is now the active promoted workstream on `feature/fb-044-boot-desktop-handoff-outcome-refinement` with WS-1 complete, H-1 settled-state hardening complete, LV-1 live validation complete, and `PR Readiness` next.
Current Active Workstream: FB-044 Boot-to-desktop handoff outcome refinement.
Branch Readiness Gate: Satisfied. Release publication, validation, updated-main revalidation, explicit path-sensitive workspace approval, and bounded-slice admission are complete for the historically released WS-1 `desktop/orin_desktop_test.py` -> `dev/desktop/orin_desktop_test.py`; that closed branch reflects the earlier path-sensitive posture rather than the current same-branch backlog-completion default.
- Minimal Scope: Complete the bounded docs/canon voice/audio planning seam chain: current surface inventory and ownership mapping, lifecycle/persona-state framing, and the implementation admission contract before runtime voice, shutdown voice, recovery voice, persona-default, or public voice-copy change begins.

## Backlog Priority Review

The 2026-04-23 priority reading is updated during FB-005 Branch Readiness:

- FB-004 is released and closed in `v1.6.3-prebeta`; it is no longer an active or selected-next branch candidate.
- FB-015 is released and closed in `v1.6.4-prebeta`; it no longer owns release debt or active branch truth.
- FB-029 is released and closed in `v1.6.4-prebeta`; it no longer owns release debt or active branch truth.
- FB-030 remains `Medium` as historical planning priority, but it is now Released / Closed in `v1.6.5-prebeta` and no longer owns release debt or active branch truth.
- FB-005 remains `Low` as historical workspace priority, but it is now Released / Closed in `v1.6.6-prebeta` and no longer owns release debt or selected-next truth.
- FB-042 is now Released / Closed in `v1.6.7-prebeta`; the completed runtime slice is stable historical proof.
- FB-043 is now Released / Closed in `v1.6.8-prebeta`.
- FB-044 is now selected-only / `Registry-only` on `feature/fb-044-boot-desktop-handoff-outcome-refinement`; Branch Readiness is complete and `Workstream` is next.

Current-branch clarity: latest public prerelease is `v1.6.8-prebeta`; FB-043 release debt is clear; FB-044 now owns the active promoted workstream on `feature/fb-044-boot-desktop-handoff-outcome-refinement`; WS-1 is complete and validated; the authoritative desktop-settled outcome signal is aligned across proof paths; rollback false-green on missing settled proof is fixed; the real desktop shortcut gate is green; and `PR Readiness` is the next legal phase.

## Current Merged-Unreleased Workstream

None.

## Latest Released Workstream Context

### FB-029 ORIN Legal-Safe Rebrand, Future ARIA Persona Option, And Repo Licensing Hardening

- status: `released`
- record state: `Closed`
- priority: `High`
- canonical workstream doc: `Docs/workstreams/FB-029_orin_identity_licensing_hardening.md`
- selection basis: selected during FB-015 PR Readiness as the highest-priority remaining open backlog candidate, then carried on this branch first for blocker-clearing FB-015 canon repair and now for completed Branch Readiness planning.
- branch: `feature/fb-029-orin-identity-licensing-hardening`
- phase status: Released / Closed in `v1.6.4-prebeta`; PR #76 merged into `main` at `0897fab768dc07385f83fab81434ba7926ecc4a1`; the milestone remains docs/canon-only historical truth, and explicit product/legal approval still blocks any later implementation-facing naming, licensing, release, runtime, or persona-surface change.
- repo-level post-release state: FB-030 is Released / Closed in `v1.6.5-prebeta`; FB-005 is Released / Closed in `v1.6.6-prebeta`; FB-042 is Released / Closed in `v1.6.7-prebeta`; FB-043 is Released / Closed in `v1.6.8-prebeta`; and FB-044 is now the active promoted workstream on `feature/fb-044-boot-desktop-handoff-outcome-refinement` with WS-1 complete, H-1 settled-state hardening complete, LV-1 live validation complete, and `PR Readiness` next.
- next legal seam: none; this record is now historical released truth.
Release Target: v1.6.4-prebeta
Release Floor: patch prerelease
Version Rationale: FB-029 remains a docs/canon-only identity, persona-option, and licensing-planning milestone with no new executable, runtime, operator-facing, user-facing, or materially expanded product capability.
Release Scope: Identity source-of-truth inventory, persona-option boundary framing, licensing boundary framing, implementation admission contract, hardening corrections, Live Validation waivers, PR package history, merged-unreleased package-state repair, and post-merge current-state cleanup.
Release Artifacts: Tag v1.6.4-prebeta; release title Pre-Beta v1.6.4; rich Markdown release notes summarize the FB-015 boundary model and the FB-029 identity/licensing planning frame without repeating the release title inside the notes body, and GitHub-generated `## What's Changed` plus `**Full Changelog**:` must be included.
Post-Release Truth: FB-029 is Released / Closed in `v1.6.4-prebeta`; FB-015 is also Released / Closed in the same package; FB-030 is Released / Closed in `v1.6.5-prebeta`; FB-005 is Released / Closed in `v1.6.6-prebeta`; FB-042 is Released / Closed in `v1.6.7-prebeta`; FB-043 is Released / Closed in `v1.6.8-prebeta`; and FB-044 is now the active promoted workstream on `feature/fb-044-boot-desktop-handoff-outcome-refinement` with WS-1 complete, H-1 settled-state hardening complete, LV-1 live validation complete, and `PR Readiness` next.
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
Post-Release Truth: FB-015 is Released / Closed in `v1.6.4-prebeta`; FB-029 is also Released / Closed in the same package; FB-030 is Released / Closed in `v1.6.5-prebeta`; FB-005 is Released / Closed in `v1.6.6-prebeta`; FB-042 is Released / Closed in `v1.6.7-prebeta`; FB-043 is Released / Closed in `v1.6.8-prebeta`; and FB-044 is now the active promoted workstream on `feature/fb-044-boot-desktop-handoff-outcome-refinement` with WS-1 complete, H-1 settled-state hardening complete, LV-1 live validation complete, and `PR Readiness` next.
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
- successor note: FB-015 and FB-029 are released and closed in `v1.6.4-prebeta`, FB-030 is released and closed in `v1.6.5-prebeta`, FB-005 is released and closed in `v1.6.6-prebeta`, FB-042 is released and closed in `v1.6.7-prebeta`, FB-043 is released and closed in `v1.6.8-prebeta`, and FB-044 is now the active promoted workstream on `feature/fb-044-boot-desktop-handoff-outcome-refinement` with WS-1 complete, H-1 settled-state hardening complete, LV-1 live validation complete, and `PR Readiness` next.

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
- successor note: FB-004 is released and closed in `v1.6.3-prebeta`; FB-015 and FB-029 are released and closed in `v1.6.4-prebeta`; FB-030 is released and closed in `v1.6.5-prebeta`; FB-005 is released and closed in `v1.6.6-prebeta`; FB-042 is released and closed in `v1.6.7-prebeta`; FB-043 is released and closed in `v1.6.8-prebeta`; and FB-044 is now the active promoted workstream on `feature/fb-044-boot-desktop-handoff-outcome-refinement` with WS-1 complete, H-1 settled-state hardening complete, LV-1 live validation complete, and `PR Readiness` next.

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
- successor note: FB-032 is released and closed in `v1.6.2-prebeta`; FB-004 is released and closed in `v1.6.3-prebeta`; FB-015 and FB-029 are released and closed in `v1.6.4-prebeta`; FB-030 is released and closed in `v1.6.5-prebeta`; FB-005 is released and closed in `v1.6.6-prebeta`; FB-042 is released and closed in `v1.6.7-prebeta`; FB-043 is released and closed in `v1.6.8-prebeta`; and FB-044 is now the active promoted workstream on `feature/fb-044-boot-desktop-handoff-outcome-refinement` with WS-1 complete, H-1 settled-state hardening complete, LV-1 live validation complete, and `PR Readiness` next.

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
  - FB-005 for workspace and folder organization, `Low`, promoted on `feature/fb-005-workspace-path-planning`, with historical proof that WS-1 `desktop/orin_desktop_test.py` -> `dev/desktop/orin_desktop_test.py` was the released slice on that branch under the earlier path-sensitive posture
- those candidate lanes must be selected deliberately rather than bundled together as one implicit interaction continuation
- FB-037 Branch Readiness does not imply automatic continuation into any remaining candidate lane

Use canonical workstream docs for execution detail.
Use the backlog for item identity.
