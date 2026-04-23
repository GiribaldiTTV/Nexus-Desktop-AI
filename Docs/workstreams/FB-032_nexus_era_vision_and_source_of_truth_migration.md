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

- Phase: `Workstream`

## Phase Status

- `WS-1 complete / WS-2 admission ready`
- FB-031 is released and closed in `v1.6.1-prebeta`.
- Latest public prerelease truth is `v1.6.1-prebeta`.
- Release debt is clear.
- FB-032 Branch Readiness is complete and this record is the active Workstream authority.
- WS-1 current-vs-historical source-of-truth inventory and naming policy is complete.
- No FB-032 wording migration, persona work, runtime behavior, UI implementation, rebrand execution, release work, or source-of-truth migration implementation has started.
- Workstream continuation is limited to WS-2 classification and mapping of canonical vs historical surfaces.

## Branch Class

- `implementation`

## Blockers

None.

## Entry Basis

- `main` reached the public `v1.6.1-prebeta` release at `4ba705d2c855ad271bc73b5dae0e1ba2b88bb5ff`.
- FB-031 post-release canon closure was completed before FB-032 admission work started.
- Live GitHub release notes governance drift was repaired on this branch before FB-032 promotion.
- FB-032 was selected as the successor lane in FB-031 merge-target canon and completed Branch Readiness on this legal active branch surface.
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
- Confirm `Docs/prebeta_roadmap.md` records FB-032 as the active Workstream-phase workstream and does not leave Branch Readiness-only truth behind.
- Confirm no runtime, UI, persona, wording migration, source code, release, or desktop artifact changed during WS-1.

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

- Status: Completed.
- Goal: inventory the authoritative current and historical source layers, then define the naming policy that separates Nexus current truth from preserved Jarvis/ORIN-era history.
- Scope: docs/canon inventory, source-of-truth ownership map, current-vs-historical terminology policy, preservation rules, contradiction capture, and migration candidates for later seams.
- Non-Includes: no source code edits, no runtime behavior, no UI implementation, no persona implementation, no release work, no public wording migration, and no historical rewrite that destroys traceability.

Seam 2: AI/UI identity routing and migration admission contract

- Status: Planned / next admitted Workstream seam after WS-1 validation is green and durable.
- Goal: define separate routing for assistant/persona identity, product/UI identity, repo source-of-truth identity, and historical identity before any migration implementation.
- Scope: identity routing rules, later-seam admission checklist, user-facing applicability triggers, and validator/handoff expectations.
- Non-Includes: no persona switch, no UI copy migration, no runtime changes, no asset changes, and no release packaging.

Seam 3: migration sequencing and validation-readiness map

- Status: Planned / not admitted until prior seams are green and durable.
- Goal: turn the migration policy into a sequenced implementation/readiness map with explicit validation and stop conditions.
- Scope: migration order, affected authority layers, validator coverage expectations, User Test Summary strategy updates, and phase-exit readiness criteria.
- Non-Includes: no execution of the migration map, no runtime behavior, no UI implementation, and no release work.

## Active Seam

Active seam: WS-1 current-vs-historical source-of-truth inventory and naming policy is complete; WS-2 classification and mapping of canonical vs historical surfaces is the next admitted Workstream seam after this WS-1 pass is validated and durable.

- BR-1 Status: Completed in this pass.
- BR-1 Boundary: promote FB-032, define branch objective, target end-state, seam families, validation contract, User Test Summary strategy, later-phase expectations, and the first Workstream seam.
- BR-1 Non-Includes: no wording migration, persona work, runtime behavior, UI implementation, rebrand execution, source code migration, release packaging, or tag work.
- WS-1 Status: Completed / executed.
- WS-1 Boundary: docs/canon inventory and naming policy only.
- WS-1 Non-Includes: no source code edits, no runtime behavior, no UI implementation, no persona implementation, no public wording migration, no release work, and no historical rewrite that destroys traceability.
- WS-2 Admission: allowed after WS-1 validation is green and branch truth is durable.

## WS-1 Execution Record

