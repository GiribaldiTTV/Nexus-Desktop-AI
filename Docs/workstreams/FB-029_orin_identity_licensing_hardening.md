# FB-029 ORIN Legal-Safe Rebrand, Future ARIA Persona Option, And Repo Licensing Hardening

## Identity

- ID: `FB-029`
- Title: `ORIN legal-safe rebrand, future ARIA persona option, and repo licensing hardening`

## Record State

- `Promoted`

## Status

- `Active`

## Release Stage

- `pre-Beta`

## Canonical Branch

- `feature/fb-029-orin-identity-licensing-hardening`

## Current Phase

- Phase: `Branch Readiness`

## Phase Status

- `Branch Readiness complete; Workstream next`
- FB-015 remains the merged-unreleased release-debt owner on `main` for `v1.6.4-prebeta`.
- Repo-level current active workstream remains `none` while FB-015 release debt is unresolved.
- FB-029 is the current promoted Branch Readiness authority on `feature/fb-029-orin-identity-licensing-hardening`.
- This milestone is admitted as docs/canon-only planning and governance work.
- WS-1 current identity, persona-option, and licensing source-of-truth inventory is admitted next.
- Explicit product/legal approval still blocks any implementation-facing naming, licensing, release, runtime, or persona-surface change.
- No naming changes, license-file changes, runtime changes, release edits, UI copy sweeps, asset changes, or repo ownership changes have started.

## Branch Class

- `implementation`

## Blockers

None.

## Entry Basis

- PR #75 merged and FB-015 now owns merged-unreleased release debt on `main` for `v1.6.4-prebeta`.
- Escaped FB-015 post-merge canon drift was repaired on this branch at `e4bb6405358ce74124f3dba6655720025a2c3fe1`.
- FB-029 remained the selected-next workstream after the repair because it is still the highest-priority open backlog candidate.
- The current branch is now the legal FB-029 planning surface.
- FB-029 implementation is not yet admitted; Branch Readiness is the first legal phase for this workstream.

## Branch Objective

- Define the planning frame for legal-safe ORIN naming, optional future ARIA persona posture, and repo licensing hardening without performing the rebrand, persona rollout, or licensing implementation.
- Separate canonical current identity, preserved historical identity, optional future persona direction, and licensing-hardening scope so later implementation does not guess across legal, product, runtime, release, and documentation boundaries.
- Establish implementation-admission rules so any later naming, licensing, runtime, UI, release, or persona-facing edit must prove the exact affected surfaces, approval posture, rollback path, and validation contract before work begins.

## Target End-State

- FB-029 has a canonical planning record for current-vs-historical identity truth, future persona-option framing, licensing-hardening boundaries, and implementation non-goals.
- Workstream execution can begin with a source-of-truth inventory before any wording, licensing, runtime, release, or UI implementation is considered.
- The branch has a validation contract that distinguishes docs/canon proof from later user-facing, release-facing, licensing, runtime, or operator-facing proof.
- Later implementation remains blocked unless a future legal surface explicitly admits the affected surfaces and product/legal approval posture.

## Scope

- Inventory current ORIN, Nexus, and preserved historical naming surfaces.
- Inventory current licensing, ownership, release, and identity-claim surfaces that future hardening must classify.
- Define future ARIA persona posture as an optional later lane rather than an implicit default or incidental wording sweep.
- Define validation, rollback, and admission rules for later legal-safe naming or licensing implementation.

## Non-Goals

- No live rebrand execution.
- No repository-wide wording sweep.
- No runtime behavior changes.
- No launcher, installer, shortcut, or renderer changes.
- No UI copy changes.
- No asset, icon, splash, or brand-surface edits.
- No license-file edits, copyright reassignment, or repo ownership transfer.
- No public release-note edits, tag edits, or release publication.
- No legal conclusion presented as implemented truth.
- No ARIA rollout as a default persona.

## Expected Seam Families And Risk Classes

