# FB-032 Nexus-Era Vision And Source-Of-Truth Migration

## Identity

- ID: `FB-032`
- Title: `Nexus-era vision and source-of-truth migration`

## Record State

- `Promoted`

## Status

- `Active`

## Release Stage

- `pre-Beta`

## Target Version

- `TBD`

## Canonical Branch

- `feature/fb-032-nexus-era-vision-source-of-truth-migration`

## Current Phase

- Phase: `Branch Readiness`

## Phase Status

- `Branch Readiness complete / Workstream admission ready`
- FB-031 is released and closed in `v1.6.1-prebeta`.
- Latest public prerelease truth is `v1.6.1-prebeta`.
- Release debt is clear.
- FB-032 is promoted from selected-only registry state into this canonical workstream record.
- No FB-032 wording migration, persona work, runtime behavior, UI implementation, rebrand execution, release work, or source-of-truth migration implementation has started.
- Workstream admission is limited to WS-1 as recorded in the Initial Workstream Seam Sequence.

## Branch Class

- `implementation`

## Blockers

None.

## Entry Basis

- `main` reached the public `v1.6.1-prebeta` release at `4ba705d2c855ad271bc73b5dae0e1ba2b88bb5ff`.
- FB-031 post-release canon closure was completed before FB-032 admission work started.
- Live GitHub release notes governance drift was repaired on this branch before FB-032 promotion.
- FB-032 was selected as the successor lane in FB-031 merge-target canon and now has the legal active Branch Readiness surface.
- The current branch is `feature/fb-032-nexus-era-vision-source-of-truth-migration`.

## Branch Objective

- Establish the Nexus-era vision and source-of-truth migration lane before any implementation begins.
- Define how current Nexus identity, historical Jarvis/ORIN references, AI/persona identity, UI/product identity, source-of-truth ownership, and migration admission rules relate to each other.
- Keep naming, wording, persona, UI, runtime, and release changes deliberate instead of allowing a broad rebrand or source migration to happen by drift.

## Target End-State

- FB-032 has a canonical migration frame that separates current product truth from preserved historical identity.
- Source-of-truth ownership is explicit enough to say which docs or artifacts may be migrated, which must preserve historical wording, and which require a later admitted seam before edits.
- AI/UI identity routing is defined so future copy, persona, UI, and runtime work do not collapse into one ambiguous rebrand.
- The implementation admission contract is clear before any wording migration, persona work, runtime behavior, UI implementation, rebrand execution, or release work can start.

## Scope

- Define current-vs-historical naming policy for Nexus-era truth.
- Define source-of-truth migration boundaries across backlog, roadmap, workstream, governance, release, and historical closeout layers.
- Define AI/persona identity routing and UI/product identity routing at planning level.
- Define admission rules for later migration or implementation seams.
- Preserve historical record integrity while allowing current truth to move forward.

## Non-Goals

- No runtime behavior changes.
- No UI implementation.
- No source code migration.
- No persona implementation.
- No wholesale rebrand execution.
- No historical record rewriting that destroys release-era traceability.
- No release packaging or tag work during Branch Readiness.

## Expected Seam Families And Risk Classes

- Source-of-truth inventory and ownership family; risk class: governance/docs, because conflicting authority layers can create durable repo drift.
- Current-vs-historical naming policy family; risk class: product identity/governance, because over-normalizing historical names can damage traceability while under-normalizing current names can keep the repo split-brained.
- AI/UI identity routing family; risk class: product/persona/UI, because assistant identity, visible product identity, and historical naming need separate admission paths.
- Migration admission contract family; risk class: validation/governance, because later wording or implementation seams must prove what they are allowed to change before they touch user-facing or runtime surfaces.
- Release and closeout continuity family; risk class: release governance, because public release notes, tags, and closeouts must remain historically faithful while current release posture advances.

## Validation Contract

- Run `python dev\orin_branch_governance_validation.py`.
- Run `git diff --check`.
- Confirm `Docs/Main.md` routes the promoted FB-032 workstream record.
- Confirm `Docs/feature_backlog.md` marks FB-032 as `Promoted` and cites this canonical workstream doc.
- Confirm `Docs/workstreams/index.md` lists FB-032 under Active and not under Closed or Merged / Release Debt Owners.
- Confirm `Docs/prebeta_roadmap.md` records FB-032 as the active Branch Readiness workstream and does not leave selected-only branch truth behind.
- Confirm no runtime, UI, persona, wording migration, source code, release, or desktop artifact changed during Branch Readiness.

## User Test Summary Strategy

- Branch Readiness is canon/planning-only and does not change user-facing behavior.
- No desktop shortcut validation or manual User Test Summary handoff is required during Branch Readiness.
- If a later Workstream seam remains docs/canon-only, Live Validation may waive the exact `## User Test Summary` artifact with a recorded reason.
- If a later seam changes user-facing copy, UI, runtime behavior, shortcut behavior, persona behavior, or another operator-facing path, FB-032 must add the exact `## User Test Summary` artifact and desktop export required by governance before Live Validation can advance.