WS-1 is docs/canon only. It defines the source-of-truth inventory and naming policy that later FB-032 seams must use before any controlled migration execution is considered.

### Current Source-Of-Truth Inventory

Current source-of-truth layers:

- Routing and layer ownership: `Docs/Main.md` owns the source-of-truth routing map, protected-main rule, current layer split, and current active workstream routing.
- Execution governance: `Docs/development_rules.md`, `Docs/phase_governance.md`, `Docs/codex_modes.md`, and `Docs/orin_task_template.md` own execution posture, phase names, blocker rules, seam behavior, durability, proof authority, and prompt contract.
- Product and identity intent: `Docs/orin_vision.md` owns current product intent for `Nexus Desktop AI` and the `ORIN` assistant layer; it records that older Jarvis releases are preserved history and do not define the active public Nexus release line.
- Architecture and orchestration truth: `Docs/architecture.md` and `Docs/orchestration.md` own the current runtime path, launcher/renderer ownership, runtime evidence boundaries, and explicit current legacy-named artifacts such as `launch_orin_desktop.vbs`, `desktop/orin_desktop_launcher.pyw`, `desktop/orin_desktop_main.py`, `%LOCALAPPDATA%/Nexus Desktop AI/state/jarvis_history_v1.jsonl`, `C:/Jarvis/logs`, `C:/Jarvis/logs/crash`, and `C:/Jarvis/dev/logs/<lane>/...`.
- Persona display guidance: `Docs/orin_display_naming_guidance.md` owns display-form guidance for `ORIN`, `O.R.I.N.`, and `Operational Response and Intelligence Nexus`; it does not own rollout sequencing or broad source rewrites.
- Registry and sequencing: `Docs/feature_backlog.md` owns tracked identity and record state; `Docs/prebeta_roadmap.md` owns sequencing, release posture, current active lane, and current release debt posture.
- Promoted workstream truth: `Docs/workstreams/index.md` routes active, merged-unreleased, and closed workstream records; this FB-032 record owns branch-local execution, evidence, active seam history, and reuse notes for the current lane.
- User Test Summary and validation support: `Docs/user_test_summary_guidance.md` and `Docs/validation_helper_registry.md` own manual validation handoff structure and reusable helper governance when those layers become relevant.
- Closeout and epoch truth: `Docs/closeout_guidance.md`, `Docs/closeout_index.md`, and routed closeout/rebaseline docs own historical lookup and epoch summaries without replacing current workstream, release, or roadmap truth.
- Live implementation truth: source files, structured runtime logs, release tags, and GitHub releases remain authoritative for the behavior, artifacts, and public release state they directly record.

### Historical Source-Of-Truth Inventory

Historical source-of-truth layers:

- Closed workstream docs under `Docs/workstreams/` preserve released lane truth and are not active execution authority by inertia.
- Historical closeout docs under `Docs/closeouts/` preserve older Jarvis-era and epoch-level history; they must be routed through `Docs/closeout_index.md`.
- Public release tags, GitHub release notes, PRs, branch names, commit history, and release-era issue context remain historical evidence and must not be modernized by wording preference.
- Older Jarvis-named release records, docs, and closeouts remain preserved historical records unless a current source explicitly identifies a still-real runtime artifact that keeps the name.
- Current runtime artifacts with historical names, including `jarvis_history_v1.jsonl` and `C:/Jarvis/...` evidence roots, are not historical-only references; they are current runtime truth until an admitted implementation seam changes the underlying path or file contract.
- Future-facing planning docs may contain deferred Nexus/ORIN or ARIA concepts; those sections are planning truth only and must not be recast as current shipped behavior.

### Naming Policy For Canonical Vs Historical Surfaces

Use this policy before any later FB-032 classification, mapping, or migration seam edits wording:

