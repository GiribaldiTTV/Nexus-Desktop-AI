# FB-038 Taskbar / Tray Quick-Task UX And Create Custom Task Surface

## ID And Title

- ID: `FB-038`
- Title: `Taskbar / tray quick-task UX and Create Custom Task surface`

## Record State

- `Promoted`

## Status

- `Workstream`

## Release Stage

- `pre-Beta`

## Target Version

- `TBD`

## Canonical Branch

- `feature/fb-038-taskbar-tray-quick-task-ux`

## Purpose / Why It Matters

Define and deliver the smallest safe shell-facing quick-task entry surface above the released interaction, authoring, callable-group execution, and built-in catalog baselines.

This workstream exists so taskbar or tray access and Create Custom Task entry are planned as deliberate UX surfaces instead of being added by inertia to the overlay, authoring, launcher, or settings systems.

## Current Phase

- Phase: `Workstream`

## Phase Status

- `Active Branch`
- current branch: `feature/fb-038-taskbar-tray-quick-task-ux`
- Branch Readiness is complete and durably checkpointed in commit `766ff67`
- no FB-038 product or runtime implementation has started
- first Workstream pass is source-map and seam selection only
- FB-037 is released and closed in `v1.4.0-prebeta`
- FB-037 release publication exists at `https://github.com/GiribaldiTTV/Nexus-Desktop-AI/releases/tag/v1.4.0-prebeta`
- no FB-037 release-debt blocker remains
- no active release-packaging branch remains

## Branch Class

- `implementation`

## Blockers

- None

## Entry Basis

- local `main` and `origin/main` are aligned at the FB-037 release-packaging merge baseline
- current branch is `feature/fb-038-taskbar-tray-quick-task-ux`
- current branch is based on updated `main`
- Branch Readiness governance/canon repair plus FB-038 admission setup is durable in commit `766ff67`
- FB-037 is `Released (v1.4.0-prebeta)` and `Closed`
- the `v1.4.0-prebeta` Git tag exists locally and remotely
- the GitHub prerelease for `v1.4.0-prebeta` exists, is published, and is marked prerelease
- FB-038 was selected in canon before this admission and is now promoted
- Branch Readiness exit criteria are satisfied
- no FB-038 implementation work is authorized until the first Workstream pass selects and bounds a seam

## Exit Criteria

- source-map and seam-selection pass is complete
- the first implementation seam is explicitly selected, bounded, and validated before implementation begins
- no implementation starts without exact non-includes and validation targets
- approved Workstream scope remains within FB-038 and does not reopen released FB-027, FB-036, FB-041, or FB-037 behavior by inertia
- direct verification is complete for each selected Workstream seam
- User Test Summary obligations are updated when a user-visible seam lands
- no unresolved same-slice correctness gap remains

## Rollback Target

- `Branch Readiness`

## Next Legal Phase

- `Hardening`

## Bounded Objective

Plan and then implement the smallest safe user-facing entry surface for quick task access from taskbar or tray context, including a Create Custom Task affordance only when it can reuse the released shared action and authoring foundations safely.

The branch should prove a bounded shell-facing UX milestone, not redesign the action system.

## Target End-State

- a clearly bounded taskbar or tray quick-task entry surface is implemented or the branch records why the smallest safe surface must be deferred
- Create Custom Task entry reuses the released FB-036 authoring model rather than inventing a second authoring path
- released shared-action resolution, saved-action authority, built-in catalog behavior, and callable-group execution remain unchanged
- branch-local validation and Live Validation evidence are sufficient to support PR Readiness

## Expected Seam Families And Risk Classes

- source map / seam-selection audit:
  - risk class: analysis and boundary-setting
  - goal: identify the existing taskbar, tray, launcher, overlay, and Create Custom Task entry surfaces before selecting code changes
- shell-facing entry surface:
  - risk class: UI-model and launcher-adjacent desktop UX
  - goal: expose one smallest safe taskbar or tray entry into existing Nexus behavior
- Create Custom Task affordance:
  - risk class: authoring-entry UX over released FB-036 foundations
  - goal: route to the existing authoring surface without changing saved-action schema, collision rules, or resolution behavior
- validation support:
  - risk class: helper or harness support only if the existing validation surface cannot prove the selected UX seam

Because taskbar, tray, launcher-adjacent, and UI-model behavior are higher-risk than catalog-only actions, FB-038 begins with single-seam fallback by default.
Bounded multi-seam workflow may be used later only if a Workstream analysis proves the seams share the same risk class, subsystem family, and validation gate.

## First Workstream Pass

The first Workstream pass should be a source-map and seam-selection pass only.

