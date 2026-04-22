# FB-040 Monitoring, Thermals, And Performance HUD Surface

## ID And Title

- ID: `FB-040`
- Title: `Monitoring, thermals, and performance HUD surface`

## Record State

- `Promoted`

## Status

- `Active (Branch Readiness)`

## Release Stage

- `pre-Beta`

## Target Version

- `TBD`

## Canonical Branch

- `feature/fb-040-monitoring-thermals-performance-hud-surface`

## Current Phase

- Phase: `Branch Readiness`

## Phase Status

- `Active Branch`
- This branch is the legal Branch Readiness surface for carried-forward FB-039 post-release canon repair before FB-040 implementation can begin.
- FB-039 is released and closed in `v1.5.0-prebeta`.
- FB-039 release debt is clear.
- Latest public prerelease truth is `v1.5.0-prebeta`.
- This Branch Readiness pass is implementing the approved seam workflow governance contract before FB-040 Workstream begins.
- No FB-040 runtime, HUD, telemetry, thermal, monitoring, plugin, installer, or settings implementation has started.

## Branch Class

- `implementation`

## Blockers

- None after BR-1 through BR-3 repair and validation.

## Entry Basis

- `main` was aligned with `origin/main` before `feature/fb-040-monitoring-thermals-performance-hud-surface` was admitted.
- FB-039 release execution completed as `v1.5.0-prebeta`.
- Release debt is clear after carried-forward canon repair in Branch Readiness.
- The active branch exists because FB-039 release/post-release drift was discovered after merge and must be repaired on the next active Branch Readiness surface before implementation.
- FB-040 was the selected successor in FB-039 merge-target canon.

## Branch Objective

- Define the branch authority and first execution boundaries for monitoring, thermals, and performance HUD surfaces.
- Keep FB-040 focused on local monitoring/HUD product boundaries rather than external trigger integration, saved-action execution, installer behavior, release packaging, or generic telemetry sprawl.
- Complete carried-forward FB-039 post-release canon repair before any FB-040 implementation seam is admitted.

## Target End-State

- FB-040 has a coherent Branch Readiness scaffold that can admit Workstream only after current repo truth is clean.
- Monitoring, thermal, and performance HUD source categories are separated from later telemetry plumbing or UI implementation.
- First Workstream seams can begin with architecture/source-map work rather than runtime collection, HUD rendering, persistence, plugin integration, or installer changes.
- FB-039 remains closed/released and release debt remains clear.

## Expected Seam Families And Risk Classes

- Source-map and ownership seam family; risk class: architecture/governance because monitoring data origins, ownership, and display authority must be defined before implementation.
- Privacy/safety and performance-boundary seam family; risk class: product/safety because monitoring can expose local system state and must not create noisy, privileged, or always-on behavior by accident.
- HUD surface framing seam family; risk class: desktop/UI because future overlays or status surfaces can affect visibility, focus, readability, and operator trust.
- Validation/admission seam family; risk class: validator/governance because later implementation must prove cleanup, non-invasive behavior, and no unrelated runtime expansion.

## User Test Summary Strategy

- Branch Readiness has no manual `UTS` artifact because no user-facing FB-040 behavior exists yet.
- If later Workstream seams add a user-visible HUD, tray, overlay, shortcut, settings, or monitoring display path, the workstream must add an exact `## User Test Summary` artifact before Live Validation.
- If FB-040 remains architecture-only or internal-only in a later phase, any UTS waiver must include explicit waiver reasons in the canonical `## User Test Summary` section.

## Later-Phase Expectations

- Workstream must begin with source-map and ownership vocabulary before any runtime collection or HUD UI work.
- Hardening must pressure-test cleanup, no-persistence-by-default behavior, performance overhead, and boundary regressions if implementation is admitted.
- Live Validation must classify whether the milestone is user-facing and must include shortcut/HUD/manual validation only if an operator-visible surface exists.
- PR Readiness must prove merge-target canon, release target semantics, next-workstream selection, helper retention, and branch-creation gate truth before PR creation and validation.
- Release Readiness remains analysis-only and file-frozen.

## Initial Workstream Seam Sequence

Seam 1: monitoring and thermal source map plus ownership vocabulary

