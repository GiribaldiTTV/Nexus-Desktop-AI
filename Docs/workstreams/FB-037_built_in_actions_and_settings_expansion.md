# FB-037 Curated Built-In System Actions And Nexus Settings Expansion

## ID And Title

- ID: `FB-037`
- Title: `Curated built-in system actions and Nexus settings expansion`

## Record State

- `Promoted`

## Status

- `Branch Readiness`

## Release Stage

- `pre-Beta`

## Target Version

- `TBD`

## Canonical Branch

- `feature/fb-037-built-in-actions-and-settings-expansion`

## Purpose / Why It Matters

Promote the curated built-in system actions and Nexus settings expansion lane above the released shared action, saved-action authoring, callable-group authoring, and deterministic callable-group execution baseline.

This workstream exists so common Windows, vendor utility, and Nexus-owned destinations can become deliberate first-class built-in actions under the shared action model instead of being left to ad hoc saved-action customization.

## Current Phase

- Phase: `Branch Readiness`

## Phase Status

- `Active Branch`
- Branch Readiness admission is open on `feature/fb-037-built-in-actions-and-settings-expansion`
- no implementation seam has been selected yet
- no product or runtime code changes are authorized in Branch Readiness

## Branch Class

- `implementation`

## Blockers

- no active blockers

## Entry Basis

- updated `main` is aligned with `origin/main`
- FB-041 is released in `v1.3.1-prebeta` and no longer blocks next-lane admission
- no active promoted workstream exists before this admission
- FB-037 was `Registry-only` on merged canon before this Branch Readiness pass
- this branch was created fresh from updated `main`

## Exit Criteria

- backlog, roadmap, workstreams index, and this workstream doc agree that FB-037 is promoted and in `Branch Readiness`
- bounded objective and explicit non-goals are recorded before implementation begins
- reuse baseline and validation contract are recorded
- no product or runtime implementation has started during Branch Readiness
- no unresolved blocker prevents transition to `Workstream`

## Rollback Target

- `Branch Readiness`

## Next Legal Phase

- `Workstream`

## Bounded Objective

Define and later implement a curated set of built-in actions for standard Windows, vendor utility, and Nexus-owned surfaces that belong in the product catalog rather than user-authored saved actions.

The first Workstream-phase slice must begin by inventorying candidate built-ins, locating the shared action catalog boundaries, and choosing the smallest safe built-in action expansion seam before product code changes.

## Explicit Non-Goals

- no implementation during Branch Readiness
- no product or runtime code changes during Branch Readiness
- no saved-action authoring redesign
- no callable-group execution changes
- no scheduling, branching, retries, nested groups, or parallelism
- no taskbar, tray, plugin, external trigger, monitoring, thermal, or performance HUD work
- no Action Studio behavior
- no voice invocation changes
- no broad UI redesign
- no implicit promotion of FB-038, FB-039, or FB-040

## Reuse Baseline

- `Docs/closeouts/nexus_prebeta_rebaseline_through_v1.3.1-prebeta.md`
- `Docs/workstreams/FB-041_deterministic_callable_group_execution_layer.md`
- `Docs/workstreams/FB-036_saved_action_authoring.md`
- `Docs/workstreams/FB-027_interaction_system_baseline.md`
- `desktop/shared_action_model.py`
- `desktop/interaction_overlay_model.py`

## Validation Contract

Branch Readiness validation is docs/governance-only and must prove:

- FB-037 is promoted exactly once
- FB-037 has a canonical workstream doc
- the active phase block uses the canonical phase enum
- the branch class is `implementation`
- FB-041 released truth remains unchanged
- no product or runtime code changed
- governance validation passes

Future Workstream-phase validation must be defined before implementation begins and must preserve:

- shared action model compatibility
- built-in versus saved action source distinction
- exact-match resolution expectations
- saved-action and callable-group regression behavior
- failure classification and result-surface boundaries from the released baseline

## Branch Readiness Progress

- created fresh branch `feature/fb-037-built-in-actions-and-settings-expansion` from updated `main`
- promoted FB-037 from `Registry-only` to `Promoted`
- created this canonical workstream record
- recorded Branch Readiness phase authority, scope, non-goals, reuse baseline, and validation contract

## User Test Summary

No manual user test is required for this Branch Readiness pass because no product, runtime, UI, or user-visible behavior changed.
