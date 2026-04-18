# FB-041 Deterministic Callable-Group Execution Layer

## ID And Title

- ID: `FB-041`
- Title: `Deterministic callable-group execution layer`

## Record State

- `Promoted`

## Status

- `Completed on branch (pending merge)`

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

- Phase: `Completed`
- Substate: `Exact-branch closeout evidence captured; ready for merge-facing closeout flow`

## Phase Entry Basis

- merged `main` included the governance-hardening merge from PR `#56`
- merged `main` included `FB-041` in backlog as the selected successor lane
- merged `main` included the promoted canonical workstream record before implementation started
- the implementation branch was recreated from updated `main` so no stale pre-promotion execution state was reused
- product work in this lane then stayed bounded to deterministic callable-group execution plus the two explicitly documented UI clarification exceptions

## Phase Exit Criteria

- deterministic callable-group execution is implemented and bounded to stored-order, stop-on-failure follow-through
- dispatch routing, execution intent binding, failure-path parity, and failure payload normalization are complete
- the confirm-surface clarification exception and the result status-text clarification exception are both complete without widening into broader UI redesign
- repo-side validation is green on the exact branch truth
- interactive launched-process success and failure validation is green on the exact branch truth
- live confirm and result surface audit evidence is captured on the exact branch truth

## Current Branch Truth

- the current shared baseline remains the released FB-027 interaction floor plus the released FB-036 authoring-and-callable-group milestone
- exact group invocation still enters through the released chooser and confirm flow, but group follow-through now executes the full stored-order callable group after confirm
- deterministic callable-group execution now emits bounded runtime markers for:
  - group start
  - per-step start
  - per-step success or failure
  - terminal completion or failure
- dispatch now consumes immutable execution intent captured at confirm time rather than ambient overlay group state
- group failures now reuse the existing recoverable launch-failure classification pipeline with structured group-aware payloads
- single-action dispatch, confirm text, result text, and failure behavior remain unchanged except where the documented confirm/result group-only clarification exceptions apply

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

Exception:

- a single confirm-surface clarification seam is allowed to accurately reflect deterministic callable-group execution behavior
- this confirm-surface exception does not include result-surface changes or UI restructuring
- a single result status-text clarification seam is allowed to accurately reflect deterministic callable-group execution outcomes
- this result-surface exception is limited to status-text only and does not include result hint changes, timing changes, payload or model changes, or UI restructuring

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
- added deterministic callable-group execution with stored-order stepping, stop-on-failure, and terminal propagation
- routed the post-confirm dispatch handoff through the deterministic group-execution helper when a callable-group confirm context is active
- replaced ambient group-state dispatch decisions with immutable execution intent captured at confirm time and consumed exactly once
- aligned group failure handling with the existing single-action recoverable failure classification and reporting path
- completed structured failure payload normalization so single and group paths are schema-compatible downstream
- added the confirm-surface clarification seam so group confirm copy accurately states that Enter runs the full stored-order group while the selected member remains inspection context
- added the result status-text clarification seam so group success and fallback failure text accurately reflect callable-group outcomes
- added result-name sanity checks proving result text uses execution intent group truth rather than mutable overlay state
- added branch-local interactive launched-process validation and screenshot audit coverage for:
  - real group success
  - real group failure
  - unchanged single-action confirm and result surfaces

## Validation Evidence

- repo-side deterministic validator:
  - `python dev/orin_callable_group_execution_validation.py`
  - latest pass confirms:
    - stored-order execution
    - gap-free step indices
    - stop-on-failure
    - no-later-member execution after failure
    - execution intent single-use behavior
    - confirm/result copy assertions
    - overlay mutation protection for group result naming
- FB-036 regression guard:
  - `python dev/orin_saved_action_authoring_validation.py`
- recoverable-failure regression guard:
  - `python dev/orin_recoverable_launch_failed_validation.py`
  - latest report:
    - `dev/logs/recoverable_launch_failed_validation/reports/RecoverableLaunchFailedValidationReport_20260418_094518.txt`
- exact-branch interactive launched-process closeout proof:
  - `dev/orin_callable_group_execution_interactive_validation.ps1`
  - latest report:
    - `dev/logs/fb_041_callable_group_interactive_validation/20260418_094333/FB041CallableGroupInteractiveValidationReport_20260418_094333.txt`
  - latest manifest:
    - `dev/logs/fb_041_callable_group_interactive_validation/20260418_094333/manifest.json`
  - latest launched-process UI captures:
    - `dev/logs/fb_041_callable_group_interactive_validation/20260418_094333/group_success_confirm.png`
    - `dev/logs/fb_041_callable_group_interactive_validation/20260418_094333/group_success_result.png`
    - `dev/logs/fb_041_callable_group_interactive_validation/20260418_094333/group_failure_result.png`
    - `dev/logs/fb_041_callable_group_interactive_validation/20260418_094333/single_action_confirm.png`
    - `dev/logs/fb_041_callable_group_interactive_validation/20260418_094333/single_action_result.png`
- closeout-grade interactive proof now explicitly covers:
  - one real callable-group success pass
  - one real callable-group failure pass
  - live confirm copy audit
  - live result status-text audit
  - unchanged result hint audit
  - unchanged single-action confirm and result audit

## User Test Summary

- setup:
  - start the desktop runtime on the exact FB-041 branch truth
  - ensure the saved-actions source includes:
    - group `Workspace Tools`
    - group `Broken Workspace Tools`
    - single saved action `Open Notes Task`
- exact success invocation:
  - invoke `workspace tools`
  - when the chooser appears, select `Open Notes Task`
  - expected confirm text:
    - hint: `Review the selected member details below. Press Enter to run "Workspace Tools" group in stored order.`
    - footer: `Press Enter to run "Workspace Tools" group in stored order, or Esc to return.`
  - expected success result text:
    - `Group "Workspace Tools" executed in stored order.`
- exact failure invocation:
  - invoke `broken workspace tools`
  - when the chooser appears, select `Open Notes Task`
  - expected failure result text prefix:
    - `Group "Broken Workspace Tools" failed at step 1:`
- unchanged single-action control check:
  - invoke `notes task`
  - expected confirm text:
    - hint: `Review the resolved action origin and destination before execution.`
    - footer: `Press Enter to confirm or Esc to return.`
  - expected success result text:
    - `Launch request sent.`
- what must remain unchanged:
  - result hint text stays `Returning to passive desktop mode.`
  - no new panels, rows, or workflow steps appear
  - single-action behavior stays on the original non-group path
  - the selected group member remains inspection context only; execution still follows the full stored-order group