- Current identity and naming source-of-truth inventory family; risk class: branding/source-of-truth, because current versus historical naming drift can spread quickly if not classified first.
- Licensing and ownership surface classification family; risk class: legal/repo-governance, because licensing, copyright, and repo-ownership surfaces require explicit boundary control before any hardening edits.
- Future persona-option framing family; risk class: product/persona, because optional ARIA posture must not quietly become an active runtime or UI commitment.
- Implementation admission and rollback contract family; risk class: governance/implementation, because later naming or licensing edits must prove exact approval, affected surfaces, rollback, and validation.
- Release and user-facing surface trigger family; risk class: release/user-facing, because later naming or licensing changes can affect public release notes, user-visible copy, and operator-facing documentation.

## Validation Contract

- Run `python dev\orin_branch_governance_validation.py`.
- Run `git diff --check`.
- Confirm `Docs/Main.md` routes this workstream record.
- Confirm `Docs/feature_backlog.md` marks FB-029 as `Promoted`, `Active`, and cites this doc.
- Confirm `Docs/workstreams/index.md` lists FB-029 under Active while FB-015 remains under Merged / Release Debt Owners.
- Confirm `Docs/prebeta_roadmap.md` preserves FB-015 merged-unreleased release-debt truth with `current active workstream: none` while also recording FB-029 Branch Readiness completion and WS-1 as the admitted next seam.
- Confirm `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, `Docs/workstreams/index.md`, and `Docs/workstreams/FB-015_boot_and_desktop_phase_boundary_model.md` agree that FB-029 is promoted on this branch, Branch Readiness is complete, and WS-1 is next.
- Confirm FB-015 merged-unreleased release-debt truth still routes Release Readiness to updated `main`.
- Confirm explicit product/legal approval remains required before any implementation-facing naming, licensing, release, runtime, or persona-surface change.
- Confirm no naming changes, license-file edits, runtime changes, release edits, UI copy edits, asset edits, or other user-facing or operator-facing implementation occurred in this pass.

## Branch Readiness Validation Results

- `python dev\orin_branch_governance_validation.py`: PASS, 1057 checks.
- `git diff --check`: PASS with line-ending normalization warnings only and no whitespace errors.
- Scope validation: PASS; this pass changes docs/canon routing, workstream authority, and validation coverage only.
- Admission validation: PASS; FB-029 is promoted, Branch Readiness is complete, and WS-1 is the admitted next seam.

## User Test Summary Strategy

- Branch Readiness and the admitted WS-1 through WS-3 seam chain remain docs/canon only and do not change user-facing behavior.
- No desktop shortcut validation, desktop export, or manual User Test Summary handoff is required during Branch Readiness or the planned docs/canon-only Workstream seams.
- If a later legal surface admits implementation-facing naming, licensing, release, runtime, UI, installer, shortcut, or other operator-facing work, that future work must add the exact `## User Test Summary` artifact and any required desktop export before Live Validation can advance.

## Later-Phase Expectations

- Workstream must execute bounded docs/canon seams and keep the active seam recorded here.
- Workstream must start with WS-1 and must not perform live rebrand execution, license-file edits, runtime behavior changes, UI wording changes, asset changes, installer changes, release edits, or public release updates.
- Hardening must pressure-test current-vs-historical identity framing, legal and licensing boundary classification, optional persona posture, implementation-admission rules, rollback boundaries, and approval gating.
- Live Validation must classify user-facing shortcut applicability and User Test Summary applicability for the completed docs/canon-only milestone.
- PR Readiness must prove merge-target canon completeness, clean branch truth, successor selection, release-floor reasoning, and live PR state before PR green.
- If this milestone remains docs/canon-only through PR Readiness, any later release target defaults to `patch prerelease` unless a future legal surface explicitly admits a release-bearing capability.
- Any implementation-facing naming, licensing, release, runtime, or persona-surface work requires a later explicit product/legal approval and legal branch-surface admission; it must not enter by inertia on this branch.

## Initial Workstream Seam Sequence