It must:

- identify the current tray, taskbar, overlay, launcher, and Create Custom Task surfaces
- recommend the smallest safe first implementation seam
- define exact non-includes before any product/runtime patch
- select validation targets for the first seam
- preserve all released FB-027, FB-036, FB-041, and FB-037 behavior

## Explicit Non-Goals

- no product/runtime implementation during Branch Readiness
- no implementation before the first Workstream pass selects and bounds a seam
- no broad UI redesign
- no Action Studio behavior
- no saved-action schema change
- no shared-action resolution change
- no built-in catalog expansion
- no callable-group execution change
- no new target kinds
- no settings or protocol behavior
- no installer, startup, or Windows pinning policy changes unless a later approved seam proves that is the smallest safe need
- no external trigger, plugin integration, monitoring, thermals, or performance HUD work
- no FB-039 or FB-040 scope

## Reuse Baseline

- `Docs/closeouts/nexus_prebeta_rebaseline_through_v1.4.0-prebeta.md`
- `Docs/workstreams/FB-037_built_in_actions_and_settings_expansion.md`
- `Docs/workstreams/FB-041_deterministic_callable_group_execution_layer.md`
- `Docs/workstreams/FB-036_saved_action_authoring.md`
- `Docs/workstreams/FB-027_interaction_system_baseline.md`
- `desktop/shared_action_model.py`
- `desktop/interaction_overlay_model.py`

## Validation Contract

Branch Readiness validation proved:

- FB-038 is promoted exactly once
- this canonical workstream doc exists and owns active phase authority
- backlog, roadmap, workstream index, and this workstream doc agreed on `Branch Readiness`
- FB-037 remains released and closed in `v1.4.0-prebeta`
- no product/runtime code changed during Branch Readiness
- `python dev/orin_branch_governance_validation.py` passes
- `git diff --check` passes

Workstream validation must preserve:

- released FB-027 typed-first interaction baseline
- released FB-036 saved-action authoring, collision, and source-safety behavior
- released FB-041 deterministic callable-group execution behavior
- released FB-037 built-in catalog behavior and saved-action override authority
- existing confirm/result boundaries unless a later approved UI seam explicitly scopes visible changes

Future desktop UX validation must include:

- repo-side validators for affected behavior
- real interactive OS-level proof when feasible
- cleanup verification for any windows, tray state, helper processes, or temporary artifacts opened by validation
- User Test Summary updates when the branch changes user-visible behavior

## User Test Summary Strategy

No meaningful manual User Test Summary exists yet because Branch Readiness does not change product behavior.

When a Workstream seam changes taskbar, tray, Create Custom Task, or other user-visible desktop behavior, update this workstream's `## User Test Summary` incrementally and refresh `C:\Users\anden\OneDrive\Desktop\User Test Summary.txt` when the user-facing seam chain is complete unless an explicit exception applies.

## Later-Phase Plan

- Workstream:
  - run the first source-map and seam-selection pass
  - implement only the approved smallest safe seam
  - validate before continuing
  - use single-seam fallback until same-risk continuation is explicitly proven safe
- Hardening:
  - pressure-test the selected shell-facing UX and authoring-entry behavior across normal and edge cases
  - repair only defects, validation gaps, or helper seams inside the approved scope
- Live Validation:
  - capture real desktop evidence for taskbar/tray/Create Custom Task behavior when implementation reaches that point
  - digest evidence into this authority record before phase advancement
- PR Readiness:
  - complete merge-target canon, Governance Drift Audit, next-workstream selection, post-merge truth, and dirty-branch gates before PR green
- Release Readiness:
  - if FB-038 becomes a user-facing implementation milestone, handle release packaging only after merge according to the release-debt model

## Branch Readiness Progress

- promoted FB-038 from `Registry-only` to `Promoted`
- created this canonical workstream record
- recorded Branch Readiness phase authority, scope, non-goals, reuse baseline, validation contract, User Test Summary strategy, and later-phase plan
- preserved FB-037 released truth and cleared release-debt posture
- validated Branch Readiness with `python dev/orin_branch_governance_validation.py`
- validated whitespace with `git diff --check`
- committed Branch Readiness admission in `766ff67`
- transitioned phase authority from `Branch Readiness` to `Workstream`
- no product/runtime implementation was started during the transition

## Workstream Progress

- Workstream is open for source-map and seam selection.
- No implementation seam has been selected yet.
- No product/runtime implementation has started.

## User Test Summary

No user-facing behavior changed in Branch Readiness.

Manual validation becomes relevant only after a Workstream seam changes taskbar, tray, Create Custom Task, or related visible desktop behavior.