- Current product, repository, release, and platform-shell identity should use `Nexus Desktop AI` on first clear mention, with `Nexus` acceptable where the product context is unambiguous.
- Assistant persona identity should use `ORIN` by default; use `O.R.I.N.` or `Operational Response and Intelligence Nexus` only where `Docs/orin_display_naming_guidance.md` admits that presentation form.
- Current source-of-truth docs may mention `Jarvis` only for preserved historical context, exact legacy artifact names, exact runtime/log/state paths, exact branch/tag/commit/PR history, or quoted source material.
- Historical closeouts, closed workstream history, release notes, tags, branch names, commit messages, and old public context should preserve their release-era names. Do not rewrite them merely to make wording look modern.
- Current runtime paths or files that still contain `Jarvis` or `orin` names must be cited exactly. If explanatory copy is needed, say that the artifact name is legacy or current-runtime-with-legacy-name rather than silently renaming it.
- Do not run broad search/replace across `Jarvis`, `ORIN`, `Nexus`, or related identity terms. Every future edit must be admitted by classification, source owner, surface type, and validation impact.
- Backlog entries keep tracked identity and minimal scope; roadmap keeps sequencing and release posture; workstream docs keep execution/evidence detail. Do not duplicate full execution story just to normalize wording.
- Future or deferred concepts must be labeled as future, planning, deferred, or post-Beta when they are not current runtime truth.
- User-facing copy, persona behavior, UI naming, runtime paths, helper names, release notes, and historical records require separate migration admission decisions. A policy-valid term in one surface does not authorize changing another surface.
- When canonical and historical wording conflict, prefer the owner layer from `Docs/Main.md`, then preserve the conflicting historical wording as historical evidence until WS-2 maps the surface and WS-3 admits or blocks migration execution.

### WS-1 Completion Decision

- WS-1 Result: Complete / green.
- User-facing impact: none. This seam changed docs/canon only.
- Next admitted seam: WS-2 classification and mapping of canonical vs historical surfaces.
- Stop condition: none identified; bounded multi-seam continuation remains valid after validation.

## Reuse Baseline

- Reuse the existing governance validator `dev/orin_branch_governance_validation.py`.
- Reuse the current workstream lifecycle and UTS rules in `Docs/phase_governance.md`, `Docs/development_rules.md`, and `Docs/workstreams/index.md`.
- Reuse FB-031's architecture-only admission pattern for docs/canon planning seams, while keeping FB-032's identity/source-of-truth scope distinct from UI/UX implementation planning.
- Do not create a new helper during WS-1.

## Exit Criteria

- WS-1 current-vs-historical source-of-truth inventory is recorded.
- WS-1 naming policy for canonical vs historical surfaces is recorded.
- `Docs/feature_backlog.md`, `Docs/prebeta_roadmap.md`, and `Docs/workstreams/index.md` identify FB-032 as the active Workstream-phase authority.
- No implementation work is admitted beyond the planned docs/canon seam sequence.
- Workstream phase does not exit to Hardening until WS-1 through WS-3 are complete and green.
- Governance validation and diff hygiene pass for the current seam.

## Rollback Target

- `Workstream`

## Next Legal Phase

- `Workstream`

## Governance Drift Audit

Governance Drift Found: No.

- Release Readiness drift found before FB-032 promotion was repaired by standardizing live GitHub release notes and updating release governance/validator requirements.
- FB-031 post-release canon closure is complete.
- FB-032 Branch Readiness no longer has selected-only / registry-only drift after this promotion record.
- No contradiction remains between backlog, roadmap, workstream index, and main routing for FB-032.
- WS-1 found no reason to reinterpret historical Jarvis records as current Nexus truth and no reason to rename current legacy-named runtime paths without a later admitted implementation seam.

## Validation Results

- Branch Readiness validation: `python dev\orin_branch_governance_validation.py` PASS, 875 checks; `git diff --check` PASS with line-ending normalization warnings only; targeted selected-only drift search PASS.
- WS-1 validation: `python dev\orin_branch_governance_validation.py` PASS, 863 checks.
- WS-1 diff hygiene: `git diff --check` PASS with line-ending normalization warnings only and no whitespace errors.
- WS-1 targeted drift scan across current authority surfaces: PASS; no active FB-032 Branch Readiness-only or selected-only claim remains in current-state surfaces.
- WS-1 changed docs/canon only; no runtime, UI, persona behavior, source code, release artifact, desktop shortcut behavior, broad wording migration, or historical rewrite changed.