Seam 1: Current identity, persona-option, and licensing source-of-truth inventory

- Status: Admitted next.
- Goal: inventory the current identity, historical identity, optional future persona, licensing, ownership, and release-facing surfaces before any implementation is considered.
- Scope: docs/canon source inventory, current-vs-historical classification, licensing and ownership surface map, evidence roots, ambiguity capture, and non-goal boundaries.
- Non-Includes: no wording edits, no license-file edits, no runtime changes, no UI or asset edits, no release edits, and no public release editing.

Seam 2: Canonical vs historical identity, persona-option, and licensing boundary framing

- Status: Planned.
- Goal: define the boundary vocabulary and ownership model that distinguishes current truth, preserved history, optional future persona posture, licensing hardening targets, and out-of-scope execution surfaces.
- Scope: docs/canon boundary framing, risk notes, approval notes, ambiguity capture, and implementation-readiness constraints.
- Non-Includes: no wording edits, no license-file edits, no runtime changes, no UI or asset edits, no release edits, and no public release editing.

Seam 3: Validation and admission contract for future identity and licensing implementation

- Status: Planned.
- Goal: define the proof and admission contract required before future naming, licensing, release, runtime, UI, or persona-facing implementation can begin.
- Scope: validation gates, approval posture, rollback proof, helper reuse posture, release and user-facing trigger classification, and implementation-admission checklist.
- Non-Includes: no wording edits, no license-file edits, no runtime changes, no UI or asset edits, no release edits, and no public release editing.

## Active Seam

Active seam: WS-1 current identity, persona-option, and licensing source-of-truth inventory.

- BR-1 Status: Completed in this pass.
- BR-1 Boundary: promote FB-029, define branch objective, target end-state, seam families, validation contract, User Test Summary strategy, later-phase expectations, and the first Workstream seam.
- BR-1 Non-Includes: no naming edits, no licensing edits, no runtime changes, no UI or asset changes, no installer changes, no release edits, and no public release editing.
- WS-1 Status: Admitted next.
- WS-1 Boundary: docs/canon source-of-truth inventory only.
- WS-1 Non-Includes: no naming edits, no licensing edits, no runtime changes, no UI or asset changes, no installer changes, no release edits, and no public release editing.

## Reuse Baseline

- `Docs/feature_backlog.md`
- `Docs/prebeta_roadmap.md`
- `Docs/workstreams/index.md`
- `Docs/workstreams/FB-015_boot_and_desktop_phase_boundary_model.md`
- `Docs/workstreams/FB-032_nexus_era_vision_and_source_of_truth_migration.md`
- `Docs/orin_vision.md`
- `Docs/orin_display_naming_guidance.md`
- `Docs/ownership_ip_plan.md`
- `Docs/phase_governance.md`
- `Docs/validation_helper_registry.md`
- `dev/orin_branch_governance_validation.py`

## Exit Criteria

- The branch objective, target end-state, seam families, validation contract, User Test Summary strategy, later-phase expectations, and first Workstream seam are recorded.
- `Docs/Main.md`, `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, and `Docs/workstreams/index.md` route FB-029 as promoted current-branch truth on `feature/fb-029-orin-identity-licensing-hardening`.
- FB-015 remains the merged-unreleased release-debt owner on `main` for `v1.6.4-prebeta`.
- WS-1 current identity, persona-option, and licensing source-of-truth inventory is admitted next.
- Explicit product/legal approval remains recorded as the gate on any implementation-facing naming, licensing, release, runtime, or persona-surface work.
- No naming edits, license-file edits, runtime changes, UI or asset changes, installer changes, release edits, or public release edits were made in this pass.
- Validation is green.

## Rollback Target

- `Branch Readiness`
- Revert the FB-029 Branch Readiness docs/canon commit(s) and return FB-029 to selected-only / `Registry-only` branch truth on `feature/fb-029-orin-identity-licensing-hardening` with no admitted Workstream seam.

## Next Legal Phase

- `Workstream`