## Later-Phase Expectations

- Workstream must execute one seam at a time and keep the active seam recorded here.
- Workstream must start with WS-1 and must not begin runtime, UI, persona, release, or broad wording migration work unless a later seam is explicitly admitted.
- Hardening must pressure-test naming ambiguity, historical preservation, source ownership conflicts, migration scope boundaries, validation coverage, and implementation-readiness risks.
- Live Validation must classify user-facing shortcut applicability and User Test Summary applicability based on the actual completed FB-032 delta.
- PR Readiness must prove merge-target canon completeness, clean branch truth, successor selection, User Test Summary state, and live PR state before PR green.
- Release Readiness remains file-frozen and may only validate release package truth if FB-032 becomes release-bearing after merge.

## Initial Workstream Seam Sequence

Seam 1: Current-vs-historical source-of-truth inventory and naming policy

- Status: Planned / first admitted Workstream seam.
- Goal: inventory the authoritative current and historical source layers, then define the naming policy that separates Nexus current truth from preserved Jarvis/ORIN-era history.
- Scope: docs/canon inventory, source-of-truth ownership map, current-vs-historical terminology policy, preservation rules, contradiction capture, and migration candidates for later seams.
- Non-Includes: no source code edits, no runtime behavior, no UI implementation, no persona implementation, no release work, no public wording migration, and no historical rewrite that destroys traceability.

Seam 2: AI/UI identity routing and migration admission contract

- Status: Planned / not admitted until WS-1 validation is green and durable.
- Goal: define separate routing for assistant/persona identity, product/UI identity, repo source-of-truth identity, and historical identity before any migration implementation.
- Scope: identity routing rules, later-seam admission checklist, user-facing applicability triggers, and validator/handoff expectations.
- Non-Includes: no persona switch, no UI copy migration, no runtime changes, no asset changes, and no release packaging.

Seam 3: migration sequencing and validation-readiness map

- Status: Planned / not admitted until prior seams are green and durable.
- Goal: turn the migration policy into a sequenced implementation/readiness map with explicit validation and stop conditions.
- Scope: migration order, affected authority layers, validator coverage expectations, User Test Summary strategy updates, and phase-exit readiness criteria.
- Non-Includes: no execution of the migration map, no runtime behavior, no UI implementation, and no release work.

## Active Seam

Active seam: BR-1 Branch Readiness admission framing is complete; WS-1 is the next admitted Workstream seam after this Branch Readiness pass is validated and durable.

- BR-1 Status: Completed in this pass.
- BR-1 Boundary: promote FB-032, define branch objective, target end-state, seam families, validation contract, User Test Summary strategy, later-phase expectations, and the first Workstream seam.
- BR-1 Non-Includes: no wording migration, persona work, runtime behavior, UI implementation, rebrand execution, source code migration, release packaging, or tag work.
- WS-1 Admission: allowed after Branch Readiness validation is green and branch truth is durable.

## Reuse Baseline

- Reuse the existing governance validator `dev/orin_branch_governance_validation.py`.
- Reuse the current workstream lifecycle and UTS rules in `Docs/phase_governance.md`, `Docs/development_rules.md`, and `Docs/workstreams/index.md`.
- Reuse FB-031's architecture-only admission pattern for docs/canon planning seams, while keeping FB-032's identity/source-of-truth scope distinct from UI/UX implementation planning.
- Do not create a new helper during Branch Readiness.

## Exit Criteria

- FB-032 is marked `Promoted` in backlog and has this canonical workstream record.
- `Docs/Main.md` routes this workstream record.
- `Docs/workstreams/index.md` lists this record under Active only.
- `Docs/prebeta_roadmap.md` records FB-032 as the current active Branch Readiness workstream.
- Branch objective, target end-state, seam families, validation contract, User Test Summary strategy, later-phase expectations, and first Workstream seam are recorded.
- No implementation work is admitted beyond the planned WS-1 docs/canon seam.
- Governance validation and diff hygiene pass.

## Rollback Target

- `Branch Readiness`

## Next Legal Phase

- `Workstream`

## Governance Drift Audit

Governance Drift Found: No.

- Release Readiness drift found before FB-032 promotion was repaired by standardizing live GitHub release notes and updating release governance/validator requirements.
- FB-031 post-release canon closure is complete.
- FB-032 Branch Readiness no longer has selected-only / registry-only drift after this promotion record.
- No contradiction remains between backlog, roadmap, workstream index, and main routing for FB-032.

## Validation Results

- `python dev\orin_branch_governance_validation.py`: PASS, 875 checks.
- `git diff --check`: PASS; line-ending normalization warnings only, with no whitespace errors.
- Targeted selected-only drift search across current authority surfaces and FB-031 handoff fields: PASS.
- Branch Readiness changed docs/canon only; no runtime, UI, persona, source code, release artifact, or desktop shortcut behavior changed.