- Goal: define candidate monitoring data origins, ownership terms, and product boundaries for CPU/GPU thermals, performance status, and HUD-facing signals.
- Scope: architecture-only source categories, Nexus-owned versus external/system-owned responsibility, naming vocabulary, and explicit unknowns for later admission.
- Non-Includes: no telemetry collection, sensor polling, hardware API binding, HUD rendering, persistence, settings UI, tray/taskbar work, plugin integration, installer changes, or release packaging.

Seam 2: HUD surface and visibility boundary framing

- Goal: define when a monitoring or performance signal may become user-visible and what surface classes are candidates.
- Scope: desktop/HUD/tray/overlay framing, visibility ownership, and non-invasive display constraints.
- Non-Includes: no UI implementation, no layout, no live overlays, no notification system, no hotkeys, no timers, and no runtime rendering.

Seam 3: validation and admission contract for later implementation seams

- Goal: define the proof required before any monitoring, thermal, or HUD runtime seam can begin.
- Scope: cleanup expectations, non-invasive behavior, performance overhead proof, no-persistence-by-default checks, and UTS classification rules.
- Non-Includes: no validation helper creation unless a later implementation seam makes it necessary, no hardware-dependent test matrix, and no release execution.

## Active Seam

Active seam: GOV-1 through GOV-3 Branch Readiness seam workflow governance implementation.

- BR-1: repair carried-forward post-release canon drift from FB-039.
- BR-2: repair carried-forward version-governance drift and validator expectations.
- BR-3: re-evaluate repo truth and admit FB-040 only if Branch Readiness becomes clean.
- GOV-1: implement the refined seam workflow contract in the canonical governance owner.
- GOV-2: align development rules and Codex mode posture to the canonical seam contract without creating duplicate authority.
- GOV-3: validate governance alignment and confirm FB-040 remains ready for Workstream admission.

## Validation Contract

- `python dev\orin_branch_governance_validation.py`
- `git diff --check`
- `git status --short --branch`
- The validator must fail if latest public prerelease canon trails the latest local pre-Beta tag.
- The validator must fail if a workstream whose release tag exists remains represented as merged-unreleased release debt instead of closed/released.
- Branch Readiness is not clean unless FB-039 is closed/released, release debt is clear, FB-040 is active/promoted, and this authority record contains the required Branch Readiness scaffold.

## Stop Conditions

- Stop if FB-039 release debt, stale latest public prerelease truth, or merged-unreleased state remains.
- Stop if FB-040 implementation work begins before Branch Readiness is clean.
- Stop if monitoring/HUD scope drifts into external trigger integration, saved-action execution, installer behavior, release packaging, or unrelated governance expansion.
- Stop if validator enforcement would require broad redesign outside post-release truth and Branch Readiness durability.

## Exit Criteria

- FB-039 is represented as `Released (v1.5.0-prebeta)` / `Closed` in backlog, roadmap, workstreams index, and its workstream record.
- Latest public prerelease truth is `v1.5.0-prebeta`.
- Release debt is clear.
- FB-040 is represented as the active promoted workstream in backlog, roadmap, workstreams index, Main routing, and this workstream record.
- Branch objective, target end-state, expected seam families/risk classes, validation contract, UTS strategy, later-phase expectations, and first Workstream seam sequence are explicit.
- No FB-040 runtime/product implementation has started.

## Rollback Target

- `Branch Readiness`

## Next Legal Phase

- `Workstream`

## Governance Drift Audit

Governance Drift Found: Yes, repaired during FB-040 Branch Readiness.

- Drift Type: carried-forward post-release canon drift and version-governance validator gap.
- Finding: FB-039 had been released as `v1.5.0-prebeta`, but durable canon still recorded latest public prerelease `v1.4.1-prebeta`, kept FB-039 as merged-unreleased release debt, and treated FB-040 as selected-only / not-created after the FB-040 branch existed.
- Repair: latest public prerelease truth is advanced to `v1.5.0-prebeta`, FB-039 is closed/released, release debt is cleared, FB-040 is admitted as the active Branch Readiness workstream, and validator coverage is extended so the latest released tag cannot leave its owner in merged-unreleased state.
- Governance Drift Found After Repair: No unresolved drift remains after validation.
