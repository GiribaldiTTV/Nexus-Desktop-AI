# FB-041 Deterministic Callable-Group Execution Layer

## ID And Title

- ID: `FB-041`
- Title: `Deterministic callable-group execution layer`

## Record State

- `Promoted`

## Status

- `Promoted for pre-implementation setup`

## Release Stage

- `pre-Beta`

## Target Version

- `TBD`

## Canonical Branch

- `feature/fb-041-deterministic-callable-group-execution`

## Purpose / Why It Matters

Promote the first bounded callable-group follow-through execution layer above the released FB-036 authoring baseline.

This workstream exists so callable groups can move from exact invocation only into deterministic runtime follow-through without reopening FB-036 authoring foundations, widening into automation design, or overlapping the separate future lanes already tracked in FB-037 through FB-040.

## Current Phase

- Phase: `Approved Execution`
- Substate: `Execution boundary approved, reserved branch revalidated against updated main, first product slice not started`

## Phase Entry Basis

- merged `main` now includes the governance-hardening merge from PR `#56`
- merged `main` now includes `FB-041` in backlog as the selected successor lane
- the reserved branch `feature/fb-041-deterministic-callable-group-execution` has been realigned to updated `main`
- no implementation commits exist on the reserved branch beyond updated `main`
- the lane is ready for a bounded implementation startup pass, but product code has not been changed yet

## Phase Exit Criteria

- the execution-dispatch seam after chooser or confirm resolution is located precisely in code before patching
- the smallest safe first slice is approved against this workstream scope
- the first bounded execution slice is completed and verified without widening into deferred non-goals

## Current Branch Truth

- the current shared baseline remains the released FB-027 interaction floor plus the released FB-036 authoring-and-callable-group milestone
- exact group invocation already exists, but callable-group follow-through execution remains deferred on the released baseline
- the reserved branch now matches updated merged `main` after the governance-hardening merge and remains the correct future execution base for this lane

## Scope

- deterministic linear execution only
- stored-order stepping only
- stop on first failure
- terminal success or failure propagation
- runtime markers for group start, per-step progression, and terminal completion or failure

## Explicit Non-Goals

- no UI changes
- no scheduling
- no branching
- no nested groups
- no parallel execution
- no retries
- no plugin or external trigger work
- no built-in catalog expansion

## Reuse Baseline

- `Docs/workstreams/FB-036_saved_action_authoring.md`
- `Docs/workstreams/FB-027_interaction_system_baseline.md`
- `Docs/closeouts/nexus_prebeta_rebaseline_through_v1.3.0-prebeta.md`
- `desktop/interaction_overlay_model.py`
- `desktop/shared_action_model.py`

## First Execution Boundary

- the active implementation seam starts at the execution dispatch layer after chooser or confirm resolution
- this lane does not start in UI, authoring, or group-definition storage
- the exact dispatch function must be located before any product-code patching begins

## Validation Contract

- prefer repo-side deterministic proof first
- required assertions:
  - member execution order matches persisted stored order exactly
  - step indices are monotonic and gap-free
  - execution halts on first failure
  - later members do not execute after failure
  - aggregate success or failure matches the executed steps
- required runtime markers:
  - group execution start
  - per-step start
  - per-step success or failure
  - group completion or failure
- no timeout inflation
- no validation-rule drift

## Executed Slices

- promoted the backlog identity into an active canonical workstream
- created the stable canonical workstream record
- revalidated the reserved branch against updated `main`
- confirmed the lane remains pre-implementation only

## User Test Summary

No meaningful manual test exists yet because implementation has not started in this workstream.
